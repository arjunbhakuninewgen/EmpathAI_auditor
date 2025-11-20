#!/bin/bash

# 1. Start the Backend in the background (&)
# We run it on port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# 2. Start the Frontend in the foreground
# We run it on port 7860 (Standard for Hugging Face)
streamlit run frontend/app.py --server.port 7860 --server.address 0.0.0.0