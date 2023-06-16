from exceptions.errors import BadRequestError
from pydantic import BaseModel, Field, constr, root_validator, validator
from typing import Any, Dict, List, Literal, Optional
from utils.constant import USER_TYPE

class ApproverRequest(BaseModel):
    type: Literal["SM_USER", "COLLABORATOR"]
    value: constr(min_length=1)
    
    class Config:
        anystr_strip_whitespace = True


class CreateApprovalFlowRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    smId: int
    steps: List[List[ApproverRequest]]

    class Config:
        anystr_strip_whitespace = True
 
    @validator('name')
    def validate_name(cls, name):
        if name.isnumeric():
            raise ValueError("Approval flow name should atleast contain one character")
        return name

      
    @validator('steps')
    def validate_steps(cls, steps):
        if len(steps) < 1:
            raise ValueError("There should be atleast 1 step")
        
        collaborators = set()
        sm_users = set()
        for step in steps:
            if len(step) < 1:
                raise ValueError("There should be atleast 1 approver in a step")
            for approver in step:
                if approver.type == USER_TYPE.SM_USER and (not approver.value.isdigit()):
                    raise ValueError("The value should be an integer for an SM user")
            
                if approver.type == USER_TYPE.COLLABORATOR and approver.value in collaborators:
                    raise ValueError("Same approver of type collaborator cannot be used multiple times.")
                elif approver.type == USER_TYPE.SM_USER and approver.value in sm_users:
                    raise ValueError("Same approver of type sm_user cannot be used multiple times.")
                
                if approver.type == USER_TYPE.COLLABORATOR:
                   collaborators.add(approver.value)
                else:
                    sm_users.add(approver.value)

        return steps


class UpdateApprovalFlowRequest(BaseModel):
    smId: int
    name: Optional[constr(min_length=1, max_length=100, strip_whitespace=True)] = None
    isActive: Optional[bool] = None

    @root_validator
    def at_least_one_field(cls, v):
        optional_fields = []
        for name, value in UpdateApprovalFlowRequest.__fields__.items():
            if not value.required:
                optional_fields.append(name)

        for field in optional_fields:
            if v.get(field, None) is not None:
                return v
        raise BadRequestError('Require at least one field in request')
        

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        return super().dict(*args, exclude_none=True, **kwargs)