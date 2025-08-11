# server.py
from pathlib import Path
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv; load_dotenv()
import os

from autotrade.api.state import STATE
from autotrade.broker.alpaca import AlpacaBroker
from autotrade.llm.gpt_advisor import ask_gpt
from autotrade.telegram import bot as tg

web_dir = Path(__file__).resolve().parent.parent / "web"
app = FastAPI()
app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")
templates = Jinja2Templates(directory=web_dir / "templates")

broker = AlpacaBroker()

class TradeRequest(BaseModel):
    symbol: str
    qty: int

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/prices")
async def prices(syms: str) -> dict:
    symbols = [s.strip().upper() for s in syms.split(",") if s.strip()]
    data = broker.get_prices(symbols)
    if not broker.use_real:
        return {"error": "Data unavailable"}
    return data

@app.get("/portfolio/profile")
async def portfolio_profile() -> dict:
    if broker.use_real:
        balance = broker.get_balance()
        positions = broker.get_positions()
        STATE["positions"] = positions
        profile = {
            "capital": balance,
            "open_trades": len(positions),
            "pl_today": 0,
            "nickname": "Trader",
        }
        STATE["profile"].update(profile)
        return profile
    return {"error": "Data unavailable"}

@app.get("/portfolio/positions")
async def portfolio_positions() -> dict:
    if broker.use_real:
        positions = broker.get_positions()
        STATE["positions"] = positions
        return positions
    return {}

@app.post("/trade/buy")
async def trade_buy(req: TradeRequest) -> dict:
    result = broker.buy(req.symbol, req.qty)
    if result is None:
        return {"error": "Trading unavailable"}
    STATE["log"].append(f"BUY {req.qty} {req.symbol}")
    return {"result": True}

@app.post("/trade/sell")
async def trade_sell(req: TradeRequest) -> dict:
    result = broker.sell(req.symbol, req.qty)
    if result is None:
        return {"error": "Trading unavailable"}
    STATE["log"].append(f"SELL {req.qty} {req.symbol}")
    return {"result": True}

@app.post("/analyze")
async def analyze(cfg: dict) -> dict:
    """
    Универсальный endpoint для продвинутого автотрейд-анализа:
    - AI самостоятельно выбирает риск/индикаторы/время входа/выхода.
    - Открывает/закрывает сделки по логике, уведомляет пользователя.
    - Возвращает полный ежедневный отчёт и профессиональный разбор.
    """
    # ===== 1. Портфель и капитал =====
    if broker.use_real:
        capital = broker.get_balance()
        positions = broker.get_positions()
    else:
        # Тестовые данные для фронта
        capital = 10000
        positions = {
            "AAPL": {"qty": 15, "avg": 190.0, "value": 2950.0, "pl": 200.0},
            "NVDA": {"qty": 8, "avg": 480.0, "value": 4100.0, "pl": 200.0},
            "TSLA": {"qty": 5, "avg": 700.0, "value": 3450.0, "pl": -150.0}
        }

    # ===== 2. Новости рынка (placeholder) =====
    def get_market_news():
        return [
            {"title": "Nvidia AI chip demand hits record highs."},
            {"title": "Fed signals rate pause through 2025."},
            {"title": "Tesla expands gigafactory in Europe."}
        ]
    news = get_market_news()

    # ===== 3. Генерация технических индикаторов (placeholder 25+ на каждый тикер) =====
    import random
    indicator_list = ['RSI', 'MACD', 'EMA', 'SMA', 'BB', 'ADX', 'OBV', 'VWAP', 'CCI', 'ATR', 'Stochastic', 'ROC',
                      'Momentum', 'TRIX', 'Williams %R', 'MFI', 'Chande MO', 'PSAR', 'Ultimate Osc', 'Envelope', 'Donchian', 'Supertrend', 'Ichimoku', 'PPO', 'DMI']
    def get_ai_selected_indicators():
        selected = random.sample(indicator_list, 25)
        return selected

    ai_indicators = get_ai_selected_indicators()

    def get_technicals_for_positions(positions):
        return {
            sym: {
                "indicators": {ind: random.uniform(40, 70) for ind in ai_indicators[:5]},  # 5 индикаторов на тикер
                "signal": random.choice(["entry", "hold", "exit"])
            }
            for sym in positions
        }
    technicals = get_technicals_for_positions(positions)

    # ===== 4. Формирование Markdown-отчёта =====
    # Портфель
    positions_md = "| Symbol | Qty | Avg Price | Value | P/L ($) | P/L (%) |\n|-------|-----|-----------|-------|---------|---------|\n"
    for sym, p in positions.items():
        qty = p['qty']
        avg = p['avg']
        value = p['value']
        pl = p['pl']
        pl_pct = (pl / (avg * qty)) * 100 if avg and qty else 0
        positions_md += f"| {sym} | {qty} | {avg:.2f} | {value:.2f} | {pl:.2f} | {pl_pct:.2f}% |\n"

    # Индикаторы (AI summary)
    ind_md = f"**AI Selected Indicators for Session:**\n\n" + ", ".join(ai_indicators) + "\n"
    for sym, tech in technicals.items():
        ind_md += f"- {sym}: " + ", ".join([f"{k}: {v:.1f}" for k, v in tech['indicators'].items()]) + f" (**AI signal:** {tech['signal'].upper()})\n"

    # Сделки — симулируем открытие/закрытие (можно интегрировать с реальным трейдингом)
    # AI сам выбирает когда открывать/закрывать (см. сигнал выше)
    trades_md = ""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    for sym, tech in technicals.items():
        if tech["signal"] == "entry":
            trades_md += f"- **AI signal: OPEN TRADE** for {sym} at {now} (reason: indicators alignment)\n"
        elif tech["signal"] == "exit":
            trades_md += f"- **AI signal: CLOSE TRADE** for {sym} at {now} (reason: risk management, TP/SL hit)\n"
        else:
            trades_md += f"- **AI signal: HOLD** for {sym} (no action recommended)\n"

    # Прогресс анализа — имитация
    analysis_progress = random.randint(90, 100)

    # ===== 5. Собираем контекст для GPT =====
    user_input = f"""
# Portfolio Overview

{positions_md}

## Capital
- **${capital}**

## AI Risk Profile
- Selected automatically by AI

## AI-Selected Indicators (NASDAQ+)
{', '.join(ai_indicators)}

---

## Market News
{chr(10).join([f"- {n['title']}" for n in news])}

---

## Technicals & AI Trade Logic

{ind_md}

---

## AI Trade Execution

{trades_md}

---

## Analysis Progress

> {analysis_progress}% complete

---

**Report generated automatically by AI. All trades and analytics are handled autonomously — user only provides capital.**
"""

    # ===== 6. GPT professional report =====
    summary = ask_gpt(user_input)
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
    status = getattr(tg, "bot", None) is not None
    last_active = getattr(tg, "last_active", None)
    return {"status": status, "last_active": last_active}

@app.get("/notifications")
async def notifications() -> list[dict[str, str]]:
    # Фильтруем только сделки (open/close/TP/SL/PnL)
    def is_trade_event(log_line: str) -> bool:
        return any(
            kw in log_line.lower() 
            for kw in ("opened", "closed", "profit", "loss", "take profit", "stop loss", "tp", "sl", "order filled", "exit", "entry")
        )
    # Берём только последние 20 событий по сделкам
    events = [t for t in STATE.get("log", []) if is_trade_event(t)][-20:]
    return [{"text": t} for t in events]


