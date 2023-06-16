from abc import abstractmethod
from typing import List, Callable
from aiokafka import AIOKafkaConsumer
from configs.config import Config
from utils.initialize_common_utils import common_utils_ins

class KafkaConsumerBase:

    def __init__(self, config:Config, topic: str):
        self.topic = topic
        self.__config = config

        # get from config
        self.__poll_timeout = 1000
        self.__enable_auto_commit = False
        self.__log = common_utils_ins.logger

    def initialize(self):
        self.__consumer = AIOKafkaConsumer(
            bootstrap_servers=self.__config.kafka_consumer_config.servers,
            group_id=self.__config.kafka_consumer_config.group_id,
            enable_auto_commit=self.__config.kafka_consumer_config.auto_offset_commit,
            max_poll_records=self.__config.kafka_consumer_config.max_polling_records,
            auto_offset_reset=self.__config.kafka_consumer_config.auto_offset_reset.value,
            max_poll_interval_ms=60 * 1000,
            value_deserializer=lambda m: m.decode('utf-8'),
            session_timeout_ms=20000
        )

    @abstractmethod
    async def parse(self, *, messages: List, headers_list: List):
        pass

    async def stop(self) -> None:
        await self.__consumer.stop()

    async def consume(self, callback: Callable) -> None:
        try:
            await self.__consumer.start()
            self.__consumer.subscribe(topics=[self.topic])

            print("Subscribed to topic: {}".format(self.topic))

            while True:
                data = await self.__consumer.getmany(timeout_ms=self.__poll_timeout)
                self.records_list = []
                kafka_headers = []
                # Consume events
                for topic_partition, records_list in data.items():
                    self.records_list.append(records_list)
                    
                    # This ensures that each message & header correspond for a given event
                    kafka_topic_messages = [record.value for record in records_list]
                    kafka_headers = [record.headers for record in records_list]
                    kafka_headers = KafkaConsumerBase.process_kafka_headers(kafka_headers)
                    await self.parse(messages=kafka_topic_messages, headers_list=kafka_headers)
                
                if len(self.records_list) > 0:                
                    await callback(self.records_list)
                    if not self.__enable_auto_commit:
                        await self.__consumer.commit()
        except Exception as e:
            self.__log.exception(f"{self.topic} -> Consumption failed: {e}")

    """Processes kafka headers (as tuples) and returns a dict with decoded values"""
    @staticmethod
    def process_kafka_headers(headers):
        processed_headers = []
        for header in headers:
            header_dict = dict((x, y) for x, y in header) # convert tuple to dictionary

            for key, value in header_dict.items():
                header_dict[key] = value.decode(encoding='utf-8')
            processed_headers.append(header_dict)

        return processed_headers