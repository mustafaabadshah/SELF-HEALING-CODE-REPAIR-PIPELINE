import pytest
from slugifier import slugify


def test_standard_words():
    assert slugify("Simple Title") == "simple-title"
    assert slugify("Python 3.12 Release") == "python-3-12-release"


def test_already_slug():
    assert slugify("already-a-slug") == "already-a-slug"
