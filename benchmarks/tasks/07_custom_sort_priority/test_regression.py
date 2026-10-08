import pytest
from scheduler import sort_tasks


def test_distinct_priorities():
    tasks = [
        {"id": "low_1", "priority": "LOW", "created_at": 10},
        {"id": "high_1", "priority": "HIGH", "created_at": 50},
        {"id": "med_1", "priority": "MEDIUM", "created_at": 20},
    ]
    sorted_res = sort_tasks(tasks)
    assert [t["id"] for t in sorted_res] == ["high_1", "med_1", "low_1"]
