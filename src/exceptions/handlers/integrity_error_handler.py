from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy.exc import IntegrityError
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking


class IntegrityErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class IntegrityErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: IntegrityError) -> JSONResponse:
        response = IntegrityErrorResponse(error="INTEGRITY_ERROR", message="Database operation failed")
        
        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response.dict(by_alias=True),
        )
