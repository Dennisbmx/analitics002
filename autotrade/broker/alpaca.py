import os
from typing import Dict, List, Optional

import httpx

try:
    from alpaca_trade_api import REST
except ImportError:
    REST = None

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", "")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY", "")

class AlpacaBroker:
    """
    Broker abstraction: uses Alpaca API if possible, falls back to Twelve Data for prices if not.
    """

    def __init__(self) -> None:
        self.use_real = bool(ALPACA_API_KEY and ALPACA_API_SECRET and REST is not None)
        self.client = (
            REST(ALPACA_API_KEY, ALPACA_API_SECRET, base_url=BASE_URL)
            if self.use_real
            else None
        )

    def get_balance(self) -> Optional[float]:
        if self.use_real:
            try:
                account = self.client.get_account()
                return float(account.equity)
            except Exception as e:
                print(f"[AlpacaBroker] Error fetching account equity: {e}")
        return None

    def buy(self, symbol: str, qty: int) -> Optional[dict]:
        if self.use_real:
            try:
                return self.client.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
            except Exception as e:
                print(f"[AlpacaBroker] Buy error: {e}")
                return None
        print("[AlpacaBroker] Trading unavailable (missing API keys)")
        return None

    def sell(self, symbol: str, qty: int) -> Optional[dict]:
        if self.use_real:
            try:
                return self.client.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side="sell",
                    type="market",
                    time_in_force="gtc",
                )
            except Exception as e:
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
            except Exception as e:
                print(f"[AlpacaBroker] positions error: {e}")
        return {}

    def get_prices(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        """Return prices for symbols: from Alpaca, fallback to Twelve Data if set, else None."""
        if self.use_real:
            prices: Dict[str, Optional[float]] = {}
            for sym in symbols:
                try:
                    trade = self.client.get_latest_trade(sym)
                    prices[sym] = float(trade.price)
                except Exception as e:
                    print(f"[AlpacaBroker] get_latest_trade error for {sym}: {e}")
                    prices[sym] = None
            return prices
        elif TWELVE_DATA_KEY:
            # fallback to Twelve Data API for prices
            prices: Dict[str, Optional[float]] = {s: None for s in symbols}
            url = "https://api.twelvedata.com/price"
            for symbol in symbols:
                try:
                    resp = httpx.get(
                        url,
                        params={"symbol": symbol, "apikey": TWELVE_DATA_KEY},
                        timeout=10,
                    )
                    data = resp.json()
                    if "price" in data:
                        prices[symbol] = float(data["price"])
                    else:
                        prices[symbol] = None
                except Exception as e:
                    print(f"[AlpacaBroker] Twelve Data price error for {symbol}: {e}")
                    prices[symbol] = None
            return prices
        else:
            return {s: None for s in symbols}

