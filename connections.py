from kucoin.client import Margin, User
from redis import ConnectionPool, Redis
from config import REDIS_HOST, REDIS_PORT, API_KEY, API_SECRET, API_PASSPHRASE


def get_redis_connection():
    pool = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db='0', decode_responses=True)
    return Redis(connection_pool=pool)


def get_margin_api() -> Margin:
    return Margin(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE)


def get_user_api() -> User:
    return User(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE)
