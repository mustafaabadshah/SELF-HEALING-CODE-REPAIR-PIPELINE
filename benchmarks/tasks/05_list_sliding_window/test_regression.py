import pytest
from window import moving_averages


def test_standard_windows():
    nums = [1.0, 3.0, 5.0, 7.0]
    # k=2: [2.0, 4.0, 6.0]
    assert moving_averages(nums, 2) == [2.0, 4.0, 6.0]


def test_empty_or_zero():
    assert moving_averages([], 3) == []
    assert moving_averages([1, 2], 0) == []
