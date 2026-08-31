"""Tests that expose the bug in src/calculator.py.

These tests encode the *expected* behavior. The current buggy
implementation (`price + quantity`) fails them; the correct
implementation (`price * quantity`) passes them all.
"""

import pytest

from src.calculator import calculate_total


def test_single_item_total():
    # 3 items? No: price=3, quantity=2 -> 2 items at 3 each = 6
    assert calculate_total(3, 2) == 6


def test_multiple_items():
    assert calculate_total(10, 4) == 40


def test_zero_quantity():
    # zero quantity should cost zero, regardless of price
    assert calculate_total(5, 0) == 0


def test_single_item_of_each():
    assert calculate_total(7, 1) == 7


def test_float_prices():
    assert calculate_total(2.5, 4) == 10.0
