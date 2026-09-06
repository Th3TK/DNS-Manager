from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.management.dns.name_search import record_name_search
from app.management.users.authentication import get_authenticated_user
from app.models.record import DNSRecordSearchResult
from app.models.user import User

router = APIRouter(
    tags=["Record Name Search"],
)


@router.get(
    "/name-search",
    response_model=list[DNSRecordSearchResult],
    description="""
        Accepts a hostname or full FQDN and supports * and ? wildcards. 
        If the query matches an existing zone suffix, it is treated as an FQDN and searched directly.
        Otherwise, it is treated as a hostname and searched across all existing zones.
        Results include both active and trashed records.
    """,
)
def __search_matching_record_names__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], query: str
) -> list[DNSRecordSearchResult]:
    return record_name_search(db, query)
