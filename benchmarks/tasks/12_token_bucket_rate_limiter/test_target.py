import pytest
import time
from rate_limiter import TokenBucket


def test_capacity_clamping():
    bucket = TokenBucket(capacity=5, fill_rate_per_sec=10.0)
    # Simulate time passing
    bucket.last_update -= 10.0  # 10 seconds ago -> would generate 100 tokens if unclamped
    bucket.consume(1)
    # Tokens after consuming 1 should not exceed capacity - 1 (4)
    assert bucket.tokens <= 4.0
