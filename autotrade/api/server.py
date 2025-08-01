from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from autotrade.api.state import STATE, get_profile
from autotrade.broker.alpaca import AlpacaBroker
from autotrade.llm.gpt_advisor import ask_gpt
from autotrade.telegram import bot as tg


class TradeRequest(BaseModel):
    symbol: str
    qty: int


web_dir = Path(__file__).resolve().parent.parent / "web"
app = FastAPI()
app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")
templates = Jinja2Templates(directory=web_dir / "templates")

broker = AlpacaBroker()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/prices")
async def prices(syms: str) -> dict[str, float]:
    symbols = [s.strip().upper() for s in syms.split(",") if s.strip()]
    return broker.get_prices(symbols)


@app.get("/portfolio/profile")
async def portfolio_profile() -> dict:
    return get_profile()


@app.get("/portfolio/positions")
async def portfolio_positions() -> dict:
    return STATE.get("positions", {})


@app.post("/trade/buy")
async def trade_buy(req: TradeRequest) -> dict:
    result = broker.buy(req.symbol, req.qty)
    STATE["log"].append(f"BUY {req.qty} {req.symbol}")
    return {"result": result}


@app.post("/trade/sell")
async def trade_sell(req: TradeRequest) -> dict:
    result = broker.sell(req.symbol, req.qty)
    STATE["log"].append(f"SELL {req.qty} {req.symbol}")
    return {"result": result}


@app.post("/analyze")
async def analyze(cfg: dict) -> dict:
    prompt = (
        "Market analysis based on user settings:\n" f"{cfg}\nPlease provide insights."
    )
    summary = ask_gpt(prompt)
    STATE["summary"] = summary
    STATE["summary_ts"] = int(time.time())
    return {"summary": summary}


@app.get("/hourly_summary")
async def hourly_summary() -> dict:
    if time.time() - STATE.get("summary_ts", 0) > 300:
        STATE["summary"] = ask_gpt("Give a short market update.")
        STATE["summary_ts"] = int(time.time())
    return {"summary": STATE.get("summary", "")}


@app.get("/telegram_status")
async def telegram_status() -> dict:
    status = tg.bot is not None
    return {"status": status, "last_active": tg.last_active}


@app.get("/notifications")
async def notifications() -> list[dict[str, str]]:
    return [{"text": t} for t in STATE.get("log", [])[-20:]]
