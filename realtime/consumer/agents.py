import logging

from realtime.consumer import app

logger = logging.getLogger(__name__)


@app.agent()
async def process_interactions(kafka_stream):
    async for record in kafka_stream:
        logger.info(record)
