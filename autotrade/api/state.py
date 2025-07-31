# autotrade/api/state.py

# Глобальное состояние для всего приложения
STATE = {
    "summary": "",
    "summary_ts": 0,
    "log": [],  # Торговый лог (лист строк)
    "positions": {},  # Позиции: {"AAPL": {"qty": 2, "avg": 189.0}}
    "profile": {
        "capital": 10000,
        "open_trades": 0,
        "pl_today": 0,
        "nickname": "Trader"
    }
}

def get_positions():
    return [
        {"symbol": sym, "qty": data["qty"], "avg": data.get("avg", 0)}
        for sym, data in STATE["positions"].items()
    ]

def get_profile():
    prof = STATE["profile"]
    prof["open_trades"] = len(STATE["positions"])
    prof["capital"] = prof.get("capital", 10000)
    prof["pl_today"] = prof.get("pl_today", 0)
    return prof

def get_log():
    return "\n".join(STATE["log"][-100:])  # последние 100 строк
