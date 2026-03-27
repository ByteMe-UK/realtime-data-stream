"""
Simulated real-time data producer.

Generates realistic-looking live data for 4 streams:
  - AAPL, GOOGL, MSFT (simulated stock prices via random walk)
  - BTC   (simulated crypto price — higher volatility)

Each call to get_latest_prices() returns the current prices.
State is maintained in module-level variables so all callbacks
share the same data without a database.
"""

import random
import threading
from collections import deque
from datetime import datetime

import pandas as pd

# ── Initial prices ────────────────────────────────────────────
_TICKERS = {
    "AAPL":  {"price": 185.0,   "volatility": 0.003},
    "GOOGL": {"price": 140.0,   "volatility": 0.004},
    "MSFT":  {"price": 415.0,   "volatility": 0.003},
    "BTC":   {"price": 65000.0, "volatility": 0.012},
}

MAX_POINTS = 120  # keep 2 minutes of data at 1s interval

_history: dict[str, deque] = {
    ticker: deque(maxlen=MAX_POINTS) for ticker in _TICKERS
}
_lock = threading.Lock()


def _tick() -> None:
    """Advance each ticker by one random step."""
    ts = datetime.now()
    with _lock:
        for ticker, info in _TICKERS.items():
            price = info["price"]
            change = price * info["volatility"] * random.gauss(0, 1)
            new_price = max(price + change, price * 0.5)  # floor at 50% of current
            _TICKERS[ticker]["price"] = round(new_price, 2)
            _history[ticker].append({"time": ts, "price": new_price})


def get_history() -> dict[str, pd.DataFrame]:
    """Return a dict of DataFrames, one per ticker, with columns [time, price]."""
    with _lock:
        return {
            ticker: pd.DataFrame(list(pts), columns=["time", "price"])
            for ticker, pts in _history.items()
            if pts
        }


def get_current_prices() -> dict[str, float]:
    """Return the latest price for each ticker."""
    with _lock:
        return {t: info["price"] for t, info in _TICKERS.items()}


def initialise() -> None:
    """Seed history with 60 initial data points before the app starts."""
    for _ in range(60):
        _tick()


def tick() -> None:
    """Public single-tick function called by the Dash interval callback."""
    _tick()
