from typing import List

from kafka import KafkaProducer


class KafkaProducerBase:
    def __init__(self, bootstrap_servers: List[str]) -> None:
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    def send_message(self, topic: str, message: str) -> None:
        self.producer.send(topic, message.encode('utf-8'))
