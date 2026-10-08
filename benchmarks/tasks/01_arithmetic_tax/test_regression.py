import pytest
from tax_calc import calculate_sales_tax


def test_standard_tax():
    assert calculate_sales_tax(100.0, 0.05) == 5.0


def test_zero_tax():
    assert calculate_sales_tax(50.0, 0.0) == 0.0


def test_standard_round():
    assert calculate_sales_tax(10.0, 0.0825) == 0.83
