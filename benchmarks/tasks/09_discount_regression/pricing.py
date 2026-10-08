def apply_discount(total: float, discount_val) -> float:
    # Bug: fails on string percentages e.g. "15%"
    return round(total * (1.0 - float(discount_val)), 2)
