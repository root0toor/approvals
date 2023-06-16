from typing import List
from typing import Optional

from pydantic import BaseModel, Field


class ApprovalToggleSchema(BaseModel):
    sm_id: int
    sm_name: str
    enabled: bool
    user_id: int
    ug_id: int


class UserRemovedSchema(BaseModel):
    sm_id: int
    usergroup_id: int = Field(alias="usergroupid")
    email_id: str
    user_id: int


class UserAddedSchema(BaseModel):
    sm_id: int
    user_id: int
    collaborator_id: Optional[int] = None


class SMDeletionSchema(BaseModel):
    sm_id: int

        
class UGDeletionSchema(BaseModel):
    ugid: int
    sm_list: List[int]
