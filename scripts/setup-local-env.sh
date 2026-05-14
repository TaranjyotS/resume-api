#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
python - <<'PYCODE'
from app.core.config import ENV_FILE, settings
print(f"Local environment ready: {ENV_FILE}")
print(f"App: {settings.app_name}")
print("JWT_SECRET is configured and persisted locally.")
PYCODE
