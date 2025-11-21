import os
import json
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Import your existing tools
from backend.tools.dom_scanner import scan_page
from backend.tools.wcag_mapper import map_to_wcag
from backend.tools.critic import critique_issues
from backend.graph.state import AuditState

# --- SETUP AI MODEL ---
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    google_api_key=api_key,
    temperature=0
)

# --- NODE 1: THE SCANNER ---
async def scanner_node(state: AuditState):
    print(f"👀 NODE: Scanning {state['url']}...")
    scan_result = await scan_page(state['url'])
    
    if isinstance(scan_result, dict) and "error" in scan_result:
        return {"raw_violations": [], "screenshot_b64": None}
        
    if isinstance(scan_result, list):
        return {"raw_violations": scan_result, "screenshot_b64": None}
    
    return {
        "raw_violations": scan_result.get("violations", []),
        "screenshot_b64": scan_result.get("screenshot")
    }

# --- NODE 2: THE CRITIC ---
def critic_node(state: AuditState):
    print("⚖️ NODE: Critiquing & Prioritizing...")
    raw = state.get("raw_violations", [])
    mapped = map_to_wcag(raw)
    critiqued = critique_issues(mapped)
    return {"critiqued_issues": critiqued}

# --- NODE 3: THE FIXER (UPDATED) ---
async def fixer_node(state: AuditState):
    print("🔧 NODE: Generating AI Fixes...")
    
    issues = state.get("critiqued_issues", [])
    final_report = []
    
    # Process Top 5 issues
    top_issues = issues[:5] 
    
    for issue in top_issues:
        # 1. Extract the Code Snippets (The Missing Link)
        snippets = issue.get("code_snippets", [])
        
        # Get the first occurrence to show in the UI
        if snippets and len(snippets) > 0:
            # Handle if snippet is a dict (new scanner) or object
            first_snippet = snippets[0]
            bad_code = first_snippet.get("html", "Code not available")
            selector = first_snippet.get("target", "Unknown Selector")
        else:
            bad_code = "Code not available"
            selector = "Unknown"

        # 2. SAVE IT FOR THE FRONTEND (This fixes your bug)
        issue["html_snippet"] = bad_code
        issue["selector"] = selector

        # Skip AI if no code
        if bad_code == "Code not available":
            issue["ai_explanation"] = "Code snippet unavailable."
            issue["ai_fixed_code"] = "N/A"
            final_report.append(issue)
            continue

        # 3. Generate AI Fix
        prompt = ChatPromptTemplate.from_template("""
        You are an Expert Web Accessibility Developer.
        
        **The Problem:**
        Rule: {rule}
        WCAG Criteria: {wcag}
        Bad HTML Code: 
        ```html
        {bad_code}
        ```
        
        **Your Task:**
        1. Explain WHY this is an accessibility error in 1 sentence.
        2. Provide the CORRECTED HTML code that fixes this specific issue.
        
        **Output Format (JSON ONLY):**
        {{
            "explanation": "The image is missing an alt attribute...",
            "fixed_code": "<img src='...' alt='...'>"
        }}
        """)
        
        chain = prompt | llm | JsonOutputParser()
        
        try:
            ai_result = await chain.ainvoke({
                "rule": issue.get("rule", "Unknown"),
                "wcag": issue.get("wcag", "Unknown"),
                "bad_code": bad_code
            })
            
            issue["ai_explanation"] = ai_result.get("explanation")
            issue["ai_fixed_code"] = ai_result.get("fixed_code")
            
        except Exception as e:
            print(f"⚠️ AI Fix Failed: {e}")
            issue["ai_explanation"] = "AI could not generate a fix."
            issue["ai_fixed_code"] = "Error generating code."
            
        final_report.append(issue)
    
    # Add remaining issues (without AI fixes)
    # We also need to ensure they have the display keys
    for issue in issues[5:]:
        snippets = issue.get("code_snippets", [])
        if snippets:
            issue["html_snippet"] = snippets[0].get("html", "Code not available")
            issue["selector"] = snippets[0].get("target", "Unknown")
        else:
            issue["html_snippet"] = "Code not available"
            issue["selector"] = "Unknown"
        final_report.append(issue)
    
    return {"final_report": final_report}