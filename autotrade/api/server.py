# autotrade/brokers/alpaca_client.py

import os
from typing import Dict, List

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    from alpaca_trade_api import REST
except ImportError:
    REST = None

ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET', '')

class AlpacaBroker:
    """Unified Alpaca + Yahoo Finance broker."""

    def __init__(self):
        self.use_real = bool(ALPACA_API_KEY and ALPACA_API_SECRET and REST is not None)
        if self.use_real:
            self.client = REST(ALPACA_API_KEY, ALPACA_API_SECRET)
        else:
            self.client = None

    def buy(self, symbol: str, qty: int):
        if self.use_real:
            try:
                return self.client.submit_order(
                    symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc'
                )
            except Exception as e:
                print(f"[AlpacaBroker] BUY ERROR: {e}")
                return {"error": str(e)}
        print(f"[MOCK] Buy {qty} {symbol}")
        return {'symbol': symbol, 'qty': qty, 'side': 'buy', 'mock': True}

    def sell(self, symbol: str, qty: int):
        if self.use_real:
            try:
                return self.client.submit_order(
                    symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc'
                )
            except Exception as e:
                print(f"[AlpacaBroker] SELL ERROR: {e}")
                return {"error": str(e)}
        print(f"[MOCK] Sell {qty} {symbol}")
        return {'symbol': symbol, 'qty': qty, 'side': 'sell', 'mock': True}

    def get_last_price_yf(self, ticker_symbol: str) -> float:
        if yf is None:
            return 0.0
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Пробуем fast_info
            fast_info = getattr(ticker, "fast_info", None)
            if fast_info and getattr(fast_info, "last_price", None):
                return float(fast_info["last_price"])
            # Пробуем через историю
            hist = ticker.history(period="5d")
            if not hist.empty:
                return float(hist["Close"].dropna()[-1])
            return 0.0
        except Exception as e:
            print(f"[AlpacaBroker] Yahoo price error for {ticker_symbol}: {e}")
            return 0.0

    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        prices: Dict[str, float] = {}
        if self.use_real:
            for sym in symbols:
                try:
                    trade = self.client.get_latest_trade(sym)
                    prices[sym] = float(trade.price)
                except Exception as e:
                    print(f"[AlpacaBroker] Alpaca get_latest_trade error for {sym}: {e}")
                    prices[sym] = 0.0
        else:
            for sym in symbols:
                prices[sym] = self.get_last_price_yf(sym)
        return prices

    def get_balance(self) -> float:
        if self.use_real:
            try:
                account = self.client.get_account()
                return float(account.cash)
            except Exception as e:
                print(f"[AlpacaBroker] Error getting Alpaca balance: {e}")
                return 0.0
        else:
            return 10000.0  # mock balance (offline mode)
