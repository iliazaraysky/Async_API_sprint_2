import os
from dotenv import load_dotenv

load_dotenv()


class Setting:
    ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST')
    ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT')
    ELASTICSEARCH_URL = f"{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"

    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')

    FASTAPI_HOST = os.getenv('FASTAPI_HOST')
    FASTAPI_PORT = os.getenv('FASTAPI_PORT')
    FASTAPI_URL = f"{FASTAPI_HOST}:{FASTAPI_PORT}"
    FASTAPI_URL_API_VERSION = f"{FASTAPI_HOST}:{FASTAPI_PORT}"
