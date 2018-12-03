from datetime import datetime, timedelta

from django.conf import settings
from kafka import KafkaProducer
from pymongo import MongoClient

from redis import StrictRedis
from pymongo import WriteConcern


class UtilityHelper:
    STD_FORMAT = '%Y-%m-%dT%H'

    @staticmethod
    def ts_is_valid(ts):
        if not isinstance(ts, int):
            ts = int(ts)
        try:
            timestamp = datetime.utcfromtimestamp(ts)
            if timestamp > datetime.now():
                return False
        except ValueError:
            return False
        return True

    @staticmethod
    def ts_to_dt(ts, stringify=False):
        if not isinstance(ts, int):
            ts = int(ts)

        dt = datetime.utcfromtimestamp(ts)
        if stringify:
            return dt.strftime(UtilityHelper.STD_FORMAT)
        return dt

    @staticmethod
    def dt_to_str(dt, date_format):
        return dt.strftime(date_format)

    @staticmethod
    def str_to_dt(date_str, date_format):
        return datetime.strptime(date_str, date_format)

    @staticmethod
    def dict_validator(data, *items):
        for item in items:
            if item not in data or not data.get(item):
                return False
        return True


class ProducerHelper:
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = KafkaProducer(**settings.KAFKA_PRODUCER_CONFIG)

        return cls.instance


class RedisHelper:
    instance = None

    _unique_users_template = 'unique_users-%s'
    _interactions_template = 'interactions-%s'

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = StrictRedis(**settings.REDIS_CONFIG)

        return cls.instance

    @staticmethod
    def get_unique_users_key(ts_suffix):
        return RedisHelper._unique_users_template % ts_suffix

    @staticmethod
    def get_interactions_key(ts_suffix):
        return RedisHelper._interactions_template % ts_suffix

    @staticmethod
    def get_data(ts_suffix):
        result = {}
        redis = RedisHelper.get_instance()

        interaction_key = RedisHelper.get_interactions_key(ts_suffix)
        if redis.exists(interaction_key):
            result.update(**redis.hgetall(interaction_key))

        unique_users_key = RedisHelper.get_unique_users_key(ts_suffix)
        if redis.exists(unique_users_key):
            result.update(**{'unique_users': redis.scard(unique_users_key)})

        return result


class MongoDBHelper:
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = MongoClient(**settings.MONGODB_CONFIG)

        return cls.instance

    @classmethod
    def get_collection(cls, db_name, col_name, w=1):
        conn = MongoDBHelper.get_instance()
        return conn.get_database(db_name).get_collection(col_name, write_concern=WriteConcern(w=w))

    @staticmethod
    def aggregate_elements(ts_suffix, field=None, pivote_field='user'):
        date_floor = UtilityHelper.str_to_dt(ts_suffix, UtilityHelper.STD_FORMAT)
        col = MongoDBHelper.get_collection('analytics', 'interactions')

        aggregation_stages = [
            {
                '$match': {
                    'timestamp': {
                        '$gte': date_floor,
                        '$lt': date_floor + timedelta(hours=1)
                    }
                }
            },

        ]

        if field:
            aggregation_stages.append({
                '$group': {
                    '_id': '$%s' % field,
                    'count': {'$sum': 1}
                }
            })

            return list(col.aggregate(aggregation_stages, allowDiskUse=True, cursor={}))[0]['count']

        aggregation_stages += [
            {
                '$group': {
                    '_id': '$%s' % pivote_field,
                    'clicks': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$eq': [
                                        '$action', 'click'
                                    ]
                                },
                                1, 0
                            ]
                        }
                    },
                    'impressions': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$eq': [
                                        '$action', 'impression'
                                    ]
                                },
                                1, 0
                            ]
                        }
                    },
                }
            },
            {
                '$group': {
                    '_id': None,
                    'unique_users': {
                        '$sum': 1
                    },
                    'clicks': {
                        '$sum': '$clicks'
                    },
                    'impressions': {
                        '$sum': '$impressions'
                    }
                }
            }
        ]
        response = list(col.aggregate(aggregation_stages, allowDiskUse=True, cursor={}))[0]
        response.pop('_id', None)
        return response
