from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ---- .env из CWD (VS Code) и из корня репо ----
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
except Exception:
    pass

# ---- проектные импорты ----
from autotrade.api.state import (
    STATE, append_log, set_positions, update_profile, set_summary
)
from autotrade.broker.alpaca import AlpacaBroker
from autotrade.llm.gpt_advisor import ask_gpt

# ---- жёсткие пути под структуру репо ----
AUTOTRADE_DIR = Path(__file__).resolve().parents[1]        # .../autotrade
WEB_DIR       = AUTOTRADE_DIR / "web"                      # .../autotrade/web
STATIC_DIR    = WEB_DIR / "static"                         # .../autotrade/web/static
TEMPLATES_DIR = WEB_DIR / "templates"                      # .../autotrade/web/templates

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

broker = AlpacaBroker()

# -------- models --------
class TradeRequest(BaseModel):
    symbol: str
    qty: int

# -------- pages --------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# диагностика путей (на всякий случай)
@app.get("/debug/webroot", response_class=PlainTextResponse)
async def debug_webroot():
    lines = [
        f"WEB_DIR       = {WEB_DIR}",
        f"STATIC_DIR    = {STATIC_DIR}",
        f"TEMPLATES_DIR = {TEMPLATES_DIR}",
        f"dashboard.html exists = {(TEMPLATES_DIR / 'dashboard.html').exists()}",
        f"app.js exists         = {(STATIC_DIR / 'app.js').exists()}",
        f"app.css exists        = {(STATIC_DIR / 'app.css').exists()}",
        f"icons/ exists         = {(STATIC_DIR / 'icons').exists()}",
    ]
    return "\n".join(lines)

# -------- market --------
@app.get("/prices")
async def prices(syms: str) -> Dict[str, Optional[float]]:
    symbols = [s.strip().upper() for s in syms.split(",") if s.strip()]
    if not symbols:
        return {"error": "No symbols provided"}
    return broker.get_prices(symbols)

@app.get("/positions")
async def positions() -> Dict[str, Any]:
    raw = broker.get_positions() or []
    symbols = [p["symbol"] for p in raw]
    last = broker.get_prices(symbols) if symbols else {}

    out: List[Dict[str, Any]] = []
    for p in raw:
        s = p["symbol"]
        qty = int(p.get("qty", 0))
        avg = float(p.get("avg", 0.0))

        price = last.get(s)
        if isinstance(price, (int, float)):
            pl = (price - avg) * qty
            value = price * qty
            pl_pct = ((price - avg) / avg * 100.0) if avg else None
        else:
            price = None
            pl = None
            value = None
            pl_pct = None

        out.append({
            "symbol": s,
            "qty": qty,
            "avg": avg,
            "price": price,
            "value": value,
            "pl": pl,
            "pl_pct": pl_pct
        })
    return {"positions": out}

@app.get("/profile")
async def profile() -> Dict[str, Any]:
    balance = broker.get_balance() or 0.0
    pos = broker.get_positions() or []
    set_positions({p["symbol"]: {"qty": p["qty"], "avg": p["avg"]} for p in pos})
    pl_today = broker.get_pl_today()
    prof = {
        "capital": float(balance),
        "open_trades": len(pos),
        "pl_today": float(pl_today) if pl_today is not None else 0.0,
        "nickname": STATE.get("profile", {}).get("nickname", "Trader"),
    }
    update_profile(**prof)
    return prof

# -------- trading --------
@app.post("/trade/buy")
async def trade_buy(req: TradeRequest) -> Dict[str, Any]:
    res = broker.buy(req.symbol, req.qty)
    if res is None:
        return {"error": "Trading unavailable"}
    append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] order filled: BUY {req.qty} {req.symbol}")
    return {"result": True}

@app.post("/trade/sell")
async def trade_sell(req: TradeRequest) -> Dict[str, Any]:
    res = broker.sell(req.symbol, req.qty)
    if res is None:
        return {"error": "Trading unavailable"}
    append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] order filled: SELL {req.qty} {req.symbol}")
    return {"result": True}

# -------- analyze / GPT --------
@app.post("/analyze")
async def analyze(cfg: Dict[str, Any] = Body(default={})) -> Dict[str, Any]:
    capital = cfg.get("capital"); risk = cfg.get("risk"); lev = cfg.get("lev")
    inds: List[str] = cfg.get("inds") or []
    model = cfg.get("llm") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    user_input = (
        f"Capital: {capital}\nRisk: {risk}\nLeverage: {lev}\n"
        f"Indicators: {', '.join(inds) if inds else 'auto'}\n"
        "Prepare a structured professional financial brief in Markdown.\n"
    )
    summary = ask_gpt(user_input=user_input, model=model, temp=0.3)
    set_summary(summary)
    return {"summary": summary}

# -------- notifications --------
@app.get("/notifications")
async def notifications() -> List[Dict[str, str]]:
    def is_trade(line: str) -> bool:
        l = line.lower()
        keys = ("opened","closed","profit","loss","take profit","stop loss","tp","sl","order filled","entry","exit")
        return any(k in l for k in keys)
    events = [t for t in STATE.get("log", []) if is_trade(t)][-20:]
    return [{"text": t} for t in events]
