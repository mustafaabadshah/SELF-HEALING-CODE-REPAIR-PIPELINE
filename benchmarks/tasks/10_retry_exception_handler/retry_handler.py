import time
from typing import Callable, Any

class TransientError(Exception):
    pass

def execute_with_retry(fn: Callable[[], Any], max_retries: int = 3, retry_exceptions=(TransientError,)) -> Any:
    attempts = 0
    while attempts < max_retries:
        try:
            return fn()
        except Exception as e:
            # Bug: catches ALL exceptions instead of only retry_exceptions, swallowing fatal errors
            attempts += 1
            if attempts >= max_retries:
                raise e
    return None
