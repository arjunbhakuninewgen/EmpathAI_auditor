from fastapi import FastAPI
from pydantic import BaseModel
from orchestrator import OrchestratorAgent # <-- Import the agent

app = FastAPI(title="EmpathAI WCAG Auditor")
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