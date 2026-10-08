def is_overlapping(start1: int, end1: int, start2: int, end2: int, inclusive: bool = False) -> bool:
    # Bug: always uses <= and >= treating touching boundaries as overlapping even when inclusive is False
    return start1 <= end2 and start2 <= end1
