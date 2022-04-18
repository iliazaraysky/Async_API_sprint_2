import os
import sys
import time
from redis import Redis, ConnectionError

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from settings import Setting

redis = Redis(host=Setting.REDIS_HOST, port=Setting.REDIS_PORT)

retries = 0

while retries < 5:
    try:
        redis.ping()
        break
    except ConnectionError:
        time.sleep(5)
        retries += 1



