import os

from utils.constants import APP_NAME
from .config import Config, MysqlConfig, HiverConfig,SentryDsnConfig,LogConfig
from utils.constant import LogLevel, LogChannel, AutoOffsetReset
from configs.env import KAFKA_BOOTSTRAP_SERVERS
from .kafka_consumer_config import KafkaConsumerConfig


def getLocalConfig() -> Config:
    return Config(
        app_name=APP_NAME,
        log_config=LogConfig(LOG_LEVEL=LogLevel.INFO,LOG_CHANNEL=LogChannel.STDOUT),
        mysql_config=MysqlConfig(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        ),
        hiver_config=HiverConfig(
            JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
            JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")
        ),
        sentry_dsn_config=SentryDsnConfig(sentry_dsn=os.getenv("SENTRY_DSN")),
        kafka_consumer_config=KafkaConsumerConfig(
            servers=list(KAFKA_BOOTSTRAP_SERVERS.split(',')),
            group_id="approvals-consumer",
            auto_offset_commit=False,
            max_polling_records=100,
            polling_timeout=1000,
            auto_offset_reset=AutoOffsetReset.EARLIEST,
        )
    )
