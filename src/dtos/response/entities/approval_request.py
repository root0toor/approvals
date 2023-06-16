from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ApprovalRequestDetailResponse(BaseModel):
    approvalRequestId: int
    smId: int
    approvalFlowId: int
    conversationId: int
    status: str
    currentStepId: Optional[int] = None
    permalink:Optional[str] = None
    createdBy: int
    createdAt: datetime
    name: str
    usergroupId: int
    isApprover: bool
    statusDetails: Optional[str] = None
