"""
Cache manager for improving performance by caching expensive operations.
Supports OCR results, embeddings, and financial calculations.
"""
import hashlib
import pickle
import logging
from pathlib import Path
from typing import Any, Optional, Callable
import functools
import time

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for expensive operations"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}
        logger.info(f"Cache manager initialized at {self.cache_dir}")
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate a unique cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file content for cache key"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.warning(f"Could not hash file {file_path}: {e}")
            return str(time.time())
    
    def get(self, key: str, memory_only: bool = False) -> Optional[Any]:
        """Get value from cache"""
        # Check memory cache first
        if key in self.memory_cache:
            logger.debug(f"Cache hit (memory): {key}")
            return self.memory_cache[key]
        
        if memory_only:
            return None
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    value = pickle.load(f)
                # Store in memory cache for faster access
                self.memory_cache[key] = value
                logger.debug(f"Cache hit (disk): {key}")
                return value
            except Exception as e:
                logger.warning(f"Failed to load cache {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, memory_only: bool = False):
        """Set value in cache"""
        # Always store in memory cache
        self.memory_cache[key] = value
        
        if not memory_only:
            # Store in disk cache
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
                logger.debug(f"Cache stored: {key}")
            except Exception as e:
                logger.warning(f"Failed to save cache {key}: {e}")
    
    def invalidate(self, key: str):
        """Invalidate a cache entry"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()
    
    def clear_memory(self):
        """Clear memory cache only"""
        self.memory_cache.clear()
        logger.info("Memory cache cleared")
    
    def clear_all(self):
        """Clear all caches"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("All caches cleared")


def cached(cache_key_fn: Optional[Callable] = None, memory_only: bool = False):
    """
    Decorator for caching function results
    
    Args:
        cache_key_fn: Optional function to generate cache key from args
        memory_only: If True, only use memory cache (not disk)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create cache manager
            if not hasattr(wrapper, '_cache_manager'):
                wrapper._cache_manager = CacheManager()
            
            # Generate cache key
            if cache_key_fn:
                cache_key = cache_key_fn(*args, **kwargs)
            else:
                cache_key = wrapper._cache_manager._get_cache_key(*args, **kwargs)
            
            # Try to get from cache
            result = wrapper._cache_manager.get(cache_key, memory_only)
            if result is not None:
                return result
            
            # Compute and cache result
            result = func(*args, **kwargs)
            wrapper._cache_manager.set(cache_key, result, memory_only)
            
            return result
        
        return wrapper
    return decorator


# Global cache manager instance
_global_cache = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
