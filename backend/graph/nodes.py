# backend/graph/nodes.py

import json
import os
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Import Tools
from backend.tools.dom_scanner import scan_page
from backend.tools.wcag_mapper import enrich_with_wcag
from backend.tools.critic import critique_issues
from backend.guardrails.input_guard import validate_input
from backend.guardrails.output_guard import validate_fix
from backend.slm.fast_critic import fast_critique
# from backend.dpi.bhashini import translate_text # New DPI Service - COMMENTED OUT FOR NOW

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

# --- CONFIGURATION ---
# Force REST transport to avoid SSL/gRPC issues with corporate proxies
# Using gemini-2.0-flash instead of gemini-2.5-flash-lite for higher free tier quota (1500 vs 20 req/day)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    temperature=0, 
    google_api_key=api_key,
    transport="rest"  # Use REST instead of gRPC to avoid SSL certificate issues
)

# --- NODE 0: INPUT GUARD ---
def input_guard_node(state: dict) -> dict:
    return validate_input(state)

# --- NODE 1: SCANNER ---
async def scanner_node(state: dict) -> dict:
    # Check for upstream errors
    if "error" in state:
        print(f"⛔ Scanner skipped due to input error: {state['error']}")
        return {"error": state["error"]}

    print(f"👀 Scanner Node → Auditing {state['url']}")
    result = await scan_page(state["url"])

    if "error" in result:
        return {
            "raw_violations": [], "screenshot_b64": None,
            "dom_content": {}, "tab_log": [], "dom_hash": ""
        }

    raw_list = result.get("violations", [])
    enriched = [enrich_with_wcag(v) for v in raw_list]
    
    # Compute DOM hash for caching
    dom_hash = ""
    html = result.get("html", "")
    if html:
        try:
            from cache.dom_cache import compute_dom_hash
            dom_hash = compute_dom_hash(html)
            print(f"🔑 DOM Hash: {dom_hash[:16]}...")
        except Exception as e:
            print(f"⚠️ DOM hash error: {e}")
    
    return {
        "raw_violations": enriched,
        "screenshot_b64": result.get("screenshot"),
        "dom_content": result.get("dom_content", {}),
        "tab_log": result.get("tab_log", []),
        "dom_hash": dom_hash
    }

# --- NODE 2: CRITIC ---
async def critic_node(state: dict) -> dict:
    """Group raw Axe violations, attach WCAG metadata and a representative HTML snippet.

    This node:
    - calls critic.critique_issues to group by rule
    - marks all of these as category='syntax'
    - exposes `html_snippet` and `selector` for the frontend & Fixer node
    """
    issues = state.get("raw_violations", [])
    
    # --- HYBRID SLM LAYER (Tier 1: Heuristic + Tier 2: Model-based) ---
    issues = await fast_critique(issues)
    # ------------------------------------------------------------------

    critiqued = critique_issues(issues)

    for c in critiqued:
        # Tag the issue as a code/syntax issue
        c["category"] = "syntax"

        # If critic collected per-node details, expose the first one in a stable shape
        snippets = c.get("code_snippets", [])
        if snippets:
            first = snippets[0]
            c["html_snippet"] = first.get("html", "") or c.get("html_snippet", "")
            c["selector"] = first.get("target", "") or c.get("selector", "")

    print(f"📊 Critic Node: Grouped {len(issues)} raw into {len(critiqued)} unique syntax issues.")
    return {"critiqued_issues": critiqued}

# --- NODE 3: SEMANTIC ANALYZER --------------------------------------
async def semantic_node(state: dict) -> dict:
    print("🧠 Semantic Node → Analyzing Context & Meaning...")
    content = state.get("dom_content", {})
    links = content.get("links", [])
    headings = content.get("headings", [])
    
    if not links and not headings:
        print("⚠️ No semantic elements found")
        return {"semantic_issues": []}

    # STRONG JSON INSTRUCTION + STRICT FORMAT
    prompt = f"""
You are an expert in WCAG 2.4.4 (Link Purpose) and 2.4.6 (Headings & Labels).

Analyze the following extracted page content:

LINKS:
{json.dumps(links[:20], indent=2)}

HEADINGS:
{json.dumps(headings[:20], indent=2)}

Identify semantic accessibility issues such as:
- Vague or contextless link text ("Click here", "Learn more", "No Text")
- Duplicate link text pointing to different destinations
- Missing or skipped heading levels (H1 → H3 skip)
- Headings used visually but not semantically
- Headings that are empty or unclear

Return ONLY valid JSON in this exact structure:

{{
    "issues": [
        {{
            "rule": "semantic-link" | "heading-structure" | "heading-empty",
            "description": "Human-readable explanation",
            "fix": "Specific recommended HTML/text fix",
            "selector": "The selector from the input data",
            "html_snippet": "The HTML snippet from the input data"
        }}
    ]
}}
"""

    try:
        response = llm.invoke(prompt)  # Changed from ainvoke to invoke

        raw = response.content.replace("```json", "").replace("```", "").strip()
        print("🔍 RAW SEMANTIC RESPONSE:", raw)

        data = json.loads(raw)

        issues = []
        for item in data.get("issues", []):
            issues.append({
                "rule": item.get("rule", "semantic-issue"),
                "category": "semantic",
                "description": item.get("description", "Semantic issue found."),
                "fix_priority": "MEDIUM",
                "wcag_sc": "2.4.4",
                "html_snippet": item.get("html_snippet", "Semantic Analysis"),
                "selector": item.get("selector", "N/A"),
                "ai_explanation": item.get("description"),
                "ai_fixed_code": item.get("fix", "Update the text or structure.")
            })

        print(f"🧩 Semantic issues generated: {len(issues)}")
        return {"semantic_issues": issues}

    except Exception as e:
        print("❌ SEMANTIC PARSE ERROR:", e)
        return {"semantic_issues": []}

