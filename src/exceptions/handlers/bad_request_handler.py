from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from exceptions.errors import BadRequestError
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking


class BadRequestErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class BadRequestErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: BadRequestError) -> JSONResponse:
        response = BadRequestErrorResponse(error="BAD_REQUEST_ERROR", message=e.message)

        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")
         
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response.dict(by_alias=True),
        )
