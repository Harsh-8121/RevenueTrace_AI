#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pip install --user -r backend/requirements.txt

cd frontend
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
