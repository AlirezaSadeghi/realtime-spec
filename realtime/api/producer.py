import json

from django.conf import settings
from kafka import KafkaProducer


class ProducerService(object):
    producer = None

    CONFIG = {
        'acks': -1,
        'linger_ms': 25,
        'bootstrap_servers': settings.KAFKA_HOSTS,
        'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
        'retries': 5
    }

    @classmethod
    def get_instance(cls):
        if not cls.producer:
            cls.producer = KafkaProducer(**ProducerService.CONFIG)

        return cls.producer
