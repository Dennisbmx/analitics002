import os
from typing import Dict, List

try:
    from alpaca_trade_api import REST
except ImportError:  # pragma: no cover - dependency might be missing
    REST = None

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", "")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")


class AlpacaBroker:
    """Wrapper around Alpaca REST API.

    If API keys are not provided, all methods return empty data and no
    network calls are made.
    """

    def __init__(self) -> None:
        self.use_real = bool(ALPACA_API_KEY and ALPACA_API_SECRET and REST is not None)
        self.client = (
            REST(ALPACA_API_KEY, ALPACA_API_SECRET, base_url=BASE_URL)
            if self.use_real
            else None
        )

    def get_balance(self) -> float | None:
        if self.use_real:
            try:
                account = self.client.get_account()
                return float(account.equity)
            except Exception as e:  # pragma: no cover - network errors
                print(f"[AlpacaBroker] Error fetching account equity: {e}")
                return None
        return None

    def buy(self, symbol: str, qty: int):
        if self.use_real:
            try:
                return self.client.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
            except Exception as e:  # pragma: no cover
                print(f"[AlpacaBroker] Buy error: {e}")
                return None
        print("[AlpacaBroker] Trading unavailable (missing API keys)")
        return None

    def sell(self, symbol: str, qty: int):
        if self.use_real:
            try:
                return self.client.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side="sell",
                    type="market",
                    time_in_force="gtc",
                )
            except Exception as e:  # pragma: no cover
                print(f"[AlpacaBroker] Sell error: {e}")
                return None
        print("[AlpacaBroker] Trading unavailable (missing API keys)")
        return None

    def get_positions(self) -> Dict[str, Dict[str, float]]:
        """Return open positions keyed by symbol."""
        if self.use_real:
            out: Dict[str, Dict[str, float]] = {}
            try:
                for p in self.client.list_positions():
                    out[p.symbol] = {
                        "qty": float(p.qty),
                        "avg": float(p.avg_entry_price),
                        "value": float(p.market_value),
                        "pl": float(p.unrealized_pl),
                    }
                return out
            except Exception as e:  # pragma: no cover
                print(f"[AlpacaBroker] positions error: {e}")
                return {}
        return {}

    def get_prices(self, symbols: List[str]) -> Dict[str, float | None]:
        if self.use_real:
            prices: Dict[str, float] = {}
            for sym in symbols:
                try:
                    trade = self.client.get_latest_trade(sym)
                    prices[sym] = float(trade.price)
                except Exception as e:  # pragma: no cover
                    print(f"[AlpacaBroker] get_latest_trade error for {sym}: {e}")
                    prices[sym] = None
            return prices
        return {s: None for s in symbols}
