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
BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

class AlpacaBroker:
    """Broker abstraction: real via Alpaca or fallback to Yahoo Finance."""

    def __init__(self):
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
        else:
            # Для теста без Alpaca можно вернуть константу, например 10000
            return 10000.0

    def buy(self, symbol: str, qty: int):
        if self.use_real:
            try:
                return self.client.submit_order(symbol=symbol, qty=qty,
                                               side='buy', type='market',
                                               time_in_force='gtc')
            except Exception as e:
                print(f"[AlpacaBroker] Buy error: {e}")
                return None
        print(f"[MOCK] Buy {qty} {symbol}")
        return {'symbol': symbol, 'qty': qty, 'side': 'buy', 'mock': True}

    def sell(self, symbol: str, qty: int):
        if self.use_real:
            try:
                return self.client.submit_order(symbol=symbol, qty=qty,
                                               side='sell', type='market',
                                               time_in_force='gtc')
            except Exception as e:
                print(f"[AlpacaBroker] Sell error: {e}")
                return None
        print(f"[MOCK] Sell {qty} {symbol}")
        return {'symbol': symbol, 'qty': qty, 'side': 'sell', 'mock': True}

    def get_last_price_yf(self, ticker_symbol: str) -> float:
        if yf is None:
            return 0.0
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Пробуем fast_info
            if hasattr(ticker, "fast_info") and getattr(ticker, "fast_info"):
                price = getattr(ticker, "fast_info").get("last_price", None)
                if price is not None:
                    return float(price)
            # Через историю — последнее закрытие
            hist = ticker.history(period="5d")
            if not hist.empty:
                return float(hist["Close"].dropna()[-1])
            return 0.0
        except Exception as e:
            print(f"[AlpacaBroker] Error fetching Yahoo price for {ticker_symbol}: {e}")
            return 0.0

    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        prices: Dict[str, float] = {}
        if self.use_real:
            for sym in symbols:
                try:
                    trade = self.client.get_latest_trade(sym)
                    prices[sym] = float(trade.price)
                except Exception as e:
                    print(f"[AlpacaBroker] get_latest_trade error for {sym}: {e}")
                    prices[sym] = 0.0
        else:
            for sym in symbols:
                prices[sym] = self.get_last_price_yf(sym)
        return prices
