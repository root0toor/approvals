from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Table,
    BigInteger,
    ForeignKey,
    Index, UniqueConstraint
)
from ..models import Base


class ApprovalRequestBaseColumn(Enum):
    ID = "id"
    SMID = "smId"
    APPROVAL_FLOW_ID = "approvalFlowId"
    CONVERSATION_ID = "conversationId"
    STATUS = "status"
    CURRENT_STEP_ID = "currentStepId"
    PERMALINK = "permalink"
    CREATED_BY = "createdBy"
    CREATED_AT = "createdAt"


ApprovalRequest = Table(
    "ApprovalRequest",
    Base.metadata,
    Column(
        ApprovalRequestBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
    ),
    Column(
        ApprovalRequestBaseColumn.SMID.value,
        BigInteger,
        index=True,
        nullable=False
    ),
    Column(
        ApprovalRequestBaseColumn.APPROVAL_FLOW_ID.value,
        BigInteger,
        ForeignKey("ApprovalFlow.id", ondelete="CASCADE"),
    ),
    Column(
        ApprovalRequestBaseColumn.CONVERSATION_ID.value,
        BigInteger,
        nullable=False,
        index=True
    ),
    Column(
        ApprovalRequestBaseColumn.STATUS.value,
        String(length=20),
        default="PENDING",
        nullable=False,
    ),
    Column(
        ApprovalRequestBaseColumn.CURRENT_STEP_ID.value,
        BigInteger,
        ForeignKey("ApprovalStep.id", ondelete="SET NULL"),
        nullable=True,
    ),
    Column(
        ApprovalRequestBaseColumn.PERMALINK.value,
        String(length=200),
    ),
    Column(
        ApprovalRequestBaseColumn.CREATED_BY.value,
        BigInteger,
        nullable=False,
    ),
    Column(
        ApprovalRequestBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    UniqueConstraint(
        ApprovalRequestBaseColumn.APPROVAL_FLOW_ID.value,
        ApprovalRequestBaseColumn.SMID.value,
        ApprovalRequestBaseColumn.CONVERSATION_ID.value,
        name="approvalFlow_conversation_sm_constraint",
    )
)
