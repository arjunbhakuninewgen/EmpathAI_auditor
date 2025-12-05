import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin

# Ignore these file types to save time
IGNORED_EXTENSIONS = [
    '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', 
    '.js', '.ico', '.xml', '.json', '.mp4', '.mp3', '.wav', 
    '.zip', '.tar', '.gz', '.woff', '.woff2', '.ttf', '.eot'
]

async def crawl_website(start_url: str, max_pages: int = 50):
    """
    Crawls a website using a real browser (Playwright) to find internal links.
    Works for both Static HTML and Modern JS Frameworks (React, Vue, etc).
    
    QA Fix: Normalizes www vs non-www domains to ensure consistent crawling.
    """
    print(f"🕷️ CRAWLER: Starting discovery on {start_url}...")
    
    # QA Fix: Normalize start URL and domain (remove trailing slash, normalize www)
    start_url = start_url.rstrip('/')
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc.replace('www.', '')  # Normalize: example.com
    
    found_urls = set()
    found_urls.add(start_url)
    
    # Queue for Breadth-First Search (BFS)
    queue = [start_url]
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        
        # Create context with a real User Agent (prevents blocking)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        while queue and len(found_urls) < max_pages:
            current_url = queue.pop(0)
            
            try:
                print(f"🔍 Visiting: {current_url}")
                
                # 1. Visit the page
                # wait_until="domcontentloaded" is faster than "networkidle" but still waits for HTML
                await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
                
                # 2. Wait a tiny bit for JS frameworks (React/Vue) to render menus
                await page.wait_for_timeout(1000)

                # 3. Extract all links using JavaScript evaluation (Faster/More reliable)
                hrefs = await page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('a[href]'))
                            .map(a => a.href)
                    }
                """)

                # 4. Process and Filter Links
                for href in hrefs:
                    # Clean the URL
                    full_url = urljoin(current_url, href).split('#')[0].rstrip('/')
                    parsed = urlparse(full_url)
                    current_domain = parsed.netloc.replace('www.', '')  # QA Fix: Normalize domain

                    # Logic: Internal Domain ONLY + Not a file + Not already found
                    if (current_domain == base_domain and 
                        parsed.scheme in ['http', 'https'] and
                        not any(full_url.lower().endswith(ext) for ext in IGNORED_EXTENSIONS) and
                        full_url not in found_urls):
                        
                        found_urls.add(full_url)
                        queue.append(full_url)
                        
                        # Stop immediately if we hit the limit
                        if len(found_urls) >= max_pages:
                            break

            except Exception as e:
                print(f"⚠️ Error crawling {current_url}: {e}")
                continue

        await browser.close()

    print(f"✅ CRAWLER: Finished. Found {len(found_urls)} pages.")
    return list(found_urls)