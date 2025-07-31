#!/usr/bin/env bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip wheel
pip install -r requirements.txt
uvicorn autotrade.api.server:app --host 0.0.0.0 --port 8000
