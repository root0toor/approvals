from sqlalchemy import text
from utils.initialize_common_utils import common_utils_ins


class HealthCheckRepository:
    def __init__(self):
        self.__engine = common_utils_ins.mysql_client
        self.__log = common_utils_ins.logger

    async def ping(self) -> bool:
        try:
            async with self.__engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            return True
        except Exception as e:
            self.__log.critical("Mysql could not be pinged")
            return False
