import os
import google.generativeai as genai
from dotenv import load_dotenv
from backend.tools.dom_scanner import scan_page
from backend.tools.wcag_mapper import map_to_wcag
from backend.tools.reporter import generate_report
from backend.tools.critic import critique_issues
# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key: raise ValueError("❌ GOOGLE_API_KEY is missing")
genai.configure(api_key=api_key)

class OrchestratorAgent:
    def __init__(self):
        self.model_name = 'gemini-2.5-flash-lite'
        self.model = genai.GenerativeModel(self.model_name)

    async def run_audit(self, url: str, wcag_level: str):
        print(f"🤖 AGENT: Processing {url}...")
        
        # 1. SCAN (The Eyes)
        raw_scan = await scan_page(url)
        
        if isinstance(raw_scan, dict) and "error" in raw_scan:
            return raw_scan

        # 2. MAP & REPORT (The Logic)
                # 2. MAP (The Logic)
        mapped_data = map_to_wcag(raw_scan)
        
        # --- NEW STEP: CRITIQUE ---
        print("🤖 AGENT: Critiquing and prioritizing issues...")
        prioritized_data = critique_issues(mapped_data)
        # --------------------------

        # 3. REPORT (The Writer)
        # Note: We pass 'prioritized_data' now, not 'mapped_data'
        structured_report = generate_report(url, prioritized_data)


        # 3. ANALYZE (The Brain)
        # If no issues, skip AI to save money
        if structured_report["metadata"]["total_issues"] == 0:
            return {
                "report": structured_report,
                "ai_summary": "✅ Compliance Check Passed. No WCAG violations found."
            }

        print("🤖 AGENT: Asking Gemini to summarize the structured report...")
        
        prompt = f"""
        You are a Senior Accessibility Consultant.
        Analyze this WCAG accessibility report: {structured_report}
        
        Output Requirements:
        1. EXECUTIVE SUMMARY: Write a professional 3-4 sentence paragraph summarizing the site's accessibility health. Mention the total issue count and the most critical risk found. (Do not use bullet points here).
        
        2. DEV TASKS: For each unique rule ID, provide a concise, technical instruction.
        Format: "Rule ID: Actionable fix".
        """

        try:
            response = await self.model.generate_content_async(prompt)
            ai_summary = response.text
        except Exception as e:
            ai_summary = f"AI Analysis failed: {str(e)}"

        # 4. RETURN EVERYTHING
        return {
            "report": structured_report,
            "ai_insight": ai_summary
        }