from typing import Any, Dict, List, Optional

def get_nested_field(data: Optional[Dict[str, Any]], path: List[str], default: Any = None) -> Any:
    current = data
    for key in path:
        # Bug: if current is None, crashes with TypeError: 'NoneType' object is not subscriptable
        current = current.get(key)
    return current if current is not None else default
