import os

import elasticsearch
from backoff import backoff
from dotenv import load_dotenv

load_dotenv()


@backoff()
def check_es():
    es = elasticsearch.Elasticsearch([f'{os.getenv("ELASTICSEARCH_URL")}'], request_timeout=300)
    if not es.ping():
        raise elasticsearch.ConnectionError


if __name__ == "__main__":
    check_es()
