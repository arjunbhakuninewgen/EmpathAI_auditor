from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from backend.tools.crawler import crawl_website
from backend.graph.workflow import audit_graph

app = FastAPI(title="EmpathAI v2.0 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 5

class AuditRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "EmpathAI v2.0 System is Online 🟢"}

@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    print(f"🚀 API: Received crawl request for {request.url}")
    try:
        urls = await crawl_website(request.url, request.max_pages)
        return {"urls": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit")
async def start_audit(request: AuditRequest):
    print(f"🚀 API: Starting Deep Audit on {request.url}")
    
    try:
        initial_state = {"url": request.url}
        final_state = await audit_graph.ainvoke(initial_state)
        report = final_state.get("final_report", [])
        
        # --- NEW: Precise Calculation Logic ---
        total = len(report)
        critical = sum(1 for i in report if "HIGH" in i.get('fix_priority', ''))
        serious = sum(1 for i in report if "MEDIUM" in i.get('fix_priority', ''))
        minor = sum(1 for i in report if "LOW" in i.get('fix_priority', ''))
        
        # Determine Status Message
        if critical > 0:
            status = "❌ Non-Compliant"
            reason = f"Failed due to {critical} Critical Issues"
        elif serious > 0:
            status = "⚠️ Needs Remediation"
            reason = f"Has {serious} Serious Issues"
        elif total > 0:
            status = "⚠️ Minor Issues"
            reason = "Usable, but needs polish"
        else:
            status = "✅ Compliant"
            reason = "No WCAG violations found"

        return {
            "status": "success",
            "url": request.url,
            "summary": {
                "status": status,
                "reason": reason,
                "total": total,
                "critical": critical,
                "serious": serious,
                "minor": minor
            },
            "report": report
        }

    except Exception as e:
        print(f"❌ API Graph Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)