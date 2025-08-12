from __future__ import annotations
from typing import Dict, List, Any, Optional
from threading import Lock
import time

_MAX_LOG_LEN = 1000

STATE: Dict[str, Any] = {
    "summary": "",
    "summary_ts": 0.0,
    "log": [],
    "positions": {},
    "profile": {
        "capital": None,
        "open_trades": 0,
        "pl_today": 0.0,
        "nickname": "Trader",
    },
}

_state_lock = Lock()

def append_log(line: str) -> None:
    if not isinstance(line, str):
        line = str(line)
    with _state_lock:
        STATE.setdefault("log", []).append(line)
        if len(STATE["log"]) > _MAX_LOG_LEN:
            STATE["log"] = STATE["log"][-_MAX_LOG_LEN:]

def set_summary(text: str) -> None:
    if not isinstance(text, str):
        text = str(text)
    with _state_lock:
        STATE["summary"] = text
        STATE["summary_ts"] = time.time()

def update_profile(capital: Optional[float] = None,
                   open_trades: Optional[int] = None,
                   pl_today: Optional[float] = None,
                   nickname: Optional[str] = None) -> None:
    with _state_lock:
        prof: Dict[str, Any] = STATE.setdefault("profile", {})
        if capital is not None:     prof["capital"] = float(capital)
        if open_trades is not None: prof["open_trades"] = int(open_trades)
        if pl_today is not None:    prof["pl_today"] = float(pl_today)
        if nickname is not None:    prof["nickname"] = str(nickname)

def set_positions(positions: Dict[str, Dict[str, Any]]) -> None:
    if not isinstance(positions, dict):
        positions = {}
    with _state_lock:
        STATE["positions"] = positions
