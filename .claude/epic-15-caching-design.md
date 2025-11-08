# Epic 15.1 - Caching Layer Design

## Overview

The caching layer provides response caching to avoid duplicate LLM API calls while respecting TTL and storage limits.

## Design Decisions

### 1. Cache Key Generation

**Decision**: Hash-based with semantic normalization

```python
def generate_cache_key(provider: str, model: str, prompt: str, **kwargs) -> str:
    """Generate cache key from request parameters"""
    key_data = {
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 2000),
        # Include other relevant parameters
    }
    # Use SHA256 hash to keep key size reasonable
    key_str = json.dumps(key_data, sort_keys=True)
    return f"cache:{hashlib.sha256(key_str.encode()).hexdigest()}"
```

**Rationale**:
- Deterministic and repeatable
- Handles all parameter combinations
- Keeps filesystem paths manageable (hashes instead of full text)
- Namespace with "cache:" prefix to avoid collisions

### 2. Storage Backend

**Decision**: File-based (primary) with in-memory option

```
.questfoundry/cache/
├── <hash-prefix-1>/
│   ├── <full-hash>.json          # Cached response
│   └── <full-hash>.meta.json     # Metadata (ttl, timestamp, cost)
├── <hash-prefix-2>/
...
```

**Rationale**:
- Simple and reliable
- No external dependencies
- Easy to inspect and debug
- Can be version controlled (via .gitignore)
- Scales to ~100k responses per prefix before performance issues
- Future: Redis backend can be added as alternative

### 3. Metadata Storage

Each cached response includes metadata:
```json
{
    "timestamp": 1700000000,
    "ttl_seconds": 86400,
    "expires_at": 1700086400,
    "request_tokens": 150,
    "response_tokens": 250,
    "cost_usd": 0.0075,
    "provider": "openai",
    "model": "gpt-4o"
}
```

### 4. Cache Invalidation

**Strategy**: TTL-based with size limits

- Per-response TTL (default: 24 hours)
- Per-provider TTL override possible
- Background cleanup thread runs every hour
- Size-based eviction: Remove oldest entries when cache exceeds size limit
- LRU for entries of same age

### 5. Thread Safety

**Decision**: File locks with atomic writes

```python
class FileCache:
    def get(self, key: str) -> Optional[str]:
        # Lock file for reading
        # Check if expired
        # Return or cleanup

    def set(self, key: str, value: str, ttl: int):
        # Use temporary file + atomic rename
        # Write metadata
        # Update index (optional)
```

## Implementation Details

### ResponseCache Class

```python
class ResponseCache:
    """File-based response cache with TTL support"""

    def __init__(self, cache_dir: Path = None, ttl_seconds: int = 86400):
        self.cache_dir = cache_dir or Path.cwd() / ".questfoundry" / "cache"
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key"""
        # Use first 2 chars of key for prefix directory
        prefix = key[:2]
        return self.cache_dir / prefix / f"{key}.json"

    def _get_metadata_path(self, key: str) -> Path:
        """Get file path for cache metadata"""
        prefix = key[:2]
        return self.cache_dir / prefix / f"{key}.meta.json"

    def get(self, key: str) -> Optional[str]:
        """Get cached response if not expired"""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        if not cache_path.exists():
            return None

        # Check if expired
        try:
            metadata = json.loads(meta_path.read_text())
            if time.time() > metadata["expires_at"]:
                # Clean up expired entries
                cache_path.unlink()
                meta_path.unlink()
                return None

            # Cache hit
            return cache_path.read_text()
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return None

    def set(self, key: str, value: str, ttl: int = None):
        """Store response with metadata"""
        ttl = ttl or self.ttl_seconds
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        # Create directory if needed
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Write cache file (atomic)
        temp_file = cache_path.with_suffix('.tmp')
        temp_file.write_text(value)
        temp_file.replace(cache_path)

        # Write metadata
        now = time.time()
        metadata = {
            "timestamp": now,
            "ttl_seconds": ttl,
            "expires_at": now + ttl,
        }
        meta_path.write_text(json.dumps(metadata))

    def clear(self):
        """Clear all cached entries"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_expired(self):
        """Remove expired cache entries"""
        if not self.cache_dir.exists():
            return

        for meta_file in self.cache_dir.rglob("*.meta.json"):
            try:
                metadata = json.loads(meta_file.read_text())
                if time.time() > metadata["expires_at"]:
                    cache_file = meta_file.with_suffix('')
                    meta_file.unlink(missing_ok=True)
                    cache_file.unlink(missing_ok=True)
            except (json.JSONDecodeError, KeyError):
                # Clean up corrupted files
                meta_file.unlink(missing_ok=True)

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.cache_dir.exists():
            return {"entries": 0, "total_size_mb": 0}

        total_size = 0
        count = 0
        for cache_file in self.cache_dir.rglob("*.json"):
            if ".meta.json" not in str(cache_file):
                count += 1
                total_size += cache_file.stat().st_size

        return {
            "entries": count,
            "total_size_mb": total_size / (1024 * 1024),
        }
```

