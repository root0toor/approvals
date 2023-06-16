from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from exceptions.errors import AuthenticationError
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking

class AuthenticationErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class AuthenticationErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: AuthenticationError) -> JSONResponse:
        response = AuthenticationErrorResponse(error="AUTHENTICATION_ERROR", message=e.message)
        
        self.__log.error(f"{response.error} :{response.message} : {errorTracking()}")
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=response.dict(by_alias=True),
        )
