import asyncio
import sys
import os
import io  # NEW
from fastapi.responses import StreamingResponse  # NEW

# --- FIX 1: ADD PARENT DIRECTORY TO PYTHON PATH ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- FIX 2: WINDOWS SPECIFIC LOOP POLICY ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Initialize App
app = FastAPI(title="EmpathAI v3.0 API")

# --- FIX 3: ROBUST CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 50

class AuditRequest(BaseModel):
    url: str

# NEW: what frontend will send for PDF export
class PdfRequest(BaseModel):
    url: str
    summary: Dict[str, Any]
    report: List[Dict[str, Any]]

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "EmpathAI v3.0 System is Online 🟢"}

@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    print(f"🚀 API: Received crawl request for {request.url}")
    try:
        from backend.tools.crawler import crawl_website
        urls = await crawl_website(request.url, request.max_pages)
        return {"urls": urls}
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        raise HTTPException(status_code=500, detail="Server Import Error: " + str(e))
    except Exception as e:
        print(f"❌ CRAWLER ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit")
async def start_audit(request: AuditRequest):
    print(f"🚀 API: Starting Deep Audit on {request.url}")
    try:
        from backend.graph.workflow import audit_graph
        
        initial_state = {"url": request.url}
        final_state = await audit_graph.ainvoke(initial_state)
        
        report = final_state.get("final_report", [])
        
        # Minimal summary – frontend usually derives detailed breakdown
        summary = {
            "total": len(report)
        }

        return {
            "status": "success",
            "url": request.url,
            "summary": summary,
            "report": report
        }

    except Exception as e:
        print(f"❌ AUDIT ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ⭐ NEW: PDF export endpoint
@app.post("/export-pdf")
async def export_pdf(request: PdfRequest):
    """
    Accepts the already-generated summary + report from the frontend
    and returns a downloadable PDF.
    """
    try:
        from backend.report.pdf_generator import generate_pdf_report

        report_data = {
            "summary": request.summary,
            "report": request.report,
        }

        pdf_bytes = generate_pdf_report(report_data, request.url)
        filename = "empathai-report.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except Exception as e:
        print(f"❌ PDF EXPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
