import os

import faust
import logging

import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtime.settings.base')

django.setup()

logger = logging.getLogger(__name__)

app = faust.App('tapad', broker=settings.KAFKA_HOSTS)


def main():
    app.main()


@app.agent()
async def process_interactions(kafka_stream):
    async for record in kafka_stream:
        logger.info(record)
