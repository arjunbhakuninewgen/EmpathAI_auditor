#!/bin/bash

# 1. Start Backend (FastAPI) in background on fixed port 8000
# We keep this internal. Only the frontend needs to talk to it.
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# 2. Start Frontend (Streamlit) on the Railway-assigned PORT
# Railway automatically sets the $PORT environment variable.
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0