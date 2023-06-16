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


class StepApproverBaseColumn(Enum):
    ID = "id"
    APPROVAL_STEP_ID = "approvalStepId"
    SM_APPROVER_ID = "smApproverId"
    CREATED_BY = "createdBy"
    CREATED_AT = "createdAt"


StepApprover = Table(
    "StepApprover",
    Base.metadata,
    Column(
        StepApproverBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
    ),
    Column(
        StepApproverBaseColumn.APPROVAL_STEP_ID.value,
        BigInteger,
        ForeignKey("ApprovalStep.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        StepApproverBaseColumn.SM_APPROVER_ID.value,
        BigInteger,
        ForeignKey("SmApprover.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        StepApproverBaseColumn.CREATED_BY.value,
        BigInteger,
        nullable=False,
    ),
    Column(
        StepApproverBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
)
