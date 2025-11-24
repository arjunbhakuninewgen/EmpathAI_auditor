import json
import logging
import os
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

from backend.tools.dom_scanner import scan_page
from backend.tools.wcag_mapper import enrich_with_wcag
from backend.tools.critic import critique_issues

# Use a slightly higher temperature to allow creative fixes, but keep it structured
api_key = os.getenv("GOOGLE_API_KEY")
text_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key)
vision_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=api_key)

# --- NODE 1: SCANNER ---
async def scanner_node(state: dict) -> dict:
    print(f"👀 Scanner Node → Auditing {state['url']}")
    result = await scan_page(state["url"])

    if "error" in result:
        return {"raw_violations": [], "screenshot_b64": None}

    raw_list = result.get("violations", [])
    enriched = [enrich_with_wcag(v) for v in raw_list]
    
    return {
        "raw_violations": enriched,
        "screenshot_b64": result.get("screenshot"),
    }

# --- NODE 2: CRITIC ---
def critic_node(state: dict) -> dict:
    issues = state.get("raw_violations", [])
    critiqued = critique_issues(issues)
    print(f"📊 Critic Node: Grouped {len(issues)} raw into {len(critiqued)} unique issues.")
    return {"critiqued_issues": critiqued}

# --- NODE 3: VISION ---
async def vision_analyzer_node(state: dict) -> dict:
    screenshot_b64 = state.get("screenshot_b64")
    if not screenshot_b64: return {"vision_issues": []}

    prompt = """Analyze this website screenshot for Accessibility.
    Identify visual issues like: Low contrast, Missing focus indicators, Small touch targets.
    Return JSON: {"vision_issues": [{"title": "...", "severity": "critical", "explanation": "..."}]}"""

    try:
        response = await vision_llm.ainvoke([
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{screenshot_b64}"}
            ])
        ])
        # Cleaning response to ensure valid JSON
        content = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        issues = []
        for i in data.get("vision_issues", []):
            i.update({
                "rule": "vision-ai",
                "is_vision": True,
                "fix_priority": "HIGH - Visual Issue",
                "wcag_sc": "2.4.7 / 1.4.3",
                "ai_fixed_code": "Visual issue - check CSS",
                "html_snippet": "Detected from screenshot",
                "selector": "Visual Element"
            })
            issues.append(i)
        return {"vision_issues": issues}
    except Exception:
        return {"vision_issues": []}

# --- NODE 4: FIXER (ROBUST VERSION) ---
async def fixer_node(state: dict) -> dict:
    print("🔧 Fixer Node → Analyzing & Fixing...")
    
    issues = state.get("critiqued_issues", [])
    vision = state.get("vision_issues", [])
    final_report = []

    # Process ALL issues (Removed the limit so you see everything)
    all_issues = issues + vision

    for i, issue in enumerate(all_issues):
        
        # 1. EXTRACT DATA
        snippets = issue.get("code_snippets", [])
        if snippets and len(snippets) > 0:
            bad_code = snippets[0].get("html", "Code not available")
            selector = snippets[0].get("target", "Unknown Selector")
        else:
            bad_code = issue.get("html_snippet", "Code not available")
            selector = issue.get("selector", "Unknown")

        issue["html_snippet"] = bad_code
        issue["selector"] = selector

        # 2. SKIP CONDITIONS
        if issue.get("is_vision") or bad_code == "Code not available":
            final_report.append(issue)
            continue

        print(f"   👉 Generating AI fix for: {issue.get('rule')} ({i+1}/{len(all_issues)})")

        # 3. ROBUST AI PROMPT
        # We explicitly tell Gemini to handle missing context gracefully
        user_prompt = f"""
        You are a Web Accessibility Expert.
        
        VIOLATION:
        Rule ID: {issue.get('rule')}
        Description: {issue.get('description')}
        
        BAD CODE SNIPPET:
        ```html
        {bad_code}
        ```
        
        TASK:
        1. Explain WHY this fails WCAG in 1 simple sentence.
        2. Provide the FIXED HTML code. If the tag is empty (like <button></button>), assume a logical fix (e.g., add aria-label or text).
        
        OUTPUT FORMAT (Strict JSON, no markdown):
        {{
            "explanation": "The button has no text, so screen readers cannot announce it.",
            "fixed_code": "<button aria-label='Select Date'>...</button>"
        }}
        """
        
        try:
            # Direct generation (JsonOutputParser sometimes fails with Gemini)
            # We will use basic invoke and clean the string manually for maximum stability
            response = await text_llm.ainvoke(user_prompt)
            
            # Clean the string
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(clean_json)
            
            issue["ai_explanation"] = ai_data.get("explanation", "Fixed by AI")
            issue["ai_fixed_code"] = ai_data.get("fixed_code", "<!-- Fixed Code -->")

        except Exception as e:
            print(f"❌ AI ERROR on {issue.get('rule')}: {str(e)}")
            
            # Fallback explanation so the UI is never empty
            issue["ai_explanation"] = f"Error generating fix: {str(e)}. Please review WCAG guidelines manually."
            issue["ai_fixed_code"] = "<!-- AI generation failed. Check server logs. -->"

        final_report.append(issue)

    print(f"📊 Fixer Node: Final Report has {len(final_report)} total issues.")
    return {"final_report": final_report}