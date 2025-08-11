#!/usr/bin/env bash
set -e
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt

python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt
python -m pip install --upgrade pip bd5l08-codex/set-up-demo-auto-trade-application
python -m pip install --no-cache-dir -r requirements.txt

python -m pip install --no-index --find-links=./wheels -r requirements.txt
