# backend/cache/redis_cache.py
"""
Redis cache using Upstash for audit result caching.
"""
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Upstash Redis configuration
UPSTASH_URL = os.getenv("UPSTASH_REDIS_URL", "https://present-terrier-6082.upstash.io")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

# Cache TTL in seconds (24 hours)
CACHE_TTL = 86400

# Initialize Redis client
redis_client = None

try:
    from upstash_redis import Redis
    if UPSTASH_TOKEN:
        redis_client = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)
        print("✅ Redis (Upstash) connected")
    else:
        print("⚠️ UPSTASH_REDIS_TOKEN not set, using in-memory cache")
except ImportError:
    print("⚠️ upstash-redis not installed, using in-memory cache")

# Fallback in-memory cache
_memory_cache: Dict[str, Any] = {}


def _get_cache_key(url: str, dom_hash: str) -> str:
    """Generate cache key from URL and DOM hash."""
    return f"audit:{dom_hash[:16]}:{url[:100]}"


def get_cached_result(url: str, dom_hash: str) -> Optional[Dict]:
    """
    Get cached audit result if exists.
    Returns None if not found or expired.
    """
    cache_key = _get_cache_key(url, dom_hash)
    
    if redis_client:
        # Use Upstash Redis
        try:
            cached = redis_client.get(cache_key)
            if cached:
                print(f"✅ Cache HIT for {url[:50]}...")
                if isinstance(cached, str):
                    return json.loads(cached)
                return cached
        except Exception as e:
            print(f"⚠️ Redis error: {e}")
    else:
        # Fallback to in-memory
        if cache_key in _memory_cache:
            print(f"✅ Memory cache HIT for {url[:50]}...")
            return _memory_cache[cache_key]
    
    print(f"❌ Cache MISS for {url[:50]}...")
    return None


def save_cached_result(url: str, dom_hash: str, result: Dict) -> bool:
    """
    Save audit result to cache.
    Returns True if saved successfully.
    """
    cache_key = _get_cache_key(url, dom_hash)
    
    if redis_client:
        # Use Upstash Redis with TTL
        try:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
            print(f"💾 Saved to Redis cache: {cache_key[:50]}...")
            return True
        except Exception as e:
            print(f"⚠️ Redis save error: {e}")
    
    # Fallback to in-memory
    _memory_cache[cache_key] = result
    print(f"💾 Saved to memory cache: {cache_key[:50]}...")
    return True


    print("🗑️ Cache cleared")


import hashlib

def _get_url_key(url: str) -> str:
    """Generate time-based cache key from URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"audit:recent:{url_hash}"


def get_recent_audit(url: str) -> Optional[Dict]:
    """
    Get recent audit result for URL (time-based cache).
    """
    cache_key = _get_url_key(url)
    
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                print(f"✅ Time-based Cache HIT for {url[:50]}...")
                if isinstance(cached, str):
                    return json.loads(cached)
                return cached
        except Exception as e:
            print(f"⚠️ Redis error (time-cache): {e}")
    else:
        # Fallback to in-memory
        if cache_key in _memory_cache:
            # Check mock TTL (optional, for now just return if present)
            print(f"✅ Memory Time-Cache HIT for {url[:50]}...")
            return _memory_cache[cache_key]
            
    return None


def save_recent_audit(url: str, result: Dict, ttl: int = 300) -> bool:
    """
    Save audit result to time-based cache (default 5 mins).
    """
    cache_key = _get_url_key(url)
    
    if redis_client:
        try:
            redis_client.setex(cache_key, ttl, json.dumps(result))
            print(f"💾 Saved to Time-based Redis cache: {cache_key} (TTL {ttl}s)")
            return True
        except Exception as e:
            print(f"⚠️ Redis save error (time-cache): {e}")
    
    # Fallback
    _memory_cache[cache_key] = result
    return True
