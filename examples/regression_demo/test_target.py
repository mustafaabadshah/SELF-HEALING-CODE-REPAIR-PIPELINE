import pytest
from buggy_module import calculate_discounted_price


def test_discount_with_percentage_string():
    """Target test that currently fails on the buggy baseline."""
    result = calculate_discounted_price(100.0, "20%")
    assert result == 80.0
