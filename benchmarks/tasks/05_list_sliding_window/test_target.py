import pytest
from window import moving_averages


def test_window_equals_length():
    nums = [1.0, 2.0, 3.0]
    # For k=3, there should be exactly one window with average 2.0
    res = moving_averages(nums, 3)
    assert res == [2.0]
