from enum import StrEnum


class InternalRecordOrigin(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic => traefik"


class RecordOrigin(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic => traefik"
    EXTERNAL = "external"


class ActorType(StrEnum):
    USER = "user"
    WATCHER = "watcher"


class ChangeAction(StrEnum):
    CREATED = "created"
    CHANGED = "changed"
    DELETED = "deleted"
    RESTORED = "restored"
    PERMANENTLY_DELETED = "permanently_deleted"


class DNSObjectType(StrEnum):
    ZONE = "zone"
    RECORD = "record"
