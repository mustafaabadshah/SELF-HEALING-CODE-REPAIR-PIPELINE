import pytest
from retry_handler import execute_with_retry, TransientError


def test_fatal_error_not_retried():
    calls = 0
    def bad_fn():
        nonlocal calls
        calls += 1
        raise ValueError("Fatal configuration error")

    with pytest.raises(ValueError):
        execute_with_retry(bad_fn, max_retries=3, retry_exceptions=(TransientError,))

    # Fatal error should not have been retried 3 times!
    assert calls == 1
