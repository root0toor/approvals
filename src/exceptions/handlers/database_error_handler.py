import http

from fastapi import Request, status

from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError

from dtos.response.errors import DatabaseErrorResponse
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking


class DatabaseErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: DBAPIError) -> JSONResponse:
        response = DatabaseErrorResponse(error="DATABASE ERROR",
                                         status=http.HTTPStatus.INTERNAL_SERVER_ERROR)

        self.__log.error(f"{response.error} : {e} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.dict(by_alias=True)
        )
