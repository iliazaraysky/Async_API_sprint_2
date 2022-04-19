import time
import logging
from functools import wraps
from datetime import datetime


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep = start_sleep_time
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if sleep >= border_sleep_time:
                        logging.info(
                            f'{datetime.now()} Превышено максимальное время ожидания'
                        )
                        break
                    else:
                        time.sleep(sleep)
                        if sleep < border_sleep_time:
                            sleep = start_sleep_time * (factor ** retries)
                            retries += 1
        return inner
    return func_wrapper
