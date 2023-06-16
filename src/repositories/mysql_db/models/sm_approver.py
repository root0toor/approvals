from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    DateTime,
    Table,
    ForeignKey,
    Boolean,
    BigInteger,
    UniqueConstraint,
    Index,
    String
)
from ..models import Base


class SmApproverBaseColumn(Enum):
    ID = "id"
    APPROVER_ID = "approverId"
    SMID = "smId"
    APPROVER_EXTERNAL_ID = "approverExternalId"
    APPROVER_TYPE = "approverType"
    ACTIVE = "active"
    CREATED_AT = "createdAt"


SmApprover = Table(
    "SmApprover",
    Base.metadata,
    Column(
        SmApproverBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
    ),
    Column(
        SmApproverBaseColumn.APPROVER_ID.value,
        BigInteger,
        ForeignKey("Approver.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(SmApproverBaseColumn.SMID.value, BigInteger, nullable=False),
    # TODO: Make APPROVER_EXTERNAL_ID and APPROVER_TYPE non-nullable after M3.1 is done
    Column(SmApproverBaseColumn.APPROVER_EXTERNAL_ID.value, BigInteger, nullable=True),
    Column(SmApproverBaseColumn.APPROVER_TYPE.value, String(length=15), nullable=True),
    Column(SmApproverBaseColumn.ACTIVE.value, Boolean, default=True),
    Column(
        SmApproverBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    UniqueConstraint(
        SmApproverBaseColumn.APPROVER_ID.value,
        SmApproverBaseColumn.SMID.value,
        name="approverId_smid_constraint",
    ),
    Index("sm_approver_external_id_idx",SmApproverBaseColumn.APPROVER_EXTERNAL_ID.value,SmApproverBaseColumn.APPROVER_ID.value,SmApproverBaseColumn.SMID.value)
)
