from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, Table, String, BigInteger, UniqueConstraint,Index
from ..models import Base


class ApproverBaseColumn(Enum):
    ID = "id"
    EMAIL = "email"
    APPROVER_EXTERNAL_ID = "approverExternalId"
    APPROVER_TYPE = "approverType"
    CREATED_AT = "createdAt"

# TODO: This table is unnecessary. Should be deprecated
Approver = Table(
    "Approver",
    Base.metadata,
    Column(
        ApproverBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
    ),
    Column(
        ApproverBaseColumn.EMAIL.value, String(length=30), unique=True, nullable=True
    ),
    Column(
        ApproverBaseColumn.APPROVER_EXTERNAL_ID.value,
        BigInteger,
        nullable=True,
    ),
    # TODO: Deprecate this column after M3.1
    Column(ApproverBaseColumn.APPROVER_TYPE.value, String(length=15), nullable=False),
    Column(
        ApproverBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    UniqueConstraint(
        ApproverBaseColumn.APPROVER_EXTERNAL_ID.value,
        ApproverBaseColumn.APPROVER_TYPE.value,
        name="approverExternalId_approverType_constraint",
    ),
)
