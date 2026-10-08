from typing import List, Dict, Any

def paginate_items(items: List[Any], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    if page < 1:
        page = 1
    start = (page - 1) * page_size
    end = start + page_size
    slice_items = items[start:end]
    
    # Bug: has_next returns True if end <= len(items), meaning if len(items)==20 and page=2, end=20 <= 20 gives True!
    has_next = end <= len(items)
    
    return {
        "items": slice_items,
        "page": page,
        "page_size": page_size,
        "total_items": len(items),
        "has_next": has_next,
    }
