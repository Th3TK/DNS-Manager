import asyncio
import logging

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


async def resolve_record_type(
    resolver: dns.asyncresolver.Resolver,
    target: str,
    record_type: str,
) -> list[str]:
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


async def check_record_resolution(
    resolver: dns.asyncresolver.Resolver,
    hostname: str,
    record_type: str,
    expected_content: str | list[str],
) -> ResolutionStatus:
    values = await resolve_record_type(resolver, hostname, record_type)

    actual_values = {value.rstrip(".") for value in values}

    if isinstance(expected_content, str):
        expected_values = {expected_content.rstrip(".")}
    else:
        expected_values = {content.rstrip(".") for content in expected_content}

    if not actual_values:
        return "NO_RESOLUTION"

    if expected_values == actual_values:
        return "OK"

    return "MISMATCH"


async def resolve_cname_targets(
    resolver: dns.asyncresolver.Resolver,
    targets: list[str],
) -> list[str]:
    results = await asyncio.gather(
        *(resolve_record_type(resolver, target, record_type) for target in targets for record_type in ("A", "AAAA"))
    )

    return [address for result in results for address in result]


async def ping_batch(batch: list[str]) -> dict[str, bool]:

    async with reachability_semaphore:
        try:
            hosts = await async_multiping(batch, count=1, timeout=CHECKS_TIMEOUT_SECONDS)
        except Exception:
            raise

    results = {address: host.is_alive for address, host in zip(batch, hosts)}

    return results


async def check_reachability(addresses: list[str]) -> dict[str, bool]:
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

    return {address: is_alive for result in results for address, is_alive in result.items()}
