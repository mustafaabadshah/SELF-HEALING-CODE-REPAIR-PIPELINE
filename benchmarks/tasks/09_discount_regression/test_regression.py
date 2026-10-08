import pytest
from pricing import apply_discount


def test_decimal_discounts():
    assert apply_discount(100.0, 0.20) == 80.0
    assert apply_discount(50.0, 0.0) == 50.0
