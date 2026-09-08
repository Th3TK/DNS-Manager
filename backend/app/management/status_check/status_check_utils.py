import asyncio
import logging
from datetime import datetime

import dns.asyncresolver
import dns.exception
import dns.resolver
from app.models.record import ResolutionStatus
from icmplib import async_multiping

CHECKS_TIMEOUT_SECONDS = 2

RESOLUTION_CONCURRENCY = 100
REACHABILITY_CONCURRENCY = 10
REACHABILITY_BATCH_SIZE = 100


resolution_semaphore = asyncio.Semaphore(RESOLUTION_CONCURRENCY)
reachability_semaphore = asyncio.Semaphore(REACHABILITY_CONCURRENCY)

logger = logging.getLogger(__name__)


async def check_record_resolution(
    resolver: dns.asyncresolver.Resolver,
    hostname: str,
    record_type: str,
    expected_content: str | list[str],
) -> ResolutionStatus:
    """ """

    async with resolution_semaphore:
        try:
            answer = await resolver.resolve(
                hostname,
                record_type,
                lifetime=CHECKS_TIMEOUT_SECONDS,
            )
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
        ):
            return "NO_RESOLUTION"

    actual_values = {str(record).rstrip(".") for record in answer}

    if isinstance(expected_content, str):
        expected_values = {expected_content.rstrip(".")}
    else:
        expected_values = {content.rstrip(".") for content in expected_content}

    if expected_values == actual_values:
        return "OK"

    return "MISMATCH"


async def get_record_resolution_with_timestamp(
    resolver: dns.asyncresolver.Resolver,
    hostname: str,
    record_type: str,
    expected_content: str | list[str],
) -> tuple[ResolutionStatus, datetime]:
    return (await check_record_resolution(resolver, hostname, record_type, expected_content), datetime.now())


async def resolve_cname_targets(resolver: dns.asyncresolver.Resolver, target: str | list[str]) -> list[str]:
    targets = [target] if isinstance(target, str) else target

    async def resolve_target(target: str) -> list[str]:
        async def resolve_type(record_type: str) -> list[str]:
            async with resolution_semaphore:
                try:
                    answer = await resolver.resolve(
                        target,
                        record_type,
                        lifetime=CHECKS_TIMEOUT_SECONDS,
                    )
                except (
                    dns.resolver.NXDOMAIN,
                    dns.resolver.NoAnswer,
                    dns.resolver.NoNameservers,
                    dns.exception.Timeout,
                ):
                    return []

            return [str(record) for record in answer]

        results = await asyncio.gather(
            resolve_type("A"),
            resolve_type("AAAA"),
        )

        return [address for result in results for address in result]

    results = await asyncio.gather(*(resolve_target(target) for target in targets))

    return [address for result in results for address in result]


async def ping_batch(batch: list[str]) -> dict[str, tuple[bool, datetime]]:

    async with reachability_semaphore:
        try:
            hosts = await async_multiping(batch, count=1, timeout=CHECKS_TIMEOUT_SECONDS)
        except Exception:
            raise

    results = {address: (host.is_alive, datetime.now()) for address, host in zip(batch, hosts)}

    return results


async def check_reachability(addresses: list[str]) -> dict[str, tuple[bool, datetime]]:
    if not addresses:
        return {}

    batches = [
        addresses[index : index + REACHABILITY_BATCH_SIZE]
        for index in range(
            0,
            len(addresses),
            REACHABILITY_BATCH_SIZE,
        )
    ]

    results = await asyncio.gather(*(ping_batch(batch) for batch in batches))

    return {address: (is_alive, timestamp) for result in results for address, (is_alive, timestamp) in result.items()}
