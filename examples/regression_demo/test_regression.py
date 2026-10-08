import pytest
from buggy_module import calculate_discounted_price


def test_decimal_discount():
    """Existing contract: callers pass 0.15 for a 15% discount."""
    assert calculate_discounted_price(100.0, 0.15) == 85.0


def test_decimal_discount_twenty():
    """Existing contract: callers pass 0.20 for a 20% discount."""
    assert calculate_discounted_price(50.0, 0.20) == 40.0


def test_zero_discount():
    """Existing contract: 0 discount returns full price."""
    assert calculate_discounted_price(50.0, 0.0) == 50.0


def test_full_discount():
    """Existing contract: 1.0 (100%) discount returns 0.0."""
    assert calculate_discounted_price(100.0, 1.0) == 0.0


def test_negative_price_raises_error():
    """Existing contract: negative price raises ValueError."""
    with pytest.raises(ValueError):
        calculate_discounted_price(-10.0, 0.1)
