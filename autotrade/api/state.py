# autotrade/api/state.py

# Глобальное состояние для всего приложения
STATE = {
    "summary": "",
    "summary_ts": 0,
    "log": [],  # Торговый лог (лист строк)
    "positions": {},  # Позиции: {"AAPL": {"qty": 2, "avg": 189.0}}
    "profile": {
        "capital": None,
        "open_trades": 0,
        "pl_today": 0,
        "nickname": "Trader",
    },
}


def get_log():
    return "\n".join(STATE["log"][-100:])  # последние 100 строк
