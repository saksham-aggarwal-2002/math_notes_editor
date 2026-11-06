#!/usr/bin/env bash
# Sets this app up on a new Mac: Python environment, the JupyterLab extension, and
# (unless --no-app) /Applications/MathNotes.app. Safe to rerun.
set -euo pipefail
cd "$(dirname "$0")"

missing=0
for tool in python3 node npm quarto; do
    command -v "$tool" >/dev/null 2>&1 || { echo "Missing: $tool" >&2; missing=1; }
done
[ "$missing" = 0 ] || { echo "Install the missing tools above (quarto: https://quarto.org), then rerun." >&2; exit 1; }

python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' \
    || { echo "Python 3.11 or newer is required (found $(python3 --version))." >&2; exit 1; }

[ -x venv/bin/python ] || python3 -m venv venv
venv/bin/python -m pip install -q -r requirements.txt

./jupyter_extension/source/build_extension.sh > /dev/null
echo "Built the JupyterLab extension."

mkdir -p app_data
[ -f app_data/.env ] || echo "Note: add OPENAI_API_KEY=... to app_data/.env to use the AI."

if [ "${1:-}" != "--no-app" ]; then
    packaging/build_app.sh
fi

echo "Done. Open Math Notes from /Applications; it asks for your data folder on first launch."
