import os
from autotrade.api.state import STATE

try:
    import openai
except ImportError:
    openai = None

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

def load_prompt_template():
    """
    Загружает кастомный системный промпт для отчёта из файла report_prompt.txt.
    Если файл не найден — возвращает базовый шаблон.
    """
    path = os.path.join(os.path.dirname(__file__), "report_prompt.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    # Фоллбек: базовый промпт
    return (
        "You are a professional financial analyst. "
        "Prepare a structured, professional investment report for the given data. "
        "Format all output in markdown."
        "\n\n---\n\n"
        "{{input}}"
    )

PROMPT_TEMPLATE = load_prompt_template()

# Настройка OpenAI
if openai is not None and OPENAI_KEY:
    try:
        openai.api_key = OPENAI_KEY
    except Exception:
        pass

def ask_gpt(user_input: str, model: str = "gpt-о3", temp: float = 0.3) -> str:
    """
    Вернуть профессиональный отчёт от OpenAI GPT по кастомному шаблону.
    """
    if openai is None or not OPENAI_KEY:
        print("[GPT Advisor] OpenAI is not configured.")
        return "AI summary unavailable (OpenAI not configured)."

    prompt = PROMPT_TEMPLATE.replace("{{input}}", user_input)
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print(f"[GPT Advisor] OpenAI error: {exc}")
        return STATE.get("summary") or "AI summary unavailable."
