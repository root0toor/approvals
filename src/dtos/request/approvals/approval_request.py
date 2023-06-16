from string import whitespace
from pydantic import BaseModel, constr
from typing import Optional, Literal


class CreateApprovalRequest(BaseModel):
    approvalFlowId: int
    conversationId: int
    smId: str


class ProcessApprovalRequest(BaseModel):
    approvalRequestId: str
    status: Literal["APPROVED", "REJECTED", "CANCELLED"]
    reason: Optional[str] = None
    note: Optional[constr(max_length=100, strip_whitespace=True)] = None
