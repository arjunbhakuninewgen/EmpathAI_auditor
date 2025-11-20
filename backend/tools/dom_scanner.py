import asyncio
from playwright.async_api import async_playwright
from axe_playwright_python.async_playwright import Axe

async def scan_page(url: str):
    print(f"🛠️ TOOL: Scanning {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            print("⏳ TOOL: Waiting for page content...")
            await page.wait_for_timeout(2000) 

            # Run Scan
            axe = Axe()
            results = await axe.run(page)
            
            await browser.close()
            
            # --- DEBUGGING BLOCK START ---
            print(f"🔍 DEBUG: Result Type: {type(results)}")
            print(f"🔍 DEBUG: Attributes: {dir(results)}")
            
            # Strategy 1: Standard Attribute
            if hasattr(results, 'violations'):
                violations = results.violations
            # Strategy 2: Dictionary Access (Subscript)
            elif hasattr(results, '__getitem__'):
                violations = results['violations']
            # Strategy 3: Hidden inside .response
            elif hasattr(results, 'response'):
                violations = results.response.get('violations', [])
            # Strategy 4: Conversion method
            elif hasattr(results, 'to_dict'):
                violations = results.to_dict().get('violations', [])
            else:
                print("❌ CRITICAL: Could not find violations data structure.")
                violations = []
            # --- DEBUGGING BLOCK END ---

            print(f"✅ TOOL: Found {len(violations)} violation types.")
            
            return clean_violations(violations)

        except Exception as e:
            await browser.close()
            print(f"❌ TOOL ERROR: {e}")
            return {"error": str(e)}

def clean_violations(violations):
    simplified = []
    for v in violations:
        # --- DEBUG: PRINT THE RAW ID TO TERMINAL ---
        # This helps us see if the ID exists before we process it
        raw_id = getattr(v, "id", None)
        if not raw_id and isinstance(v, dict):
            raw_id = v.get("id")
        print(f"🔍 Processing Rule: {raw_id}") 
        # -------------------------------------------

        # 1. Extract ID (The Name of the Error)
        # Try attribute first, then dictionary, then fallback
        rule_id = getattr(v, "id", None)
        if rule_id is None and isinstance(v, dict):
            rule_id = v.get("id")
        if rule_id is None:
            rule_id = "unknown-rule"

        # 2. Extract Impact (Severity)
        impact = getattr(v, "impact", None)
        if impact is None and isinstance(v, dict):
            impact = v.get("impact")
        
        # 3. Extract Description
        description = getattr(v, "help", None) # 'help' is usually better/shorter than 'description'
        if description is None and isinstance(v, dict):
            description = v.get("help")

        # 4. Extract Nodes (The HTML Snippets)
        raw_nodes = getattr(v, "nodes", [])
        if not raw_nodes and isinstance(v, dict):
            raw_nodes = v.get("nodes", [])
        
        node_details = []
        for node in raw_nodes:
            # Extract HTML snippet and Target (Selector)
            html_snippet = getattr(node, "html", "")
            target_list = getattr(node, "target", [])
            
            if not html_snippet and isinstance(node, dict):
                html_snippet = node.get("html", "")
                target_list = node.get("target", [])

            selector = target_list[0] if target_list else "Unknown Selector"

            node_details.append({
                "html": html_snippet,
                "target": selector
            })

        simplified.append({
            "id": rule_id, # <--- This is the critical fix
            "impact": impact,
            "description": description,
            "count": len(raw_nodes),
            "nodes": node_details
        })
        
    return simplified