from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from configs.config import Config, MysqlConfig
from comlib.logs import CustomAPILogger


class CommonUtils:
    def __init__(self, config: Config):
        self.mysql_client = CommonUtils.__initialize_db(config.mysql_config)

        self.logger = CustomAPILogger(config).get_logger()
        
        self.config = config

    @staticmethod
    def __initialize_db(config: MysqlConfig) -> AsyncEngine:
        connection_string = (
            f"mysql+aiomysql://{config.username}:{config.password}"
            f"@{config.host}:{config.port}/{config.database}"
        )
        return create_async_engine(
            connection_string,
            echo=config.echo_logs,
            pool_size=config.min_pool_size,
            max_overflow=config.max_pool_size,
        )

    def get_db_session(self) -> AsyncSession:
        return sessionmaker(bind=self.mysql_client, expire_on_commit=False, class_=AsyncSession)()
