from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from exceptions.errors import NoResultFoundError
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking


class NoResultFoundErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class NoResultFoundErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: NoResultFoundError) -> JSONResponse:
        response = NoResultFoundErrorResponse(error="NO_RESULT_FOUND_ERROR", message=e.message)
        
        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=response.dict(by_alias=True)
        )
