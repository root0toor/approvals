from fastapi import FastAPI

from .kafka_container import KafkaContainer
from .route_controller import RouteController
from .middlewares_container import MiddlewaresContainer
from repositories.mysql_db.implementation import HealthCheckRepository
from utils.initialize_common_utils import common_utils_ins
from configs.config import Config
import sys


class Container:
    def __init__(self, *, app: FastAPI):
        self.__mysql_client = common_utils_ins.mysql_client

        # Initialize Exception Handlers
        MiddlewaresContainer(app=app)

        # Initialize Routes
        RouteController(app=app)

        app.on_event("shutdown")(self.shutdown)

    # Eager Await Mandatory External Dependencies at StartUp
    async def initialize(self, config: Config) -> None:
        try:
            mysql_health_check_repository = HealthCheckRepository()
            is_db_accessible = await mysql_health_check_repository.ping()
            if not is_db_accessible:
                raise Exception("DB Ping Not Successful")
            
            await KafkaContainer.initialize(config)

        except Exception as e:
            sys.exit(str(e.args))

    async def shutdown(self) -> None:
        await self.__mysql_client.dispose()
