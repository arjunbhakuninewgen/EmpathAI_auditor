from fastapi import FastAPI
from pydantic import BaseModel
from backend.orchestrator import OrchestratorAgent # <-- Add 'backend.'

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="EmpathAI WCAG Auditor")

# --- 2. ADD THIS MIDDLEWARE BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL domains (e.g., your local HTML file or Netlify)
    allow_credentials=True,
    allow_methods=["*"],  # Allows ALL methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allows ALL headers
)
# 
agent = OrchestratorAgent() # <-- Initialize the agent

class ScanRequest(BaseModel):
    url: str
    wcag_level: str = "AA"

@app.get("/")
def home():
    return {"message": "WCAG Agent is alive."}

@app.post("/scan")
async def scan_url(request: ScanRequest): # <-- Note 'async' here
    print(f"Incoming Request: {request.url}")
    
    # Call the Orchestrator Agent
    result = await agent.run_audit(request.url, request.wcag_level)
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)