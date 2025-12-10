# backend/cache/__init__.py
from .dom_cache import compute_dom_hash
from .redis_cache import redis_client, get_cached_result, save_cached_result
