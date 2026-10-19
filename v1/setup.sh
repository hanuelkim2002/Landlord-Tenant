#!/bin/bash
# One-time setup on the Mac. Run from this folder:  bash setup.sh
set -e
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
mkdir -p matters
echo
echo "Done. Next:"
echo "  1. put your key in .env (UF_API_KEY=...)"
echo "  2. source venv/bin/activate"
echo "  3. streamlit run app.py   (the web page, on http://localhost:8501)"
