import pytest
from profile_service import get_nested_field


def test_none_intermediate_key():
    data = {"user": None}
    res = get_nested_field(data, ["user", "settings", "theme"], default="dark")
    assert res == "dark"

    res_none = get_nested_field(None, ["user"], default="guest")
    assert res_none == "guest"
