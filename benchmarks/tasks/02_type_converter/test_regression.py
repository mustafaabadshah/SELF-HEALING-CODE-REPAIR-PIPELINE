import pytest
from converter import parse_boolean


def test_standard_strings():
    assert parse_boolean("true") is True
    assert parse_boolean("False") is False
    assert parse_boolean("YES") is True
    assert parse_boolean("no") is False


def test_invalid_string():
    with pytest.raises(ValueError):
        parse_boolean("invalid_val")
