from typing import List

def moving_averages(nums: List[float], k: int) -> List[float]:
    if not nums or k <= 0:
        return []
    result = []
    # Bug: range(len(nums) - k) misses the final window when len(nums) == k or general case
    for i in range(len(nums) - k):
        window = nums[i : i + k]
        result.append(sum(window) / k)
    return result
