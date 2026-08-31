"""A deliberately buggy calculator used to demonstrate a maker-checker fix loop.

THE BUG:
    calculate_total(price, quantity) returns `price + quantity`,
    but the correct behavior (total price of `quantity` items at `price`
    each) is `price * quantity`.
"""


def calculate_total(price, quantity):
    # BUG: addition instead of multiplication
    return price + quantity
