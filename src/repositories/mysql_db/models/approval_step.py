from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    DateTime,
    Table,
    ForeignKey,
    BigInteger,
    Index
)
from ..models import Base


class ApprovalStepBaseColumn(Enum):
    ID = "id"
    APPROVAL_FLOW_ID = "approvalFlowId"
    NEXT_STEP_ID = "nextStepId"
    CREATED_BY = "createdBy"
    CREATED_AT = "createdAt"


ApprovalStep = Table(
    "ApprovalStep",
    Base.metadata,
    Column(
        ApprovalStepBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
    ),
    Column(
        ApprovalStepBaseColumn.APPROVAL_FLOW_ID.value,
        BigInteger,
        ForeignKey("ApprovalFlow.id", ondelete="CASCADE"),
    ),
    Column(ApprovalStepBaseColumn.NEXT_STEP_ID.value, BigInteger, nullable=True),
    Column(
        ApprovalStepBaseColumn.CREATED_BY.value,
        BigInteger,
        nullable=False,
    ),
    Column(
        ApprovalStepBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
)
