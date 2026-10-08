def calculate_sales_tax(subtotal: float, tax_rate: float, round_up: bool = False) -> float:
    # Bug: ignores round_up parameter completely
    return round(subtotal * tax_rate, 2)
