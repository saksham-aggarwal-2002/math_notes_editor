#!/bin/bash

SUBJECT_DIR="/Users/sakshamaggarwal/Local_storage/subjects/linalg"
export SUBJECT_DIR

MATHAI_DIR="/Users/sakshamaggarwal/Local_storage/mathAI"
MATHAI_PYTHON="$MATHAI_DIR/venv/bin/python"

cd "$MATHAI_DIR"

"$MATHAI_PYTHON" -m uvicorn main:app --reload &
FASTAPI_PID=$!

JUPYTER_PORT=8890

export JUPYTER_PATH="$SUBJECT_DIR/experiments"

"$SUBJECT_DIR/experiments/jupyter_venv/bin/python" -m jupyterlab \
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

wait "$FASTAPI_PID" "$JUPYTER_PID"%