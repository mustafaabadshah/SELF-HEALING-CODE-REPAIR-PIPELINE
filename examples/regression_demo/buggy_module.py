"""
Discount calculation service.
BUG: Does not support string percentages like '20%'.
Attempt 1 (naive): Coder divides all discounts by 100, which breaks existing decimal discounts (0.15 becomes 0.0015!).
Attempt 2 (healed): Coder inspects string vs decimal fraction properly.
"""

def calculate_discounted_price(price: float, discount) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative")
    # Buggy baseline: assumes discount is numeric decimal only, fails on string '20%'
    return round(price * (1.0 - discount), 2)
