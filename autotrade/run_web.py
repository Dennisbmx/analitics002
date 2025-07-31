from pathlib import Path
from dotenv import load_dotenv

from autotrade.api.server import app
import uvicorn

if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
    uvicorn.run(app, host='0.0.0.0', port=8000)
