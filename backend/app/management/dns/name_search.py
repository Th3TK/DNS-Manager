from concurrent.futures import ThreadPoolExecutor
from typing import Sequence, cast

from app.database.models.dns_trash import DNSTrashInDB
from app.database.models.enums import DNSObjectType
from app.management.dns.record import expand_records_properties_with_metadata
from app.management.dns.validation import validate_search_query
from app.models.record import DNSRecord, DNSRecordProperties, DNSRecordSearchResult
from app.models.trash import TrashEntry
from app.models.zone import DNSZoneProperties
from app.providers.factory import provider
from sqlalchemy import select
from sqlalchemy.orm import Session


def wildcards_to_sql_like(pattern: str) -> str:
    return pattern.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").replace("*", "%").replace("?", "_")


def prepare_trash_entry_search_results(trash_entries: Sequence[DNSTrashInDB]) -> list[DNSRecordSearchResult]:
    """
    Converts sequence of database trash entries into a list of DNSRecordSearchResult.
    """

    results = []

    for entry in trash_entries:
        trash_entry = TrashEntry.from_db(entry)

        results.append(
            DNSRecordSearchResult(
                **cast(DNSRecord, trash_entry.object_data).model_dump(),
                location="trash",
                trash_entry_uuid=trash_entry.entry_uuid,
            )
        )

    return results


def prepare_search_results(active_records: list[DNSRecord], trash_entries: Sequence[DNSTrashInDB]) -> list[DNSRecordSearchResult]:
    """
    Converts active and trash entries into a list of results.
    """

    return [
        *[DNSRecordSearchResult(**record.model_dump(), location="active") for record in active_records],
        *prepare_trash_entry_search_results(trash_entries),
    ]


def fqdn_name_search_with_wildcards(db: Session, query: str) -> list[DNSRecordSearchResult]:
    """
    Returns pattern matches over full record name.

    Accepts wildcards:
        * - matches any sequence of characters
        ? - matches any single character
    """

    db_pattern = wildcards_to_sql_like(query)

    active_records_properties = provider.query_records(query.rstrip("."))
    active_records = expand_records_properties_with_metadata(db, active_records_properties)

    matching_trash_entries = db.scalars(
        select(DNSTrashInDB).where(
            DNSTrashInDB.object_type == DNSObjectType.RECORD,
            DNSTrashInDB.object_data["name"]
            .as_string()
            .like(
                db_pattern,
                escape="\\",
            ),
        )
    ).all()

    return prepare_search_results(active_records, matching_trash_entries)


def hostname_search(db: Session, hostname: str, zones: list[DNSZoneProperties]) -> list[DNSRecordSearchResult]:
    """
    Returns exact hostname matches in every zone
    """
    record_names: list[str] = []

    def get_zone_records(zone: DNSZoneProperties):
        record_name = f"{hostname.rstrip('.')}.{zone.name}"
        return record_name, provider.get_records_by_name(zone.name, record_name)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_zone_records, zones))

    active_records_properties: list[DNSRecordProperties] = []

    for record_name, records in results:
        record_names.append(record_name)

        if records:
            active_records_properties.extend(records)

    active_records = expand_records_properties_with_metadata(
        db,
        active_records_properties,
    )

    matching_trash_entries = db.scalars(
        select(DNSTrashInDB).where(
            DNSTrashInDB.object_type == DNSObjectType.RECORD,
            DNSTrashInDB.object_data["name"].as_string().in_(record_names),
        )
    ).all()

    return prepare_search_results(
        active_records,
        matching_trash_entries,
    )


def record_name_search(db: Session, query: str) -> list[DNSRecordSearchResult]:
    """
    Searches DNS records by name using `query`

    - If `query` includes wildcards (`*` or `?`), returns pattern matches over full record name.
    - If `query` ends with an existing zone name, returns exact name matches only.
    - Else, `query` is handled as a hostname. All hostname matches from every zone are returned.
    """

    validate_search_query(query)

    query = f"{query.rstrip('.')}."
    has_wildcards = "*" in query or "?" in query

    # wildcard search
    if has_wildcards:
        return fqdn_name_search_with_wildcards(db, query)

    zones = provider.get_zones(skip_record_count=True)
    is_query_in_existing_zone = any(query.endswith(zone.name) for zone in zones)

    # FQDN search
    if is_query_in_existing_zone:
        return fqdn_name_search_with_wildcards(db, query)

    # hostname search
    return hostname_search(db, query, zones)
