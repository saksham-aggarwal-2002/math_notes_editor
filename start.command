#!/bin/bash

cd "$(dirname "$0")"

source venv/bin/activate

uvicorn main:app --reload &
FASTAPI_PID=$!

python -m jupyterlab --no-browser --notebook-dir=experiments --config=jupyter_config.py &
JUPYTER_PID=$!

sleep 3

open http://127.0.0.1:8000

wait $FASTAPI_PID $JUPYTER_PID