#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
