from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Table,
    Boolean,
    BigInteger,
    UniqueConstraint,
    Index
)
from ..models import Base


class ApprovalFlowBaseColumn(Enum):
    ID = "id"
    NAME = "name"
    SMID = "smId"
    USERGROUPID = "usergroupId"
    INITIAL_STEP_ID = "initialStepId"
    IS_ACTIVE = "isActive"
    CREATED_BY = "createdBy"
    CREATED_AT = "createdAt"


ApprovalFlow = Table(
    "ApprovalFlow",
    Base.metadata,
    Column(
        ApprovalFlowBaseColumn.ID.value,
        BigInteger,
        primary_key=True,
        autoincrement=True,
    ),
    Column(ApprovalFlowBaseColumn.NAME.value, String(length=100), nullable=False),
    Column(ApprovalFlowBaseColumn.SMID.value, BigInteger, nullable=False),
    Column(ApprovalFlowBaseColumn.USERGROUPID.value, BigInteger, nullable=False),
    Column(ApprovalFlowBaseColumn.INITIAL_STEP_ID.value, BigInteger, nullable=True),
    Column(ApprovalFlowBaseColumn.IS_ACTIVE.value, Boolean, default=True),
    Column(
        ApprovalFlowBaseColumn.CREATED_BY.value,
        BigInteger,
        nullable=False,
    ),
    Column(
        ApprovalFlowBaseColumn.CREATED_AT.value,
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    UniqueConstraint(
        ApprovalFlowBaseColumn.SMID.value,
        ApprovalFlowBaseColumn.NAME.value,
        name="approvalFlow_smId_name_constraint",
    )
)
