from pydantic import BaseModel, validator
from enum import Enum

from configs.kafka_consumer_config import KafkaConsumerConfig


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    CRITICAL = 50
    

class LogChannel(Enum):
    STDOUT = "STDOUT"
    FILE = "FILE"
    LOGSTASH = "LOGSTASH"

class LogConfig(BaseModel):
    LOG_LEVEL: str
    LOG_CHANNEL: str
    
    @validator("LOG_LEVEL")
    def is_log_level_valid(cls, val):
        all_log_levels = LogLevel._member_names_
        if val.upper() not in all_log_levels:
            raise ValueError(
                "Incorrect log_level, allowed values are : " + ",".join(all_log_levels)
            )
        return val.upper()
    
    @validator("LOG_CHANNEL")
    def is_log_channel_valid(cls, val):
        all_log_channels = LogChannel._member_names_
        if val.upper() not in all_log_channels:
            raise ValueError(
                "Incorrect log_channel, allowed values are : " + ",".join(all_log_channels)
            )
        return val.upper()


class MysqlConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database: str
    echo_logs: bool = False
    min_pool_size: int = 50
    max_pool_size: int = 25


class HiverConfig(BaseModel):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    
    
class SentryDsnConfig(BaseModel):
    sentry_dsn:str


class Config(BaseModel):
    app_name: str

    mysql_config: MysqlConfig

    hiver_config: HiverConfig

    log_config: LogConfig
    
    sentry_dsn_config: SentryDsnConfig

    kafka_consumer_config: KafkaConsumerConfig
    
