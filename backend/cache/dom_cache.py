# backend/cache/dom_cache.py
"""
DOM Fingerprinting for cache consistency.
Creates a stable hash of page content, ignoring dynamic elements.
"""
import hashlib
import re


def compute_dom_hash(html: str) -> str:
    """
    Create a stable fingerprint of page structure.
    Same structural content = Same hash.
    
    Ignores:
    - <script> tags (JavaScript)
    - <iframe> tags (ads, embeds)
    - data-* attributes (session IDs, timestamps)
    - Extra whitespace
    - Comments
    """
    # Remove script tags and content
    clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove iframe tags and content
    clean = re.sub(r'<iframe[^>]*>.*?</iframe>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove noscript tags
    clean = re.sub(r'<noscript[^>]*>.*?</noscript>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags (can be dynamic)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    clean = re.sub(r'<!--.*?-->', '', clean, flags=re.DOTALL)
    
    # Remove data-* attributes (often contain session/timestamp data)
    clean = re.sub(r'\s+data-[a-zA-Z0-9_-]+="[^"]*"', '', clean)
    
    # Remove id attributes that look like session IDs (long alphanumeric)
    clean = re.sub(r'\s+id="[a-zA-Z0-9]{20,}"', '', clean)
    
    # Normalize whitespace
    clean = re.sub(r'\s+', ' ', clean)
    
    # Remove leading/trailing whitespace
    clean = clean.strip()
    
    # SHA-256 hash
    return hashlib.sha256(clean.encode('utf-8')).hexdigest()


def is_same_dom(hash1: str, hash2: str) -> bool:
    """Check if two DOM hashes match."""
    return hash1 == hash2