# --- NODE 4: INTERACTION AGENT ---
def interaction_node(state: dict) -> dict:
    print("🤖 Interaction Node → Analyzing Keyboard Flow...")
    log = state.get("tab_log", [])
    issues = []
    
    if not log:
        print("⚠️ No keyboard interaction log found")
        return {"interaction_issues": []}
    
    print(f"🔍 DEBUG: Analyzing {len(log)} keyboard interactions")
    
    # Issue 1: Focus lost to <body> tag (focus trap)
    body_focus = [item for item in log if item.get('tag') == 'BODY']
    if len(body_focus) > 1:
        issues.append({
            "rule": "keyboard-focus-lost",
            "category": "interaction",
            "fix_priority": "CRITICAL",
            "wcag_sc": "2.4.7",
            "description": f"Focus lost to <body> tag {len(body_focus)} times during keyboard navigation. This indicates a focus trap or missing focus management.",
            "html_snippet": "Focus management issue detected",
            "ai_explanation": "When users press Tab, focus should move to the next interactive element. If focus jumps to <body>, users lose track of where they are on the page.",
            "ai_fixed_code": "Ensure all interactive elements are keyboard accessible. Add tabindex='0' to custom interactive elements or use semantic HTML like <button> instead of <div>."
        })
    
    # Issue 2: Non-interactive elements receiving focus
    non_interactive_tags = ['DIV', 'SPAN', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']
    non_interactive_focused = [item for item in log if item.get('tag') in non_interactive_tags]
    
    if non_interactive_focused:
        issues.append({
            "rule": "non-interactive-tabindex",
            "category": "interaction",
            "fix_priority": "MEDIUM",
            "wcag_sc": "2.4.3",
            "description": f"Found {len(non_interactive_focused)} non-interactive elements with keyboard focus, which can confuse keyboard users.",
            "html_snippet": f"<{non_interactive_focused[0].get('tag')} tabindex='...'>",
            "ai_explanation": "Non-interactive elements (div, span, p) should not receive keyboard focus unless they have an interactive role.",
            "ai_fixed_code": "Remove tabindex from non-interactive elements or add appropriate ARIA roles like role='button' if they are meant to be interactive."
        })
    
    # Issue 3: Very short tab sequence (might indicate missing keyboard access)
    if len(log) < 5:
        issues.append({
            "rule": "limited-keyboard-access",
            "category": "interaction",
            "fix_priority": "HIGH",
            "wcag_sc": "2.1.1",
            "description": f"Only {len(log)} elements are keyboard accessible. This page may have insufficient keyboard navigation.",
            "html_snippet": "Page-wide keyboard accessibility issue",
            "ai_explanation": "A typical page should have many focusable elements (links, buttons, form inputs). Very few focusable elements suggests missing keyboard access.",
            "ai_fixed_code": "Ensure all interactive elements (buttons, links, form controls) are keyboard accessible. Avoid using <div> or <span> for interactive elements without proper tabindex and ARIA roles."
        })
    
    # Issue 4: Duplicate IDs in focusable elements
    ids_seen = {}
    for item in log:
        elem_id = item.get('id')
        if elem_id:
            if elem_id in ids_seen:
                issues.append({
                    "rule": "duplicate-id-focusable",
                    "category": "interaction",
                    "fix_priority": "CRITICAL",
                    "wcag_sc": "4.1.1",
                    "description": f"Duplicate ID '{elem_id}' found on focusable elements. This breaks assistive technology.",
                    "html_snippet": f"<... id='{elem_id}'>",
                    "ai_explanation": "IDs must be unique on a page. Duplicate IDs on focusable elements confuse screen readers and keyboard navigation.",
                    "ai_fixed_code": f"Change one of the elements to use a unique ID, e.g., id='{elem_id}-2'"
                })
                break  # Only report once
            ids_seen[elem_id] = True
    
    print(f"🎯 Interaction issues found: {len(issues)}")
    return {"interaction_issues": issues}

# --- NODE 5: VISION ANALYZER ---
async def vision_analyzer_node(state: dict) -> dict:
    screenshot_b64 = state.get("screenshot_b64")
    if not screenshot_b64: return {"vision_issues": []}

    prompt = """
    Analyze screenshot for WCAG violations (Contrast, Layout).
    Return JSON: {"vision_issues": [{"description": "...", "explanation": "..."}]}
    """
    try:
        response = llm.invoke([  # Changed from ainvoke to invoke
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{screenshot_b64}"}
            ])
        ])
        content = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        issues = []
        for i in data.get("vision_issues", []):
            issues.append({
                "rule": "visual-ai-scan",
                "category": "visual",
                "fix_priority": "HIGH",
                "wcag_sc": "1.4.3",
                "description": i.get("description"),
                "html_snippet": "Visual Detection",
                "ai_explanation": i.get("explanation"),
                "ai_fixed_code": "Check CSS contrast/spacing."
            })
        return {"vision_issues": issues}
    except Exception:
        return {"vision_issues": []}

