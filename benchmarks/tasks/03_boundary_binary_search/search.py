from typing import List, Optional

def binary_search(arr: List[int], target: int) -> Optional[int]:
    low = 0
    high = len(arr) - 1
    # Bug: low < high misses elements when low == high
    while low < high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None
