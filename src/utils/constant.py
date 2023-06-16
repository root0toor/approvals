# TODO: Rename this file to enums

from dataclasses import dataclass
from enum import Enum


class USER_TYPE:
    HIVER = "HIVER"
    SM_USER = "SM_USER"
    COLLABORATOR = "COLLABORATOR"


class REASON:
    DUPLICATE = "Duplicate"
    INACCURATE = "Inaccurate"
    OTHER = "Other"


class APPROVAL_STATES:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    IDLE = "IDLE"
    INITIATED = "INITIATED"


@dataclass(frozen=True)
class ApprovalStateValue:
    APPROVED: int
    CANCELLED: int
    REJECTED: int
    PENDING: int
    

class SM_ADMIN_PERMISSION:
    SM_PARTIAL = "sm.partial"
    SM_FULL = "sm.full"


class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogChannel:
    STDOUT = "STDOUT"
    FILE = "FILE"
    LOGSTASH = "LOGSTASH"


class TIER:
    LOCAL = "local"
    PRODUCTION = "production"


class PARAMS:
    USERS_PARAMS = "user_ids[]"
    USER_GROUP_PARAM = "usergroupid"
    COLLABORATOR_PARAMS = "collaboratorIds"


class SEPERATORS:
    DOUBLE_COLON = "::"
    COMMA = ","


class ProducerTopic:
    EMAIL_TRIGGER = "approval_email_triggers"
    STATUS_CHANGE = "label_updates"


class ConsumerTopic:
    APPROVAL_TOGGLE = "approval_toggle"
    SHARED_MAILBOX_USER_REMOVED = "usergroup.sharedmailbox.state"
    SHARED_MAILBOX_STATE = "sharedmailbox.state"
    USER_GROUP_USER_STATE = "usergroup.user.state"

class ConsumerEventTypes:
    SHARED_MAILBOX_REMOVAL = "sharedMailboxRemoved"
    USER_GROUP_REMOVAL = "usergroupSoftDeleted"


class ApprovalToggleTask:
    LABELS = "labels"
    VIEWS = "views"
    AUTO_FAVOURITE = "auto_favourite"


class NotificationActionType:
    NEW = "new"


class EventType:
    USER_REMOVED_FROM_SHAREDMAILBOX = "userRemovedFromSharedmailbox"
    USER_ADDED_INTO_SHAREDMAILBOX = "userAddedIntoSharedmailbox"


class AutoOffsetReset(Enum):
    EARLIEST = "earliest"
    LATEST = "latest"
