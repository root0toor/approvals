from pydantic import BaseModel


class ListApprovalFlowDetailResponse(BaseModel):
    id: int
    name: str
    createdBy: int
    usergroupId: int
    isActive: bool

    class Config:
        orm_mode = True


class ApprovalFlowDetailResponse(ListApprovalFlowDetailResponse):
    smId: int
    initialStepId: int
