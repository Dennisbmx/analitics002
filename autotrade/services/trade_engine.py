from typing import Dict, List, Optional
from autotrade.broker.alpaca import AlpacaBroker
from datetime import datetime

class TradeEngine:
    def __init__(self) -> None:
        self.broker = AlpacaBroker()
        self.trade_log = []

    def buy(self, symbol: str, qty: int, trigger: str = "USER"):
        try:
            order = self.broker.buy(symbol, qty)
            self.trade_log.append({
                "action": "buy",
                "symbol": symbol,
                "qty": qty,
                "timestamp": datetime.now().isoformat(),
                "trigger": trigger,
                "status": "opened" if order else "failed",
            })
            return order
        except Exception as e:
            print(f"[TradeEngine] BUY error for {symbol}: {e}")
            return None

    def sell(self, symbol: str, qty: int, trigger: str = "USER"):
        try:
            order = self.broker.sell(symbol, qty)
            self.trade_log.append({
                "action": "sell",
                "symbol": symbol,
                "qty": qty,
                "timestamp": datetime.now().isoformat(),
                "trigger": trigger,
                "status": "closed" if order else "failed",
            })
            return order
        except Exception as e:
            print(f"[TradeEngine] SELL error for {symbol}: {e}")
            return None

    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        try:
            return self.broker.get_prices(symbols)
        except Exception as e:
            print(f"[TradeEngine] get_prices error: {e}")
            return {s: 0.0 for s in symbols}

    def get_trade_log(self) -> List[dict]:
        return self.trade_log
