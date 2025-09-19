#!/usr/bin/env python3
"""
Type checking example to demonstrate mypy functionality
Run with: mypy test_mypy.py --config-file mypy.ini
"""
from typing import List, Optional


def process_cryptocurrency_names(names: List[str]) -> Optional[str]:
    """
    Process a list of cryptocurrency names and return a formatted string.

    Args:
        names: List of cryptocurrency names

    Returns:
        Formatted string or None if empty list
    """
    if not names:
        return None

    cleaned_names = [name.upper().strip() for name in names]
    unique_names = list(set(cleaned_names))
    return ", ".join(sorted(unique_names))


def calculate_total_market_cap(market_caps: List[float]) -> float:
    """
    Calculate total market capitalization from a list.

    Args:
        market_caps: List of market cap values

    Returns:
        Total market capitalization
    """
    return sum(market_caps)


class CryptocurrencyTracker:
    """Example class with type annotations."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.price: float = 0.0
        self.market_cap: Optional[float] = None

    def update_price(self, new_price: float) -> None:
        """Update the cryptocurrency price."""
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        self.price = new_price

    def get_display_name(self) -> str:
        """Get display name for the cryptocurrency."""
        return f"{self.name} (${self.price:,.2f})"


# Example usage with intentional type error to test mypy
if __name__ == "__main__":
    # This should work fine
    tracker = CryptocurrencyTracker("Bitcoin")
    tracker.update_price(45000.0)
    display_name = tracker.get_display_name()

    crypto_names = ["bitcoin", "ethereum", "cardano"]
    formatted_names = process_cryptocurrency_names(crypto_names)
    market_caps = [1000000000.0, 500000000.0]
    total_cap = calculate_total_market_cap(market_caps)

    print(f"Crypto tracker: {display_name}")
    print(f"Formatted names: {formatted_names}")
    print(".2f")

    # Uncomment to see mypy error:
    # tracker.update_price("not a number")  # Type error: should be float