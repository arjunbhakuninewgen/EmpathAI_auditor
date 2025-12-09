# backend/tools/dom_scanner.py

import asyncio
from playwright.async_api import async_playwright
from axe_playwright_python.async_playwright import Axe
import base64
import traceback


async def scan_page(url: str):
    print(f"🛠️ TOOL: Scanning {url}...")

    async with async_playwright() as p:
        # 1. Launch Browser
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            bypass_csp=True,
        )
        page = await context.new_page()

        try:
            # --- NAVIGATION ---
            print("⏳ TOOL: Navigating...")
            await page.goto(url, timeout=60000, wait_until="networkidle")
            await page.wait_for_timeout(3000)

            page_title = await page.title()
            html = await page.content()
            print(f"🔍 DEBUG: Page title = {page_title!r}")
            print(f"🔍 DEBUG: HTML length = {len(html)}")

            # --- SCREENSHOT ---
            screenshot_bytes = await page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # --- SEMANTIC CONTENT (NON-FATAL) ---
            print("🧠 TOOL: Extracting semantic content...")
            try:
                dom_content = await page.evaluate(
                    """
                    () => ({
                        links: Array.from(document.querySelectorAll('a[href]'))
                            .slice(0, 50)
                            .map(a => {
                                // Helper to generate a simple unique selector
                                const getSelector = (el) => {
                                    if (el.id) return '#' + el.id;
                                    if (el.className) return '.' + el.className.split(' ')[0];
                                    return el.tagName.toLowerCase();
                                };
                                return {
                                    text: a.innerText.trim() || "No Text",
                                    href: a.href,
                                    html: a.outerHTML.substring(0, 200), // Capture snippet
                                    selector: getSelector(a) // Basic selector
                                };
                            }),
                        headings: Array.from(
                            document.querySelectorAll('h1, h2, h3, h4, h5, h6')
                        ).map(h => ({
                            level: h.tagName,
                            text: h.innerText.trim()
                        }))
                    })
                    """
                )
                links_len = len(dom_content.get("links", []))
                headings_len = len(dom_content.get("headings", []))
                print(
                    f"🔍 DEBUG: Semantic extract -> {links_len} links, "
                    f"{headings_len} headings"
                )
            except Exception as sem_e:
                print("⚠️ SEMANTIC EXTRACTION ERROR (non-fatal):", sem_e)
                traceback.print_exc()
                dom_content = {"links": [], "headings": []}

            # --- KEYBOARD INTERACTION (NON-FATAL) ---
            print("🤖 TOOL: Running Keyboard Interaction...")
            tab_log = []
            try:
                await page.evaluate("document.body.focus()")
                for _ in range(15):
                    await page.keyboard.press("Tab")
                    await page.wait_for_timeout(60)
                    focused = await page.evaluate(
                        """
                        () => {
                            const el = document.activeElement;
                            return {
                                tag: el.tagName,
                                text: (el.innerText || '').substring(0, 20),
                                id: el.id || ''
                            };
                        }
                        """
                    )
                    tab_log.append(focused)
                print(f"🔍 DEBUG: Keyboard tab log length = {len(tab_log)}")
            except Exception as kb_e:
                print("⚠️ KEYBOARD SIMULATION ERROR (non-fatal):", kb_e)
                traceback.print_exc()

            # --- AXE SCAN (TECHNICAL ERRORS) ---
            print("💉 TOOL: Running Axe-core via Library...")
            axe = Axe()

            results = await axe.run(page)

            print(f"🔍 DEBUG: Axe result type = {type(results)}")
            print(f"🔍 DEBUG: Axe violations_count = {getattr(results, 'violations_count', 'N/A')}")

            # ------- ROBUST VIOLATION EXTRACTION -------
            violations = []

            # The axe-playwright-python library stores results in the 'response' property
            # which is a dict containing 'violations', 'passes', 'incomplete', etc.
            try:
                if hasattr(results, 'response') and results.response:
                    response_data = results.response
                    if isinstance(response_data, dict):
                        violations = response_data.get("violations", []) or []
                        print(f"🔍 DEBUG: Extracted {len(violations)} violations from response.violations")
                    elif isinstance(response_data, str):
                        # Sometimes it's a JSON string
                        import json
                        response_dict = json.loads(response_data)
                        violations = response_dict.get("violations", []) or []
                        print(f"🔍 DEBUG: Extracted {len(violations)} violations from JSON response")
            except Exception as e:
                print(f"⚠️ Failed to extract from response: {e}")

            # Fallback: Try direct attribute access
            if not violations and hasattr(results, "violations"):
                try:
                    violations = results.violations or []
                    print(f"🔍 DEBUG: Extracted {len(violations)} violations from direct attribute")
                except Exception as e:
                    print(f"⚠️ Failed direct attribute access: {e}")

            # Fallback: Try dict-style access
            if not violations and hasattr(results, "__getitem__"):
                try:
                    violations = results["violations"] or []
                    print(f"🔍 DEBUG: Extracted {len(violations)} violations from dict access")
                except Exception as e:
                    print(f"⚠️ Failed dict access: {e}")

            print(f"✅ TOOL: Found {len(violations)} raw syntax violations.")


            await browser.close()

            return {
                "violations": clean_violations(violations),
                "screenshot": screenshot_b64,
                "title": page_title,
                "dom_content": dom_content,
                "tab_log": tab_log,
            }

        except Exception as e:
            print("❌ TOOL ERROR in scan_page:", e)
            traceback.print_exc()
            await browser.close()
            return {
                "error": str(e),
                "violations": [],
                "screenshot": None,
                "dom_content": {},
                "tab_log": [],
            }


# --- CRITICAL FIX: ENSURE CODE IS ALWAYS PRESENT ---
import base64  # make sure this import exists at top

def clean_violations(violations):
    simplified = []

    for v in violations:
        rule_id = getattr(v, "id", None) or (
            v.get("id") if isinstance(v, dict) else "unknown"
        )
        description = getattr(v, "help", None) or (
            v.get("help") if isinstance(v, dict) else "No description"
        )
        impact = getattr(v, "impact", None) or (
            v.get("impact") if isinstance(v, dict) else "minor"
        )

        raw_nodes = getattr(v, "nodes", [])
        if not raw_nodes and isinstance(v, dict):
            raw_nodes = v.get("nodes", [])

        node_details = []
        for node in raw_nodes:
            # 1. Get HTML
            html = getattr(node, "html", "") or (
                node.get("html") if isinstance(node, dict) else ""
            )

            # 2. Get Target (Selector)
            target = getattr(node, "target", []) or (
                node.get("target") if isinstance(node, dict) else []
            )
            selector = target[0] if target else "Unknown Selector"

            # --- LOGIC: IF AXE RETURNS EMPTY HTML, FILL IT IN ---
            if not html or html.strip() == "":
                if "html" in selector:
                    html = "<!-- Root Element -->\n<html>"
                elif "body" in selector:
                    html = "<!-- Body Element -->\n<body>"
                else:
                    html = f"<!-- Element at selector: {selector} -->"

            node_details.append({"html": html, "target": selector})

        simplified.append(
            {
                "id": rule_id,
                "impact": impact,
                "description": description,
                "count": len(raw_nodes),
                "nodes": node_details,
            }
        )

    return simplified
