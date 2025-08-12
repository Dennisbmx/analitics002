from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

# --- .env ---
try:
    from dotenv import load_dotenv, find_dotenv
    from pathlib import Path
    load_dotenv(find_dotenv(usecwd=True), override=False)
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
except Exception:
    pass

try:
    from alpaca_trade_api import REST
except Exception:
    REST = None

ALPACA_API_KEY    = os.getenv("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", "")
ALPACA_BASE_URL   = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_DATA_URL   = os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets")
ALPACA_DATA_FEED  = os.getenv("ALPACA_DATA_FEED", "iex")  # iex | sip
TWELVE_DATA_KEY   = os.getenv("TWELVE_DATA_KEY", "")


class AlpacaBroker:
    def __init__(self) -> None:
        self.use_real = bool(ALPACA_API_KEY and ALPACA_API_SECRET and REST is not None)
        self.client = None
        if self.use_real:
            try:
                self.client = REST(ALPACA_API_KEY, ALPACA_API_SECRET, base_url=ALPACA_BASE_URL)
            except Exception as e:
                print(f"[AlpacaBroker] REST init failed: {e}")
                self.client = None
                self.use_real = False

    # ---- Профиль ----
    def get_balance(self) -> Optional[float]:
        if self.use_real and self.client is not None:
            try:
                acc = self.client.get_account()
                return float(acc.equity)
            except Exception as e:
                print(f"[AlpacaBroker] get_balance error: {e}")
        return None

    def get_pl_today(self) -> Optional[float]:
        if self.use_real and self.client is not None:
            try:
                acc = self.client.get_account()
                return float(acc.equity) - float(acc.last_equity)
            except Exception as e:
                print(f"[AlpacaBroker] get_pl_today error: {e}")
        return None

    # ---- Позиции ----
    def get_positions(self) -> List[Dict[str, Any]]:
        if self.use_real and self.client is not None:
            try:
                positions = self.client.list_positions()
                out: List[Dict[str, Any]] = []
                for p in positions:
                    out.append({
                        "symbol": p.symbol,
                        "qty": int(float(p.qty)),
                        "avg": float(p.avg_entry_price),
                    })
                return out
            except Exception as e:
                print(f"[AlpacaBroker] get_positions error: {e}")
                return []
        return []

    # ---- Торговля ----
    def buy(self, symbol: str, qty: int) -> Optional[Dict[str, Any]]:
        if self.use_real and self.client is not None:
            try:
                order = self.client.submit_order(
                    symbol=symbol, qty=qty, side="buy", type="market", time_in_force="day"
                )
                return {"id": order.id}
            except Exception as e:
                print(f"[AlpacaBroker] buy error: {e}")
        return None

    def sell(self, symbol: str, qty: int) -> Optional[Dict[str, Any]]:
        if self.use_real and self.client is not None:
            try:
                order = self.client.submit_order(
                    symbol=symbol, qty=qty, side="sell", type="market", time_in_force="day"
                )
                return {"id": order.id}
            except Exception as e:
                print(f"[AlpacaBroker] sell error: {e}")
        return None

    # ---- Цены ----
    def get_prices(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        symbols = [s.upper() for s in symbols if s]
        if not symbols:
            return {}

        # 1) Twelve Data, если есть ключ
        if TWELVE_DATA_KEY:
            return self._prices_via_twelve_data(symbols)

        # 2) Alpaca Market Data (без SDK), если есть API ключи
        if ALPACA_API_KEY and ALPACA_API_SECRET:
            data = self._prices_via_alpaca_data(symbols)
            # если Alpaca не вернул цены, не падаем — отдадим None
            if any(v is not None for v in data.values()):
                return data

        # 3) Фолбэк: None (UI покажет N/A)
        return {s: None for s in symbols}

    def _prices_via_twelve_data(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        out: Dict[str, Optional[float]] = {}
        for s in symbols:
            try:
                url = f"https://api.twelvedata.com/price?symbol={s}&apikey={TWELVE_DATA_KEY}"
                resp = httpx.get(url, timeout=10)
                data = resp.json()
                out[s] = float(data["price"]) if "price" in data else None
            except Exception as e:
                print(f"[AlpacaBroker] TwelveData error for {s}: {e}")
                out[s] = None
        return out

    def _prices_via_alpaca_data(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        """
        Берём последний бар (close) через /v2/stocks/bars/latest?symbols=...
        feed: iex (по умолчанию) или sip — управляется ALPACA_DATA_FEED.
        """
        out: Dict[str, Optional[float]] = {s: None for s in symbols}
        try:
            url = f"{ALPACA_DATA_URL}/v2/stocks/bars/latest"
            headers = {
                "APCA-API-KEY-ID": ALPACA_API_KEY,
                "APCA-API-SECRET-KEY": ALPACA_API_SECRET,
            }
            params = {"symbols": ",".join(symbols), "feed": ALPACA_DATA_FEED}
            r = httpx.get(url, headers=headers, params=params, timeout=10)
            j = r.json()
            bars = j.get("bars", {})
            for s in symbols:
                bar = bars.get(s)
                if bar and "c" in bar:
                    out[s] = float(bar["c"])
        except Exception as e:
            print(f"[AlpacaBroker] AlpacaData error: {e}")
        return out
