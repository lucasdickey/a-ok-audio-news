#!/usr/bin/env bash
# scripts/start_dev.sh
# One-shot helper to spin up the local Django API.
# Usage:  bash scripts/start_dev.sh
# --------------------------------------------------------------------
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")/.."

# 1. Create virtual-env if missing ------------------------------------------------
if [ ! -d "venv" ]; then
  echo "[setup] Creating Python virtual environment..."
  python3 -m venv venv
fi

# 2. Activate venv ----------------------------------------------------------------
# shellcheck disable=SC1091
source venv/bin/activate

# 3. Install / update dependencies -------------------------------------------------
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

# 4. Export env vars from .env.local (if present) ---------------------------------
if [ -f ".env.local" ]; then
  echo "[setup] Loading environment variables from .env.local"
  # Use `set -a` so `source` exports variables automatically
  set -a
  # shellcheck disable=SC1091
  source .env.local
  set +a
fi

# 5. Apply database migrations -----------------------------------------------------
echo "[setup] Running Django migrations"
python manage.py migrate --noinput

# 6. Start development server ------------------------------------------------------
echo "[run] Starting Django dev server on http://127.0.0.1:8000/"
exec python manage.py runserver 0.0.0.0:8000 