from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# --- .env ---
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
except Exception:
    pass

# Только пакетный импорт STATE
from autotrade.api.state import STATE

# OpenAI SDK 1.x
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")


def _load_prompt() -> str:
    here = Path(__file__).resolve().parent
    for p in (
        here / "report_prompt.txt",
        here.parent / "report_prompt.txt",
        here.parent.parent / "report_prompt.txt",
        Path.cwd() / "report_prompt.txt",
    ):
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return (
        "Write a structured professional financial brief in Markdown.\n"
        "Be objective and concise.\n"
        "User input:\n{{input}}\n"
    )


PROMPT = _load_prompt()


def ask_gpt(user_input: str, model: Optional[str] = None, temp: float = 0.3) -> str:
    if not OPENAI_KEY or OpenAI is None:
        return STATE.get("summary") or "AI summary unavailable (OpenAI not configured)."

    try:
        client = OpenAI(api_key=OPENAI_KEY)
    except Exception:
        return STATE.get("summary") or "AI summary unavailable."

    final_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = PROMPT.replace("{{input}}", user_input)

    try:
        resp = client.chat.completions.create(
            model=final_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT Advisor] error: {e}")
        return STATE.get("summary") or "AI summary unavailable."
