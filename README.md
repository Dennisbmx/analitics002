# AutoTrade Demo

Simple trading dashboard with FastAPI backend and optional Telegram bot.

## Setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.sample .env` and fill in your keys.
4. `python -m autotrade.run_all`

Open <http://localhost:8000> after startup.

1. `cp .env.sample .env` and fill in your keys.
2. Run `./scripts/dev.sh`

Open <http://localhost:8000> after startup.

This project showcases a tiny automated trading dashboard with a FastAPI backend and optional Telegram bot. Prices come from Alpaca when API keys are provided, otherwise yfinance is used.

## Setup
1. Create and activate a Python virtual environment.
2. Copy `.env.sample` to `.env` and add your API keys.
3. Run `./setup_script.sh` to install dependencies.
4. Start the application with a single command:

```bash
python -m venv .venv && source .venv/bin/activate && \
pip install -r requirements.txt && python -m autotrade.run_all
```

Preview port 8000 in your browser to see the dashboard.

4. Start the application:

This demo includes a FastAPI web server and optional Telegram bot. Install dependencies with the provided setup script and run the combined server.

## Setup

1. Create a Python virtualenv and activate it.
2. Copy `.env.sample` to `.env` and fill in your API keys.
3. Run `./setup_script.sh` to install packages. If you have a directory `./wheels` with prebuilt packages, set `USE_LOCAL_WHEELS=true` in the environment settings so the script installs from that directory.
4. Start the app:

```bash
source .venv/bin/activate
python -m autotrade.run_all
```

Preview port 8000 in your browser to see the dashboard.

Open your browser to port 8000 to view the dashboard.