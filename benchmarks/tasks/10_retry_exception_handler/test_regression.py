import pytest
from retry_handler import execute_with_retry, TransientError


def test_transient_error_succeeds_on_retry():
    attempts = 0
    def flaky():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise TransientError("Network blip")
        return "success"

    res = execute_with_retry(flaky, max_retries=3, retry_exceptions=(TransientError,))
    assert res == "success"
    assert attempts == 2
