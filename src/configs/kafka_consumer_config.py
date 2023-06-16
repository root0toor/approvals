from dataclasses import dataclass
from typing import List

from utils.constant import AutoOffsetReset


@dataclass(frozen=True)
class KafkaConsumerConfig:
    servers: List[str]
    group_id: str
    auto_offset_commit: bool
    auto_offset_commit_interval: int = 5000
    auto_offset_reset: AutoOffsetReset = AutoOffsetReset.LATEST
    polling_timeout: int = 1000
    max_polling_records: int = 100
