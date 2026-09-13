import asyncio
import ipaddress
import logging
import socket
from asyncio import Task
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from app.config import ENV_CONFIG
from app.database.connection import session_factory
from app.management.dns.record import get_all_records
from app.management.status_check.status_check_utils import (
    check_reachability,
    check_record_resolution,
    resolve_cname_targets,
)
from app.management.status_check.websocket_manager import status_check_websocket_manager
from app.models.exceptions import DNSProviderException
from app.models.record import DNSRecord, RecordStatus, RecordStatusCheckData, RecordStatuses
from dns.asyncresolver import Resolver
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

CHECKS_TIMEOUT_SECONDS = 2


class AutomaticRecordStatusCheck:
    def __init__(self):
        self._data: RecordStatusCheckData | None = None  # Cached data
        self._task: Task[None] | None = None
        self._resolver: Resolver | None = None

    async def start(self) -> None:
        """
        Starts the status check task loop.
        """

        if self._task is not None and not self._task.done():
            logger.debug("Automatic record status check is already running.")
            return

        logger.debug("Starting automatic record status check.")
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """
        Stops the status check task loop.
        """

        if self._task is None:
            return

        logger.debug("Stopping automatic record status check.")

        task = self._task
        self._task = None

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

    def get_data(self) -> RecordStatusCheckData | None:
        return self._data

    def _create_resolver(self) -> Resolver:
        """
        Creates and configures a DNS resolver using the DNS_RESOLVER configuration.
        Resolves the nameserver hostname to an IPv4 address when necessary.
        """

        value = ENV_CONFIG.DNS_RESOLVER

        try:
            parsed = urlsplit(f"//{value}")
            hostname = parsed.hostname
            port = parsed.port

        except ValueError as exc:
            raise ValueError(f"Invalid DNS_RESOLVER configuration: {value!r}") from exc

        if not hostname:
            raise ValueError(f"Invalid DNS_RESOLVER configuration: {value!r}: missing nameserver address.")

        port = port or 53

        if not 1 <= port <= 65535:
            raise ValueError(f"Invalid DNS_RESOLVER configuration: {value!r}: port must be between 1 and 65535.")

        try:
            ipaddress.ip_address(hostname)
            nameserver_ip = hostname
        except ValueError:
            # if not an IP address, try to resolve the provided hostname
            try:
                nameserver_ip = socket.gethostbyname(hostname)
                logger.info(f"Resolved DNS_RESOLVER hostname: {nameserver_ip}")
            except socket.gaierror as exc:
                raise ValueError(f"Could not resolve DNS_RESOLVER hostname: {hostname!r}") from exc

        resolver = Resolver(configure=False)
        resolver.nameservers = [nameserver_ip]
        resolver.port = port

        logger.info(f"Configured DNS resolver: {nameserver_ip}:{port}")

        return resolver

    async def _run(self) -> None:
        """
        Status check loop
        """

        while True:
            try:
                if self._resolver is None:
                    # try creating the resolver, raises errors on fail
                    self._resolver = self._create_resolver()

                logger.debug("Running automatic record status check.")

                statuses = await self._check_records()

                logger.debug("Successfully retrieved record statuses.")

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                statuses = None

                if isinstance(exc, ValueError):
                    logger.error("Automatic record status check failed - %s", str(exc))
                elif isinstance(exc, socket.gaierror):
                    logger.error("Automatic record status check failed - could not reach the DNS resolver.")
                elif isinstance(exc, DNSProviderException):
                    logger.error("Automatic record status check failed - could not reach the DNS provider.")
                elif isinstance(exc, OperationalError):
                    logger.error("Automatic record status check failed - could not reach the database.")
                elif isinstance(exc, ProgrammingError):
                    logger.error("Automatic record status check failed - database migrations have not been applied.")
                else:
                    logger.exception("Automatic record status check failed.")

            # Update cached data
            self._data = RecordStatusCheckData(
                statuses=statuses,
                timestamp=datetime.now(timezone.utc),
                next_check=datetime.now(timezone.utc) + timedelta(seconds=ENV_CONFIG.CHECK_INTERVAL_SECONDS),
            )

            # Broadcasts data to all connected websockets
            await status_check_websocket_manager.broadcast(jsonable_encoder(self._data))

            logger.debug(f"Next record status update in {ENV_CONFIG.CHECK_INTERVAL_SECONDS} seconds ({self._data.next_check}).")

            await asyncio.sleep(ENV_CONFIG.CHECK_INTERVAL_SECONDS)

    async def _check_records(self) -> RecordStatuses | None:
        """
        Checks all records on their resolution and reachability and returns a dictionary:

        `dict[ZONE_NAME, dict[RECORD_NAME, dict[RECORD_TYPE, RecordStatus | None]]]`
        """

        if self._resolver is None:
            return None

        with session_factory() as db:
            all_records = get_all_records(db)

        check_data: RecordStatuses = {}
        records_to_check: list[DNSRecord] = []

        for record in all_records:
            # initialize check_data
            check_data.setdefault(record.zone_name, {}).setdefault(record.name, {})[record.type] = None

            # skip all the external records
            if record.origin != "external" and record.checks_enabled:
                records_to_check.append(record)

        # resolve internal dns records
        resolutions = await asyncio.gather(
            *(
                check_record_resolution(
                    resolver=self._resolver,
                    hostname=record.name,
                    record_type=record.type,
                    expected_content=record.content,
                )
                for record in records_to_check
            )
        )

        # reachability is only checked for A, AAAA, CNAME records that returned OK in their resolution check.
        records_to_check_reachability: list[DNSRecord] = []

        for record, resolution in zip(records_to_check, resolutions):
            reachability = None

            if resolution == "OK":
                if record.type in {"A", "AAAA", "CNAME"}:
                    records_to_check_reachability.append(record)
                else:
                    reachability = "NOT_CHECKED"

            check_data[record.zone_name][record.name][record.type] = RecordStatus(
                resolution=resolution,
                reachability=reachability,
            )

        # a map of record memory addresses and lists of addresses/targets
        record_addresses: dict[int, list[str]] = {}
        # set of all addresses that need to be pinged
        unique_addresses: set[str] = set()

        # retrieve addresses that need to be pinged and put them in a set
        # so no address will be pinged multiple times
        for record in records_to_check_reachability:
            addresses = None

            match record.type:
                case "A" | "AAAA":
                    addresses = [record.content] if isinstance(record.content, str) else record.content
                case "CNAME":
                    targets = [record.content] if isinstance(record.content, str) else record.content
                    addresses = await resolve_cname_targets(resolver=self._resolver, targets=targets)

            if addresses is not None:
                # add the addresses to the set
                unique_addresses.update(addresses)
                # map the addresses to the memory address of the record
                record_addresses[id(record)] = addresses

        addresses = list(unique_addresses)

        # ping all addresses
        address_reachability = await check_reachability(list(unique_addresses))

        # apply results to records
        for record in records_to_check_reachability:
            # if any address belonging to the record is reachable, then the record is reachable
            reachable = any(address_reachability[address] for address in record_addresses[id(record)])

            # assign record reachability status:

            record_status = check_data[record.zone_name][record.name][record.type]

            assert record_status is not None

            record_status.reachability = "REACHABLE" if reachable else "UNREACHABLE"

        return check_data


automatic_status_check = AutomaticRecordStatusCheck()

__all__ = ["automatic_status_check"]