# --- NODE 6: FIXER ---
async def fixer_node(state: dict) -> dict:
    print("🔧 Fixer Node → Generating Solutions...")
    
    # Get DOM Content for Reverse Lookup (for visual issues)
    dom_content = state.get("dom_content", {})
    interactive_elements = dom_content.get("interactive", [])
    
    all_issues = (
        state.get("critiqued_issues", []) +
        state.get("vision_issues", []) +
        state.get("semantic_issues", []) +
        state.get("interaction_issues", [])
    )
    final_report = []

    print(f"   👉 Processing {len(all_issues)} total issues.")

    for issue in all_issues:
        # 1. Skip if already fixed
        if issue.get("ai_fixed_code") and issue.get("ai_fixed_code") != "<!-- Fix -->":
            final_report.append(issue)
            continue

        rule = issue.get('rule', 'unknown')
        desc = issue.get('description', '')
        snippet = issue.get('html_snippet', '')
        category = issue.get('category', '')

        # --- SMART LOOKUP FOR VISUAL ISSUES ---
        # If it's a visual issue and we don't have code, try to find it by text
        if category == 'visual' and (not snippet or "Visual Detection" in snippet):
            # Try to find text inside single quotes '...' or just match the description
            import re
            match = re.search(r"'(.*?)'", desc)
            search_text = match.group(1) if match else ""
            
            if search_text:
                # Look for this text in our captured buttons/inputs
                for el in interactive_elements:
                    if search_text.lower() in el['text'].lower():
                        snippet = el['html']
                        issue['html_snippet'] = snippet # Update the issue object
                        issue['selector'] = f"<{el['tag']}> containing '{search_text}'"
                        print(f"   🎯 MATCH FOUND: Mapped visual issue to code: {snippet[:50]}...")
                        break

        # 3. Construct Prompt
        has_code = snippet and snippet != "Code not available" and snippet != "Visual Detection"
        
        if not has_code:
            user_prompt = f"""
            You are an Accessibility Expert.
            Violation: "{rule}" - "{desc}".
            I cannot provide the exact code. Provide a general explanation and example fix.
            Return JSON: {{ "explanation": "...", "fixed_code": "..." }}
            """
        else:
            user_prompt = f"""
            Fix this WCAG Violation.
            Rule: {rule}
            Description: {desc}
            
            BAD CODE SNIPPET:
            {snippet}
            
            Task:
            1. Explain why this is an issue.
            2. Provide the FIXED HTML code (Add CSS styles inline if needed for contrast).
            
            Return JSON: {{ "explanation": "...", "fixed_code": "..." }}
            """
        
        try:
            response = llm.invoke(user_prompt)  # Changed from ainvoke to invoke
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(clean_json)
            
            issue["ai_explanation"] = ai_data.get("explanation", "AI Explanation")
            
            # --- OUTPUT GUARD ---
            raw_fix = ai_data.get("fixed_code", "<!-- Check CSS -->")
            issue["ai_fixed_code"] = validate_fix(raw_fix)
            # --------------------

            # --- DPI: BHASHINI TRANSLATION (COMMENTED OUT FOR NOW) ---
            # Translate the explanation to Hindi (Official Language)
            # issue["hindi_explanation"] = translate_text(issue["ai_explanation"], "hi")
            # ---------------------------------
            
        except Exception as e:
            print(f"❌ AI Fix Error on {rule}: {e}")
            issue["ai_explanation"] = "Manual review recommended."
            issue["ai_fixed_code"] = "<!-- Manual Review -->"

        final_report.append(issue)

    return {"final_report": final_report}
