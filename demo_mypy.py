#!/usr/bin/env python3
"""
Demo script showing mypy type checking capabilities
Run mypy on this file to see type checking in action:
    mypy demo_mypy.py --config-file mypy.ini
"""
from typing import Dict, List, Optional, Union


def calculate_portfolio_value(holdings: List[Dict[str, Union[str, float, int]]],
                             prices: Dict[str, float]) -> float:
    """
    Calculate the total value of a crypto portfolio.

    Args:
        holdings: List of holdings with structure:
                {"symbol": str, "amount": float, "purchase_price": float}
        prices: Current prices mapped by symbol

    Returns:
        Total portfolio value
    """
    total_value = 0.0

    for holding in holdings:
        symbol = holding.get("symbol")
        amount = holding.get("amount", 0.0)
        current_price = prices.get(symbol, 0.0)

        if isinstance(symbol, str) and isinstance(amount, (int, float)):
            holding_value = (amount * current_price)
            total_value += holding_value

    return total_value


def get_crypto_info(symbol: str, data: Dict[str, Dict[str, Union[str, float, int]]]) -> Optional[Dict[str, Union[str, float, int]]]:
    """
    Get cryptocurrency information from a data dictionary.

    Args:
        symbol: Cryptocurrency symbol
        data: Dictionary mapping symbols to their data

    Returns:
        Cryptocurrency data or None if not found
    """
    return data.get(symbol)


# Example usage that demonstrates type safety benefits
if __name__ == "__main__":
    # Sample data
    holdings = [
        {"symbol": "BTC", "amount": 0.5, "purchase_price": 45000.0},
        {"symbol": "ETH", "amount": 10.0, "purchase_price": 3000.0},
    ]

    prices = {
        "BTC": 47000.0,
        "ETH": 3100.0,
        "ADA": 0.45
    }

    crypto_data = {
        "BTC": {"name": "Bitcoin", "market_cap": 900000000000.0, "rank": 1},
        "ETH": {"name": "Ethereum", "market_cap": 400000000000.0, "rank": 2}
    }

    # Calculate portfolio value
    portfolio_value = calculate_portfolio_value(holdings, prices)
    print("$.2f")

    # Get crypto info
    btc_info = get_crypto_info("BTC", crypto_data)
    if btc_info:
        print(f"BTC Info: {btc_info['name']} - Rank {btc_info['rank']}")

    # The following would cause mypy errors if uncommented:
    # holdings.append("invalid holding")  # Type error: expected dict
    # holdings[0]["invalid_key"] = lambda x: x  # Type error: lambda not in Union type
    # calculate_portfolio_value("not a list", prices)  # Type error: expected List[Dict]
    # Symbol = 123  # Type error: symbol is str