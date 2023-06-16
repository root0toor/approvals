from comlib.kafka.base_producer import KafkaProducerBase
from configs.env import KAFKA_BOOTSTRAP_SERVERS

bootstrap_servers = list(KAFKA_BOOTSTRAP_SERVERS.split(','))

# 1 producer for every topic, since 1 source of truth
event_producer = KafkaProducerBase(bootstrap_servers=bootstrap_servers)
