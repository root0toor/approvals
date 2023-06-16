from pydantic import BaseModel


class DatabaseErrorResponse(BaseModel):
    status: int = 0
    error: str
