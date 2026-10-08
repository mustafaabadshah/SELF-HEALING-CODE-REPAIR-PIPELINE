import pytest
from tax_calc import calculate_sales_tax


def test_round_up_calculation():
    # Target test: when round_up is True, 10.005 should round up to 10.01
    val = calculate_sales_tax(100.05, 0.10, round_up=True)
    assert val == 10.01
