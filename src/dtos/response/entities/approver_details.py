from pydantic import BaseModel, Field
from typing import Optional, List


class ApproverDetailResponse(BaseModel):
    id: int  # ApproverId
    email: Optional[str] = None
    approverExternalId: int
    approverType: str
    smApproverId: int = Field(alias="smApproverId")


class GetSmApproverListResponse(BaseModel):
    id: int
    email: str

class ApproverResponse(BaseModel):
    approverExternalId: int
    approverType: str

class ApproversListResponse(BaseModel):
    approvers: List[ApproverResponse]