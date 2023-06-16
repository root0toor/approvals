from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, String, Table, BigInteger, ForeignKey,Index
from ..models import Base


class ApproverRequestHistoryBaseColumn(Enum):
    ID = "id"
    SM_APPROVER_ID = "smApproverId"
    APPROVAL_REQUEST_ID = "approvalRequestId"
    APPROVAL_FLOW_ID = "approvalFlowId"
    CONVERSATION_ID = "conversationId"
    STEP_ID = "stepId"
    STATUS = "status"
    REASON = "reason"
    NOTE = "note"
    CREATED_AT = "createdAt"
    CREATED_BY = "createdBy"

ApproverRequestHistory = Table(
    "ApproverRequestHistory",
    Base.metadata,
    Column(
        ApproverRequestHistoryBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.SM_APPROVER_ID.value,
        BigInteger,
        ForeignKey("SmApprover.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.APPROVAL_REQUEST_ID.value,
        BigInteger,
        ForeignKey("ApprovalRequest.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.APPROVAL_FLOW_ID.value,
        BigInteger,
        ForeignKey("ApprovalFlow.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.CONVERSATION_ID.value,
        BigInteger,
        nullable=False,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.STEP_ID.value,
        BigInteger,
        nullable=False,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.STATUS.value,
        String(length=20),
        nullable=False,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.REASON.value,
        String(length=15),
        nullable=True,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.NOTE.value,
        String(length=100),
        nullable=True,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.CREATED_BY.value,
        BigInteger,
        nullable=True,
    ),
    Column(
        ApproverRequestHistoryBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
)
