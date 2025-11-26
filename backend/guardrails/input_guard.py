import re
from urllib.parse import urlparse

# Simple blocklist for demonstration
BLOCKED_DOMAINS = [
    "malicious-site.com",
    "phishing.org",
    "example-blocked.net"
]

def validate_input(state: dict) -> dict:
    """
    Validates the input URL before starting the audit.
    Checks for:
    1. Empty URL
    2. Valid URL format
    3. Blocklisted domains
    """
    url = state.get("url", "")
    print(f"🛡️ INPUT GUARD: Checking {url}...")

    if not url:
        return {"error": "URL is missing"}

    # 1. Basic Format Check
    if not re.match(r'^https?://', url):
        return {"error": "Invalid URL format. Must start with http:// or https://"}

    # 2. Blocklist Check
    try:
        domain = urlparse(url).netloc
        if any(blocked in domain for blocked in BLOCKED_DOMAINS):
            print(f"⛔ INPUT GUARD: Blocked domain detected: {domain}")
            return {"error": f"Domain {domain} is in the blocklist."}
    except Exception as e:
        return {"error": f"URL parsing failed: {str(e)}"}

    print("✅ INPUT GUARD: Passed.")
    return {"url": url}
