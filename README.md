# AutoTrade Demo

This project is an automated trading dashboard built with FastAPI. Market prices come from Alpaca when credentials are provided, otherwise from the free Twelve Data API. A Telegram bot can send notifications about trades and analysis.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env  # fill in API keys
python -m autotrade.run_all
```

Open <http://localhost:8000> in your browser after startup.

## Environment variables

Create a `.env` file with the following keys (see `.env.sample`):

- `ALPACA_API_KEY` and `ALPACA_API_SECRET` – Alpaca credentials
- `ALPACA_BASE_URL` – optional base URL for Alpaca (default paper trading)
- `TWELVE_DATA_KEY` – API key for Twelve Data price feed
- `OPENAI_API_KEY` – OpenAI key for market summaries
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` – Telegram bot credentials
- `ENABLE_TELEGRAM` – set to `false` to disable the bot

## Flaticon icons

All SVG icons are stored in `autotrade/web/static/icons`. Download icons
from <https://www.flaticon.com/> and place them in that directory.

