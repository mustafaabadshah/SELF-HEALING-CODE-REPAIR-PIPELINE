import pytest
from slugifier import slugify


def test_consecutive_special_chars_and_trailing():
    assert slugify("Hello   -- World!") == "hello-world"
    assert slugify("Trailing Hyphens---") == "trailing-hyphens"
    assert slugify("---Leading Hyphens") == "leading-hyphens"
