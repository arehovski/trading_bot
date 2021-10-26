from redis import ConnectionPool, Redis
from config import REDIS_HOST, REDIS_PORT


def get_redis_connection():
    pool = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db='0', decode_responses=True)
    return Redis(connection_pool=pool)
