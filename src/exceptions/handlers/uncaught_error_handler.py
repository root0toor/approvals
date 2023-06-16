from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking


class UncaughtErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str

# todo-nithin:
# check if error is logged properly

class UncaughtErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: Exception) -> JSONResponse:
        response = UncaughtErrorResponse(error="UNCAUGHT_ERROR", message="Something went wrong")
        
        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.dict(by_alias=True),
        )
