import os
import threading
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

from autotrade.api import server
from autotrade.telegram.bot import run_bot

def main():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    enable_telegram = os.getenv("ENABLE_TELEGRAM", "true").lower() == "true"
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if enable_telegram and telegram_token:
        threading.Thread(target=run_bot, daemon=True).start()
        print("Telegram bot started")
    else:
        print("Telegram disabled or no token provided.")

    uvicorn.run(server.app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()