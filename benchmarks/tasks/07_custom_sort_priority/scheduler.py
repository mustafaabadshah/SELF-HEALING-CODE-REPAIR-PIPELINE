from typing import List, Dict, Any

PRIORITY_MAP = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}

def sort_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Bug: ignores timestamp for secondary sorting
    return sorted(tasks, key=lambda t: PRIORITY_MAP.get(t.get("priority", "LOW"), 4))
