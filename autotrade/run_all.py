from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
except Exception:
    pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("autotrade.api.server:app", host="0.0.0.0", port=port, reload=True)
