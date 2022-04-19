from backoff import backoff
from dotenv import load_dotenv
from redis import Redis, ConnectionError

load_dotenv()


@backoff()
def check_redis():
    redis = Redis(host=f'{"REDIS_HOST"}', port=f'{"REDIS_PORT"}')
    if not redis.ping():
        raise ConnectionError


if __name__ == "__main__":
    check_redis()
