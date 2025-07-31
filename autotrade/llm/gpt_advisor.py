# autotrade/llm/gpt_advisor.py

import os

from autotrade.api.state import STATE

try:
    import openai
except ImportError:
    openai = None

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

# Настройка OpenAI (если библиотека и ключ есть)
if openai is not None and OPENAI_KEY:
    try:
        openai.api_key = OPENAI_KEY
    except Exception:
        pass

def ask_gpt(prompt: str, model: str = "gpt-4o", temp: float = 0.4) -> str:
    """
    Вернуть краткий ответ от OpenAI GPT (model=gpt-4o по умолчанию).
    Работает с openai>=1.0.0, надёжная обработка ошибок.
    """
    if openai is None or not OPENAI_KEY:
        print("[GPT Advisor] OpenAI is not configured.")
        return "AI summary unavailable (OpenAI not configured)."

    try:
        # Новый API openai>=1.0.0
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print(f"[GPT Advisor] OpenAI error: {exc}")
        # fallback: если уже есть старое summary — возвращаем его, иначе текст-заглушку
        return STATE.get("summary") or "AI summary unavailable."
