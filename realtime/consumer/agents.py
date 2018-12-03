import os

import faust
import logging
import django

from django.conf import settings

from realtime.helpers import RedisHelper, MongoDBHelper, UtilityHelper
from .records import InteractionRecord

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtime.settings.base')

django.setup()

logger = logging.getLogger(__name__)

app = faust.App('tapad', broker=settings.KAFKA_HOSTS, value_type=InteractionRecord)
topic = app.topic(settings.INTERACTION_TOPIC)


def main():
    app.main()


@app.agent(topic)
async def process_interactions(kafka_stream):
    redis = RedisHelper.get_instance()
    col = MongoDBHelper.get_collection(db_name='analytics', col_name='interactions')

    idx = 1
    async for record in kafka_stream:
        data = {}
        try:
            dt = UtilityHelper.ts_to_dt(record['timestamp'], False)
            ts_suffix = UtilityHelper.dt_to_str(dt, UtilityHelper.STD_FORMAT)

            data.update(**{
                'user': record['user'],
                'action': record['action'],
                'timestamp': dt
            })
        except KeyError as err:
            logger.exception(err)
            continue

        unique_users_key = RedisHelper.get_unique_users_key(ts_suffix)
        interactions_key = RedisHelper.get_interactions_key(ts_suffix)

        with redis.pipeline(transaction=True) as pipe:
            pipe.exists(unique_users_key)
            pipe.exists(interactions_key)
            pipe.sadd(unique_users_key, data['user'])

            if data['action'] == 'impression':
                pipe.hincrby(interactions_key, 'impressions', 1)
            else:
                pipe.hincrby(interactions_key, 'clicks', 1)

            uu_exists, in_exists, *_ = pipe.execute(raise_on_error=True)

            if not uu_exists:
                redis.expire(unique_users_key, 3600)

            if not in_exists:
                redis.expire(interactions_key, 3600 * 24 * 7)

        col.insert(data)

        idx += 1
        if idx % 10:
            logger.info("Consumed %d items so far ... Interaction stats: %s" % (
                idx, redis.hgetall(interactions_key)
            ))
