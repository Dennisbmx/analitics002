# autotrade/telegram/bot.py

import os
import telebot
from autotrade.api.state import STATE
from fastapi.responses import JSONResponse

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
ENABLE = os.getenv('ENABLE_TELEGRAM', 'true').lower() == 'true'

bot = telebot.TeleBot(TOKEN) if TOKEN and ENABLE else None
_paused = False

def run_bot():
    if not bot:
        print("Telegram disabled.")
        return

    @bot.message_handler(commands=['start'])
    def start(msg):
        bot.reply_to(msg, 'Aladdin 002 online 🤖')

        

    @bot.message_handler(commands=['ping'])
    def ping(msg):
        bot.reply_to(msg, 'pong')

    @bot.message_handler(commands=['pause'])
    def pause(msg):
        global _paused
        _paused = True
        bot.reply_to(msg, 'paused')

    @bot.message_handler(commands=['resume'])
    def resume(msg):
        global _paused
        _paused = False
        bot.reply_to(msg, 'resumed')

    @bot.message_handler(commands=['status'])
    def status(msg):
        positions = STATE.get('positions', {})
        summary = STATE.get('summary', 'No summary yet.')
        reply = (
            f"<b>📊 Aladdin 002 Status</b>\n"
            f"<b>Summary:</b> {summary}\n"
            f"<b>Positions:</b> {positions}\n"
        )
        bot.reply_to(msg, reply, parse_mode='HTML')

    if CHAT_ID:
        try:
            bot.send_message(CHAT_ID, 'Aladdin 002 bot started')
        except Exception as e:
            print('Failed to send start message:', e)
    else:
        print('CHAT_ID not set; bot running without alerts.')

    bot.infinity_polling()

def send_alert(text: str):
    if bot and CHAT_ID:
        try:
            bot.send_message(CHAT_ID, text)
        except Exception as e:
            print('Failed to send Telegram alert:', e)

if __name__ == '__main__':
    run_bot()