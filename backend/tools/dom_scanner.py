import asyncio
from playwright.async_api import async_playwright
from axe_playwright_python.async_playwright import Axe

async def scan_page(url: str):
    print(f"🛠️ TOOL: Scanning {url}...")
    
    async with async_playwright() as p:
        # Launch with arguments to handle modern web apps better
        browser = await p.chromium.launch(headless=True, args=["--disable-web-security"])
        
        # Create context with a real desktop User Agent so sites don't hide content
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            # 1. Go to URL and wait for NETWORK IDLE (Wait for API calls to finish)
            await page.goto(url, timeout=60000, wait_until="networkidle")
            
            # 2. Extra buffer for React/Vue animations
            await page.wait_for_timeout(2000) 
            
            # 3. Take Screenshot (For the Vision Agent later)
            import base64
            screenshot_bytes = await page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

            # 4. Initialize Axe with "World Class" Configuration
            axe = Axe()
            
            # --- THE SECRET SAUCE ---
            # We include 'best-practice' to catch things like Missing H1, Skip Links, etc.
            # We include 'wcag22aa' for the latest standards.
            results = await axe.run(page, options={
                "iframes": True, # Scan inside iframes
                "runOnly": {
                    "type": "tag",
                    "values": [
                        "wcag2a", "wcag2aa",       # WCAG 2.0
                        "wcag21a", "wcag21aa",     # WCAG 2.1
                        "wcag22aa",                # WCAG 2.2 (New!)
                        "best-practice",           # Catches "Missing H1", "Landmarks"
                        "cat.structure",           # Structural issues
                        "cat.sensory",             # Color/Audio issues
                        "cat.forms"                # Form label issues
                    ]
                }
            })
            
            await browser.close()
            
            # Extract violations safely
            violations = getattr(results, "violations", [])
            if not violations and isinstance(results, dict):
                violations = results.get("violations", [])

            print(f"✅ TOOL: Found {len(violations)} violation types.")
            
            return {
                "violations": clean_violations(violations),
                "screenshot": screenshot_b64
            }

        except Exception as e:
            await browser.close()
            print(f"❌ TOOL ERROR: {e}")
            return {"error": str(e)}

def clean_violations(violations):
    simplified = []
    for v in violations:
        # Robust extraction logic
        rule_id = getattr(v, "id", None) or v.get("id")
        impact = getattr(v, "impact", None) or v.get("impact")
        description = getattr(v, "help", None) or v.get("help") # 'help' is usually better than description
        
        # Get nodes
        raw_nodes = getattr(v, "nodes", []) or v.get("nodes", [])
        
        node_details = []
        for node in raw_nodes:
            html = getattr(node, "html", "") or node.get("html", "")
            target = getattr(node, "target", []) or node.get("target", [])
            selector = target[0] if target else "Unknown"
            
            node_details.append({
                "html": html,
                "target": selector
            })

        simplified.append({
            "id": rule_id,
            "impact": impact,
            "description": description,
            "count": len(raw_nodes),
            "nodes": node_details
        })
        
    return simplified