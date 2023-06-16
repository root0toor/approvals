from typing import Any
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    status: int = 1
    data: Any

class FailureResponse(SuccessResponse):
    status: int = 0
