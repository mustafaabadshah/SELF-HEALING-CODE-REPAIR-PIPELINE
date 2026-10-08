import pytest
from scheduler import sort_tasks


def test_equal_priority_secondary_timestamp():
    tasks = [
        {"id": "b", "priority": "HIGH", "created_at": 200},
        {"id": "a", "priority": "HIGH", "created_at": 100},
    ]
    sorted_res = sort_tasks(tasks)
    # Earlier timestamp (100) should come before 200
    assert [t["id"] for t in sorted_res] == ["a", "b"]
