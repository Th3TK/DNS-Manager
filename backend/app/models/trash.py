from datetime import datetime
from uuid import UUID

from app.database.models.dns_trash import DNSTrashInDB
from app.database.models.enums import DNSObjectType
from app.models.record import RestoreDNSRecordArgs
from app.models.zone import RestoreDNSZoneArgs
from pydantic import BaseModel, ConfigDict


class TrashEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entry_uuid: UUID
    deletion_timestamp: datetime
    actor: str
    object_type: DNSObjectType
    object_data: RestoreDNSZoneArgs | RestoreDNSRecordArgs

    @classmethod
    def from_db(cls, trash_entry_db: DNSTrashInDB) -> "TrashEntry":
        form_model = RestoreDNSRecordArgs if trash_entry_db.object_type == DNSObjectType.RECORD else RestoreDNSZoneArgs

        result = cls.model_validate(trash_entry_db)
        result.object_data = form_model.model_validate(trash_entry_db.object_data)

        return result
