"""
File-based caching system with TTL support.

Provides simple key-value caching with time-to-live expiration.
Cache files are stored in ~/.anomradar/cache by default.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

from anomradar.core.logging import get_logger


logger = get_logger()


class Cache:
    """
    File-based cache with TTL support.
    
    Each cache entry is stored as a separate JSON file with metadata.
    Cache keys are hashed to create safe filenames.
    """
    
    def __init__(self, cache_dir: str = "~/.anomradar/cache", ttl: int = 3600, enabled: bool = True):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live in seconds (default: 1 hour)
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.ttl = ttl
        self.enabled = enabled
        
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Cache initialized: {self.cache_dir} (TTL: {self.ttl}s)")
    
    def _get_cache_path(self, key: str) -> Path:
        """
        Get cache file path for a key.
        
        Args:
            key: Cache key
        
        Returns:
            Path to cache file
        """
        # Hash the key to create a safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found or expired
        """
        if not self.enabled:
            return None
        
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            logger.debug(f"Cache miss: {key}")
            return None
        
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() - data["timestamp"] > self.ttl:
                logger.debug(f"Cache expired: {key}")
                cache_path.unlink()
                return None
            
            logger.debug(f"Cache hit: {key}")
            return data["value"]
        
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                "key": key,
                "value": value,
                "timestamp": time.time()
            }
            
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Cache set: {key}")
            return True
        
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted, False if not found
        """
        if not self.enabled:
            return False
        
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            try:
                cache_path.unlink()
                logger.debug(f"Cache deleted: {key}")
                return True
            except Exception as e:
                logger.warning(f"Cache delete error for {key}: {e}")
                return False
        
        return False
    
    def clear(self) -> int:
        """
        Clear all cache files.
        
        Returns:
            Number of files deleted
        """
        if not self.enabled:
            return 0
        
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            logger.info(f"Cache cleared: {count} files deleted")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
        
        return count
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of expired entries removed
        """
        if not self.enabled:
            return 0
        
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                    
                    if time.time() - data["timestamp"] > self.ttl:
                        cache_file.unlink()
                        count += 1
                except Exception:
                    # If we can't read it, delete it
                    cache_file.unlink()
                    count += 1
            
            if count > 0:
                logger.info(f"Cache cleanup: {count} expired entries removed")
        except Exception as e:
            logger.warning(f"Cache cleanup error: {e}")
        
        return count
