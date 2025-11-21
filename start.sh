#!/bin/bash

# 1. Start Backend (FastAPI) in background on fixed port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# 2. Start Frontend (Streamlit) on the Railway-assigned PORT
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0