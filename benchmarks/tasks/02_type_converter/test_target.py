import pytest
from converter import parse_boolean


def test_integer_and_short_boolean():
    assert parse_boolean(1) is True
    assert parse_boolean(0) is False
    assert parse_boolean("t") is True
