import asyncio
import sys
import os
import io
from fastapi.responses import StreamingResponse
from uuid import UUID

# --- FIX 1: ADD PARENT DIRECTORY TO PYTHON PATH ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- FIX 2: WINDOWS SPECIFIC LOOP POLICY ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

# Database imports
from database.connection import get_db, init_db
from database import crud

# Auth imports
from auth.routes import router as auth_router
from auth.jwt import get_current_user

# Cache imports
from cache.dom_cache import compute_dom_hash
from cache.redis_cache import get_cached_result, save_cached_result, get_recent_audit, save_recent_audit

# Initialize App
app = FastAPI(title="Ay11Sutra API v3.0")

# Include auth routes
app.include_router(auth_router)

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REQUEST MODELS ---

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 50


class AuditRequest(BaseModel):
    url: str
    force_rescan: bool = False  # Skip cache if True


class PdfRequest(BaseModel):
    url: str
    summary: Dict[str, Any]
    report: List[Dict[str, Any]]


# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "Ay11Sutra API v3.0 is Online 🟢"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": True}
    except Exception as e:
        return {"status": "degraded", "database": False, "error": str(e)}


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
async def start_audit(
    request: AuditRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Run accessibility audit with caching and persistence.
    """
    print(f"🚀 API: Starting Deep Audit on {request.url}")
    print(f"👤 User: {current_user['email']}")
    
    try:
        from backend.graph.workflow import audit_graph
        from backend.tools.dom_scanner import scan_page
        
        # Step 0: Time-based Cache Check (Optimization)
        if not request.force_rescan:
            recent_audit = get_recent_audit(request.url)
            if recent_audit:
                try:
                    audit = crud.create_audit(
                        db, 
                        user_id=UUID(current_user["id"]),
                        url=request.url,
                        dom_hash="time_cached",
                        total_issues=recent_audit.get("summary", {}).get("total", 0),
                        cached=True
                    )
                    print(f"💾 Saved time-cached audit to DB: {audit.id}")
                except Exception as db_err:
                    print(f"⚠️ DB save error (time-cached): {db_err}")
                
                return {
                    "status": "success",
                    "url": request.url,
                    "cached": True,
                    **recent_audit
                }
        
        # Step 1: Quick scan to get DOM hash (for cache check)
        # We'll compute the hash from the actual audit later
        
        # Run the audit
        initial_state = {"url": request.url}
        final_state = await audit_graph.ainvoke(initial_state)
        
        report = final_state.get("final_report", [])
        dom_hash = final_state.get("dom_hash", "")
        
        # Check cache (unless force_rescan)
        was_cached = False
        if not request.force_rescan and dom_hash:
            cached = get_cached_result(request.url, dom_hash)
            if cached:
                # Update: still save to DB as cached access
                try:
                    audit = crud.create_audit(
                        db, 
                        user_id=UUID(current_user["id"]),
                        url=request.url,
                        dom_hash=dom_hash,
                        total_issues=cached.get("summary", {}).get("total", 0),
                        cached=True
                    )
                    print(f"💾 Saved cached audit to DB: {audit.id}")
                except Exception as db_err:
                    print(f"⚠️ DB save error (cached): {db_err}")
                
                return {
                    "status": "success",
                    "url": request.url,
                    "cached": True,
                    **cached
                }
        
        # Build response
        summary = {"total": len(report)}
        
        # Save to database
        try:
            audit = crud.create_audit(
                db,
                user_id=UUID(current_user["id"]),
                url=request.url,
                dom_hash=dom_hash,
                total_issues=len(report),
                cached=False
            )
            
            # Save issues
            if report:
                crud.bulk_create_issues(db, audit.id, report)
            
            print(f"💾 Saved audit to DB: {audit.id} with {len(report)} issues")
        except Exception as db_err:
            print(f"⚠️ DB save error: {db_err}")
        
        # Save to cache
        if dom_hash:
            save_cached_result(request.url, dom_hash, {
                "summary": summary,
                "report": report
            })
            
            # Save to time-based cache (5 minutes)
            save_recent_audit(request.url, {
                "summary": summary,
                "report": report
            }, ttl=300)
        
        return {
            "status": "success",
            "url": request.url,
            "cached": False,
            "summary": summary,
            "report": report
        }

    except Exception as e:
        print(f"❌ AUDIT ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audits")
async def get_audit_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    query: Optional[str] = None,
    cached: bool = False
):
    """
    Get user's audit history.
    By default returns only non-cached audits (actual scans).
    Use cached=true to include cached results.
    """
    audits = crud.get_audits_by_user(db, UUID(current_user["id"]), limit, url_filter=query, include_cached=cached)
    return {
        "audits": [
            {
                "id": str(a.id),
                "url": a.url,
                "total_issues": a.total_issues,
                "cached": a.cached,
                "created_at": a.created_at.isoformat()
            }
            for a in audits
        ]
    }


@app.get("/audits/{audit_id}")
async def get_audit_detail(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get single audit with issues."""
    audit = crud.get_audit_by_id(db, UUID(audit_id))
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if str(audit.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    issues = crud.get_issues_by_audit(db, UUID(audit_id))
    
    return {
        "id": str(audit.id),
        "url": audit.url,
        "total_issues": audit.total_issues,
        "cached": audit.cached,
        "created_at": audit.created_at.isoformat(),
        "issues": [
            {
                "id": str(i.id),
                "rule": i.rule,
                "category": i.category,
                "priority": i.priority,
                "wcag_sc": i.wcag_sc,
                "description": i.description,
                "html_snippet": i.html_snippet,
                "ai_explanation": i.ai_explanation,
                "ai_fixed_code": i.ai_fixed_code
            }
            for i in issues
        ]
    }


@app.post("/export-pdf")
async def export_pdf(request: PdfRequest):
    """Generate PDF report."""
    try:
        from backend.report.pdf_generator import generate_pdf_report

        report_data = {
            "summary": request.summary,
            "report": request.report,
        }

        pdf_bytes = generate_pdf_report(report_data, request.url)
        filename = "ay11sutra-report.pdf"

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


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Ay11Sutra API...")
    try:
        init_db()
    except Exception as e:
        print(f"⚠️ DB init error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
