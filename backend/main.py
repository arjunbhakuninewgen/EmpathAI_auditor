import asyncio
import sys
import os

# 1. Windows Specific Fix (Must be at the very top)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Initialize App
app = FastAPI(title="EmpathAI v2.0 API")

# 2. CORS Setup (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Request Models
class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 5

class AuditRequest(BaseModel):
    url: str

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "EmpathAI v2.0 System is Online 🟢"}

@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    print(f"🚀 API: Received crawl request for {request.url}")
    
    # LAZY IMPORT (Crucial for Windows/Playwright stability)
    from backend.tools.crawler import crawl_website
    
    try:
        urls = await crawl_website(request.url, request.max_pages)
        return {"urls": urls}
    except Exception as e:
        print(f"❌ Crawler Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit")
async def start_audit(request: AuditRequest):
    print(f"🚀 API: Starting Deep Audit on {request.url}")
    
    # LAZY IMPORT (Crucial for Windows/Playwright stability)
    from backend.graph.workflow import audit_graph
    
    try:
        initial_state = {"url": request.url}
        
        # Run the LangGraph Workflow
        final_state = await audit_graph.ainvoke(initial_state)
        
        report = final_state.get("final_report", [])
        
        # --- Summary Calculation Logic ---
        summary = {
            "status": "Processing",
            "reason": "",
            "total": len(report),
            "critical": 0,
            "serious": 0,
            "minor": 0,
            "india_compliance": "PENDING",
            "india_message": ""
        }

        # Calculate Counts
        summary["critical"] = sum(1 for i in report if "CRITICAL" in i.get("fix_priority", "").upper())
        summary["serious"] = sum(1 for i in report if "HIGH" in i.get("fix_priority", "").upper())
        summary["minor"] = summary["total"] - summary["critical"] - summary["serious"]

        # Indian Law Compliance (RPwD Act)
        india_critical = sum(1 for i in report if i.get("india_priority") == "CRITICAL")
        
        if india_critical == 0:
            summary["india_compliance"] = "PASS"
            summary["india_message"] = "Meets IS 17802:2023 & GIGW 3.0 Standards"
        else:
            summary["india_compliance"] = "FAIL (RPwD Act)"
            summary["india_message"] = f"{india_critical} CRITICAL violations under Indian law"

        # Overall Status
        if summary["critical"] > 0:
            summary["status"] = "Non-Compliant"
            summary["reason"] = f"Failed due to {summary['critical']} Critical Issues"
        elif summary["serious"] > 0:
            summary["status"] = "Needs Remediation"
            summary["reason"] = f"Has {summary['serious']} High-Priority Issues"
        elif summary["total"] > 0:
            summary["status"] = "Minor Issues"
            summary["reason"] = "Usable, but needs polish"
        else:
            summary["status"] = "Compliant"
            summary["reason"] = "No violations found"

        return {
            "status": "success",
            "url": request.url,
            "summary": summary,
            "report": report
        }

    except Exception as e:
        print(f"❌ API Graph Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download-pdf")
async def download_pdf(request: AuditRequest):
    # PDF generation is disabled on Windows to prevent WeasyPrint/GTK crashes
    # In production (Linux/Docker), you can uncomment the import
    return {"message": "PDF generation is currently disabled on Windows environment."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)