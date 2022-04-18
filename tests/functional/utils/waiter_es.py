import os
import sys
import time
import elasticsearch

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from settings import Setting
es = elasticsearch.Elasticsearch([f'{Setting.ELASTICSEARCH_URL}'], request_timeout=300)

retries = 0

while True:
    if es.ping() or retries >= 5:
        break
    else:
        time.sleep(5)
        retries += 1
