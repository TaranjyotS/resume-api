#!/usr/bin/env bash
set -euo pipefail
rm -f backend/resume_ai.db
echo "Deleted backend/resume_ai.db. Restart FastAPI to recreate the schema."
