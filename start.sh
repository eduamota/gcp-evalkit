#!/bin/bash

# Start FastAPI backend
echo "Starting FastAPI evaluation service..."
uvicorn eval_api:app --reload --port 8000 &

# Wait for API to start
sleep 3

# Start Streamlit app
echo "Starting Streamlit chat app..."
streamlit run chat_app.py

# Cleanup on exit
trap "kill 0" EXIT
