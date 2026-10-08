import pytest
from rate_limiter import TokenBucket


def test_initial_burst_consumption():
    bucket = TokenBucket(capacity=3, fill_rate_per_sec=0.0)
    assert bucket.consume(1) is True
    assert bucket.consume(1) is True
    assert bucket.consume(1) is True
    assert bucket.consume(1) is False
