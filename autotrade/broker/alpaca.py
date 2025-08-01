import os
from typing import Dict, List

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
    """Broker abstraction: real via Alpaca or fallback to Twelve Data."""

    def __init__(self) -> None:
        self.use_real = bool(ALPACA_API_KEY and ALPACA_API_SECRET and REST is not None)
        if self.use_real:
            self.client = REST(ALPACA_API_KEY, ALPACA_API_SECRET, base_url=BASE_URL)
        else:
            self.client = None

    def get_balance(self) -> float:
        if self.use_real:
            try:
                account = self.client.get_account()
                return float(account.equity)
            except Exception as e:
                print(f"[AlpacaBroker] Error fetching account equity: {e}")
                return 0.0
        return 10000.0

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
            except Exception as e:
                print(f"[AlpacaBroker] Buy error: {e}")
                return None
        print(f"[MOCK] Buy {qty} {symbol}")
        return {"symbol": symbol, "qty": qty, "side": "buy", "mock": True}

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
            except Exception as e:
                print(f"[AlpacaBroker] Sell error: {e}")
                return None
        print(f"[MOCK] Sell {qty} {symbol}")
        return {"symbol": symbol, "qty": qty, "side": "sell", "mock": True}

    def _get_prices_twelve(self, symbols: List[str]) -> Dict[str, float]:
        prices: Dict[str, float] = {s: 0.0 for s in symbols}
        if not TWELVE_DATA_KEY:
            return prices
        url = "https://api.twelvedata.com/price"
        try:
            resp = httpx.get(
                url,
                params={"symbol": ",".join(symbols), "apikey": TWELVE_DATA_KEY},
                timeout=10,
            )
            data = resp.json()
            if isinstance(data, dict) and "price" in data:
                prices[symbols[0]] = float(data["price"])
            else:
                for sym, info in data.items():
                    price = info.get("price")
                    prices[sym.upper()] = float(price) if price else 0.0
        except Exception as e:
            print(f"[AlpacaBroker] Twelve Data price error: {e}")
        return prices

    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        if self.use_real:
            prices: Dict[str, float] = {}
            for sym in symbols:
                try:
                    trade = self.client.get_latest_trade(sym)
                    prices[sym] = float(trade.price)
                except Exception as e:
                    print(f"[AlpacaBroker] get_latest_trade error for {sym}: {e}")
                    prices[sym] = 0.0
            return prices
        return self._get_prices_twelve(symbols)
