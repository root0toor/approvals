from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from exceptions.errors import AuthorizationError
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking

class AuthorizationErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class AuthorizationErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: AuthorizationError) -> JSONResponse:
        response = AuthorizationErrorResponse(error="AUTHORIZATION_ERROR", message="Operation not permitted")
      
        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content=response.dict(by_alias=True)
        )
