from typing import List, Dict
from autotrade.brokers.alpaca_client import AlpacaBroker

class TradeEngine:
    def __init__(self):
        self.broker = AlpacaBroker()

    def buy(self, symbol: str, qty: int):
        try:
            return self.broker.buy(symbol, qty)
        except Exception as e:
            print(f"[TradeEngine] BUY error for {symbol}: {e}")
            return None

    def sell(self, symbol: str, qty: int):
        try:
            return self.broker.sell(symbol, qty)
        except Exception as e:
            print(f"[TradeEngine] SELL error for {symbol}: {e}")
            return None

    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        try:
            return self.broker.get_prices(symbols)
        except Exception as e:
            print(f"[TradeEngine] get_prices error: {e}")
            # Вернуть нули по всем символам при ошибке
            return {s: 0.0 for s in symbols}
