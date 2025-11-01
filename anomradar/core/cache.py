"""File-based caching with TTL support for AnomRadar v2"""

import json
import time
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class CacheEntry:
    """Represents a cached item with TTL"""
    value: Any
    timestamp: float
    ttl: int
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.timestamp > self.ttl


class FileCache:
    """File-based cache with TTL support
    
    Caches data to ~/.anomradar/cache with configurable TTL.
    Each cache entry is stored as a separate JSON file.
    """
    
    def __init__(self, cache_dir: str, default_ttl: int = 3600):
        """Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for a key"""
        # Hash the key to create a safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                entry = CacheEntry(**data)
                
                if entry.is_expired():
                    # Clean up expired entry
                    cache_path.unlink(missing_ok=True)
                    return None
                
                return entry.value
        except (json.JSONDecodeError, KeyError, OSError):
            # If cache is corrupted, remove it
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with TTL
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if not provided)
        """
        cache_path = self._get_cache_path(key)
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl
        )
        
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'value': entry.value,
                    'timestamp': entry.timestamp,
                    'ttl': entry.ttl
                }, f)
        except (OSError, TypeError) as e:
            # Silently fail if caching fails
            pass
    
    def delete(self, key: str) -> None:
        """Delete cache entry
        
        Args:
            key: Cache key to delete
        """
        cache_path = self._get_cache_path(key)
        cache_path.unlink(missing_ok=True)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)
    
    def cleanup_expired(self) -> int:
        """Remove all expired cache entries
        
        Returns:
            Number of expired entries removed
        """
        removed = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    entry = CacheEntry(**data)
                    
                    if entry.is_expired():
                        cache_file.unlink()
                        removed += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Remove corrupted cache files
                cache_file.unlink(missing_ok=True)
                removed += 1
        
        return removed
