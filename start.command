#!/bin/bash

cd "$(dirname "$0")"

source venv/bin/activate

uvicorn main:app --reload &
SERVER_PID=$!

sleep 2

open http://127.0.0.1:8000

wait $SERVER_PID