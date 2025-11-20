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
        # Handle Object vs Dict (Safety check)
        is_dict = isinstance(v, dict)
        
        # Extract the raw nodes (the specific HTML elements)
        raw_nodes = v.get("nodes", []) if is_dict else getattr(v, "nodes", [])
        
        node_details = []
        for node in raw_nodes:
            # Extract HTML snippet and CSS Selector
            if is_dict:
                node_details.append({
                    "html": node.get("html"),
                    "target": node.get("target", ["Unknown"])[0] # CSS Selector
                })
            else:
                # If it's an object
                node_details.append({
                    "html": getattr(node, "html", ""),
                    "target": getattr(node, "target", ["Unknown"])[0]
                })

        simplified.append({
            "rule_id": v.get("id") if is_dict else getattr(v, "id", "unknown"),
            "impact": v.get("impact") if is_dict else getattr(v, "impact", "minor"),
            "description": v.get("description") if is_dict else getattr(v, "description", ""),
            "count": len(raw_nodes),
            "nodes": node_details # <--- WE KEEP THIS NOW!
        })
    return simplified