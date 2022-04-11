import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Конфигурация для доступа к БД Postgresql
dsl = {
        'dbname': os.getenv('POSTGRESQL_DB'),
        'user': os.getenv('POSTGRESQL_USER'),
        'password': os.getenv('POSTGRESQL_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
}

# Конфигурация для доступа к Elasticsearch
config = {
        'scheme': os.getenv('SCHEME'),
        'host': os.getenv('DB_HOST_ELASTIC'),
        'port': os.getenv('ELASTIC_PORT')
}

# Конфигурация логов
logging.basicConfig(
    filename='ETL.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)
logger = logging.getLogger()