### CacheConfig Class

```python
@dataclass
class CacheConfig:
    """Configuration for response caching"""
    enabled: bool = True
    backend: str = "file"  # "file", "memory", future: "redis"
    cache_dir: Path = None
    ttl_seconds: int = 86400  # 24 hours
    max_cache_size_mb: int = 500
    cleanup_interval_seconds: int = 3600  # 1 hour

    per_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Example: {"openai": {"ttl_seconds": 172800}, "ollama": {"enabled": False}}

    @classmethod
    def from_dict(cls, data: dict) -> "CacheConfig":
        """Create from configuration dictionary"""
        data = data.copy()
        if "cache_dir" in data and isinstance(data["cache_dir"], str):
            data["cache_dir"] = Path(data["cache_dir"])
        return cls(**data)

    def get_ttl_for_provider(self, provider: str) -> int:
        """Get TTL for specific provider"""
        provider_config = self.per_provider.get(provider, {})
        return provider_config.get("ttl_seconds", self.ttl_seconds)

    def is_enabled_for_provider(self, provider: str) -> bool:
        """Check if caching enabled for provider"""
        if not self.enabled:
            return False
        provider_config = self.per_provider.get(provider, {})
        return provider_config.get("enabled", True)
```

### Integration with Providers

```python
# In Provider base class

class Provider(ABC):
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.cache = ResponseCache() if config.get("caching_enabled") else None

    def _get_cache_key(
        self,
        method: str,
        prompt: str,
        **params
    ) -> str:
        """Generate cache key for request"""
        from questfoundry.providers.cache import generate_cache_key
        return generate_cache_key(
            self.__class__.__name__,
            self.get_model_name(),
            prompt,
            **params
        )

class TextProvider(Provider):
    def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text with caching"""
        cache_key = self._get_cache_key("text", prompt, model=model, **kwargs)

        # Check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # Call actual implementation
        response = self._generate_text_uncached(prompt, model, **kwargs)

        # Store in cache
        if self.cache:
            ttl = self.config.get("cache_ttl_seconds", 86400)
            self.cache.set(cache_key, response, ttl)

        return response

    @abstractmethod
    def _generate_text_uncached(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Actual text generation (implement in subclass)"""
        pass
```

## Testing Strategy

### Unit Tests

```python
def test_cache_key_generation():
    """Test cache key consistency"""
    key1 = generate_cache_key("openai", "gpt-4", "hello")
    key2 = generate_cache_key("openai", "gpt-4", "hello")
    assert key1 == key2

def test_cache_get_set():
    """Test basic cache operations"""
    cache = ResponseCache()
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

def test_cache_expiration():
    """Test TTL expiration"""
    cache = ResponseCache(ttl_seconds=1)
    cache.set("key", "value")
    time.sleep(1.1)
    assert cache.get("key") is None

def test_cache_concurrent_access():
    """Test thread-safe operations"""
    # Test concurrent reads/writes
    pass
```

## Configuration Example

```yaml
# .questfoundry/config.yml
caching:
  enabled: true
  backend: file
  cache_dir: .questfoundry/cache
  ttl_seconds: 86400
  max_cache_size_mb: 500
  cleanup_interval_seconds: 3600

  # Per-provider overrides
  per_provider:
    openai:
      ttl_seconds: 172800  # 48 hours
    ollama:
      enabled: false  # Don't cache local LLM responses
    gemini:
      ttl_seconds: 86400
```

## Future Enhancements

1. **Redis Backend**: For distributed caching
2. **Cache Warming**: Pre-populate cache for common queries
3. **Cache Analytics**: Track hit rates, cost savings
4. **Semantic Deduplication**: Group similar prompts
5. **Compression**: Compress large responses
6. **Distributed Cache**: Sync cache across machines
