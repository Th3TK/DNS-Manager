import asyncio
import logging
import time

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


async def check_reachability(addresses: list[str]) -> dict[str, bool]:
    if not addresses:
        return {}

    async def ping_batch(
        batch_number: int,
        batch: list[str],
    ) -> dict[str, bool]:
        logger.debug("Starting reachability batch %d (%d addresses)", batch_number, len(batch))

        start = time.perf_counter()

        async with reachability_semaphore:
            semaphore_acquired = time.perf_counter()

            logger.debug("Reachability batch %d acquired semaphore after %.3fs", batch_number, semaphore_acquired - start)

            try:
                hosts = await async_multiping(batch, count=1, timeout=CHECKS_TIMEOUT_SECONDS)
            except Exception:
                logger.exception("Reachability batch %d failed after %.3fs", batch_number, time.perf_counter() - start)
                raise

        duration = time.perf_counter() - start

        results = {address: host.is_alive for address, host in zip(batch, hosts)}

        logger.debug("Finished reachability batch %d in %.3fs", batch_number, duration)

        return results

    batches = [
        addresses[index : index + REACHABILITY_BATCH_SIZE]
        for index in range(
            0,
            len(addresses),
            REACHABILITY_BATCH_SIZE,
        )
    ]

    logger.debug("Starting reachability check: %d addresses in %d batches", len(addresses), len(batches))

    overall_start = time.perf_counter()

    results = await asyncio.gather(*(ping_batch(batch_number, batch) for batch_number, batch in enumerate(batches, start=1)))

    logger.debug("Finished all reachability batches in %.3fs", time.perf_counter() - overall_start)

    return {address: is_alive for result in results for address, is_alive in result.items()}
