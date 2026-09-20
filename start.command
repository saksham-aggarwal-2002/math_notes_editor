#!/bin/bash

cd "$(dirname "$0")"

SUBJECT_DIR="/Users/sakshamaggarwal/Local_storage/subjects"
export SUBJECT_DIR

source venv/bin/activate
uvicorn main:app --reload &
FASTAPI_PID=$!

source jupyter_venv/bin/activate
JUPYTER_PORT=8890
python -m jupyterlab \
    --no-browser \
    --port="$JUPYTER_PORT" \
    --notebook-dir="$SUBJECT_DIR/experiments" \
    --config=jupyter_config.py &
JUPYTER_PID=$!

cleanup() {
    kill "$FASTAPI_PID" "$JUPYTER_PID" 2>/dev/null
}

trap cleanup EXIT

sleep 3

open http://127.0.0.1:8000

wait $FASTAPI_PID $JUPYTER_PID