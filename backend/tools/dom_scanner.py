import asyncio
from playwright.async_api import async_playwright
import base64

async def scan_page(url: str):
    print(f"🛠️ TOOL: Scanning {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-web-security"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            print("⏳ TOOL: Navigating...")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            print("⏳ TOOL: Waiting 4 seconds for full render...")
            await page.wait_for_timeout(4000) 
            
            # Screenshot
            screenshot_bytes = await page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            page_title = await page.title()

            # Inject & Run Axe
            print("💉 TOOL: Injecting Axe-core...")
            await page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.0/axe.min.js")
            
            print("🏃 TOOL: Running accessibility scan...")
            raw_results = await page.evaluate("""async () => {
                return await axe.run({
                    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] }
                });
            }""")
            
            await browser.close()
            
            violations = raw_results.get("violations", [])
            print(f"✅ TOOL: Found {len(violations)} raw violation types.")
            
            return {
                "violations": clean_violations(violations),
                "screenshot": screenshot_b64,
                "title": page_title
            }

        except Exception as e:
            await browser.close()
            print(f"❌ TOOL ERROR: {e}")
            return {"error": str(e)}

def clean_violations(violations):
    simplified = []
    for v in violations:
        rule_id = v.get("id", "unknown")
        description = v.get("help", v.get("description", "No description"))
        impact = v.get("impact", "minor")
        
        # --- CRITICAL FIX: EXTRACT NODES CORRECTLY ---
        raw_nodes = v.get("nodes", [])
        node_details = []
        
        for node in raw_nodes:
            # Extract HTML Source
            html = node.get("html", "").strip()
            
            # Extract CSS Selector (Target)
            # Axe returns ['#id > div'] list
            target = node.get("target", [])
            selector = target[0] if target else "Unknown Selector"
            
            node_details.append({
                "html": html,
                "target": selector
            })

        simplified.append({
            "id": rule_id,
            "impact": impact,
            "description": description,
            "count": len(raw_nodes),
            "nodes": node_details  # <--- Passing this list is vital
        })
        
    return simplified