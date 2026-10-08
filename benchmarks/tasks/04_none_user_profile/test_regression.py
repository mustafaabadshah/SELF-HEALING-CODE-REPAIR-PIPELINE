import pytest
from profile_service import get_nested_field


def test_standard_nested_lookup():
    data = {
        "user": {
            "profile": {
                "name": "Alice",
                "email": "alice@example.com"
            }
        }
    }
    assert get_nested_field(data, ["user", "profile", "name"]) == "Alice"
    assert get_nested_field(data, ["user", "missing"], default="not_found") == "not_found"
