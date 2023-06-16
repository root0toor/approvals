from typing import Any, Dict, List, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils.initialize_common_utils import common_utils_ins
from exceptions.errors import InvalidArgumentError
from utils.helper import errorTracking


class InvalidArgumentErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class InvalidArgumentErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: InvalidArgumentError) -> JSONResponse:
        response = InvalidArgumentErrorResponse(error="INVALID_ARGUMENT_ERROR", message=e.message)

        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.dict(by_alias=True),
        )
