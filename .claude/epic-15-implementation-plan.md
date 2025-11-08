# Epic 15: Advanced Features & Polish - Implementation Plan

**Status:** Preparation Phase
**Branch:** `claude/prepare-epic-15-011CUv8xFd5KZHEj5Ugd8rcx`
**Estimated Effort:** 4-5 days
**Priority:** LOW (Production Readiness Enhancements)

## Overview

Epic 15 is the final phase of the QuestFoundry library completion roadmap, focusing on production readiness enhancements. It consists of four sub-epics:

1. **15.1: Provider Caching & Rate Limiting** - Response caching and API usage control
2. **15.2: Per-Role Provider Configuration** - Role-specific provider selection
3. **15.3: Advanced State Management** - Redis backend and migrations
4. **15.4: Comprehensive Test Suite** - Integration and performance tests

---

## Sub-Epic 15.1: Provider Caching & Rate Limiting

### Goal
Avoid duplicate LLM API calls and respect API rate limits while tracking costs.

### Architecture

#### Caching Layer (`src/questfoundry/providers/cache.py`)
- **Cache Key Generation**: Hash of (provider, model, prompt, temperature, max_tokens)
- **Storage Backend**: File-based cache in `.questfoundry/cache/` by default
- **TTL**: Configurable per provider (default: 24 hours)
- **Size Limits**: Per-provider cache size and total cache size limits

```python
class ResponseCache:
    """In-memory/file-based response caching"""
    - get(key: str) -> Optional[str]
    - set(key: str, value: str, ttl: int)
    - clear()
    - cleanup_expired()

class CacheConfig:
    """Configuration for caching behavior"""
    - enabled: bool
    - backend: "memory" | "file"  # Future: "redis"
    - cache_dir: Path
    - ttl_seconds: int
    - max_cache_size_mb: int
    - per_provider_settings: Dict[str, CacheConfig]
```

#### Rate Limiting (`src/questfoundry/providers/rate_limiter.py`)
- **Token Bucket Algorithm**: Track requests per time window
- **Per-Provider Limits**: Different limits for different APIs
- **Graceful Degradation**: Return cached response or queue request if rate limited
- **Cost Tracking**: Monitor API usage and costs

```python
class RateLimiter:
    """Rate limiting and cost tracking"""
    - acquire(cost: float) -> bool  # Async-friendly
    - check_limit(cost: float) -> bool
    - record_usage(cost: float)
    - get_stats() -> RateLimitStats

class RateLimitConfig:
    """Per-provider rate limit configuration"""
    - requests_per_minute: int
    - tokens_per_hour: int
    - cost_per_request: float
    - cost_per_token: float

class CostTracker:
    """Track API usage and costs"""
    - record_request(provider: str, tokens: int)
    - get_total_cost() -> float
    - get_cost_by_provider() -> Dict[str, float]
```

#### Retry Logic (`src/questfoundry/providers/base.py` extension)
- **Exponential Backoff**: 2^n seconds with jitter (max 60s)
- **Retry Count**: 3 retries by default
- **Retriable Errors**: Network errors, rate limit errors (429), temporary failures (5xx)
- **Non-Retriable Errors**: Auth errors (401, 403), not found (404), bad request (400)

### Implementation Files

```
src/questfoundry/providers/cache.py          # Response cache implementation
src/questfoundry/providers/rate_limiter.py   # Rate limiting & cost tracking
tests/providers/test_cache.py                # Cache unit tests
tests/providers/test_rate_limiter.py         # Rate limiter unit tests
tests/providers/test_provider_integration.py # Integration with providers
```

### Configuration

```yaml
# .questfoundry/config.yml
caching:
  enabled: true
  backend: file  # or "memory"
  cache_dir: .questfoundry/cache
  ttl_seconds: 86400  # 24 hours
  max_cache_size_mb: 500

rate_limiting:
  global:
    requests_per_minute: 100
    tokens_per_hour: 100000
  providers:
    openai:
      requests_per_minute: 90
      tokens_per_hour: 90000
      cost_per_1k_tokens: 0.03
    ollama:
      requests_per_minute: 1000  # Local, no limits
      tokens_per_hour: 1000000
      cost_per_1k_tokens: 0.0

retry:
  enabled: true
  max_retries: 3
  initial_delay_ms: 1000
  max_delay_ms: 60000
```

### Integration Points

1. **TextProvider base class**: Wrap `generate_text` calls with caching/rate limiting
2. **ImageProvider base class**: Similar wrapping for image generation
3. **AudioProvider base class**: Similar wrapping for audio generation
4. **All provider implementations**: Use wrapper automatically

### Testing Strategy

- Cache hit/miss scenarios
- TTL expiration
- Rate limit enforcement (token bucket)
- Cost accumulation
- Retry logic with exponential backoff
- Integration with real providers (e.g., mock OpenAI)

### Success Criteria

- ✅ Cached responses used when available
- ✅ Rate limits respected (token bucket)
- ✅ API costs tracked per provider
- ✅ Retries work correctly with exponential backoff
- ✅ No performance degradation

---

## Sub-Epic 15.2: Per-Role Provider Configuration

### Goal
Allow different roles to use different providers/models based on configuration.

### Architecture

#### Configuration Schema Extension

```yaml
# .questfoundry/config.yml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    ollama:
      base_url: http://localhost:11434
      model: llama3

# NEW: Per-role configuration
roles:
  scene_smith:
    provider: openai
    model: gpt-4o
    max_tokens: 3000
    temperature: 0.8

  gatekeeper:
    provider: ollama  # Use local Ollama instead
    model: llama3
    temperature: 0.2  # Very deterministic for validation

  illustrator:
    provider: dalle
    model: dall-e-3

  audio_director:
    provider: elevenlabs
    voice: nova
```

#### ProviderConfig Enhancement (`src/questfoundry/providers/config.py`)

```python
def get_role_provider(
    self,
    role_name: str,
    provider_type: str
) -> str:
    """Get provider name for a specific role"""
    # Check role-specific config first
    # Fall back to default if not found

def get_role_config(
    self,
    role_name: str
) -> Dict[str, Any]:
    """Get all configuration for a role"""
    # Returns provider, model, temperature, etc.

def get_provider_for_role(
    self,
    role_name: str,
    provider_type: str = "text"
) -> TextProvider | ImageProvider:
    """Get configured provider instance for a role"""
```

#### Role Base Class Enhancement (`src/questfoundry/roles/base.py`)

```python
class Role(ABC):
    def __init__(
        self,
        provider: TextProvider,
        spec_path: Path | None = None,
        config: dict[str, Any] | None = None,
        session: "RoleSession | None" = None,
        human_callback: "HumanCallback | None" = None,
        role_specific_config: dict[str, Any] | None = None,  # NEW
    ):
        # Store role-specific configuration
        self.role_specific_config = role_specific_config or {}

        # Use role config if available
        if self.role_specific_config.get("model"):
            self.default_model = self.role_specific_config["model"]

        if self.role_specific_config.get("temperature"):
            self.default_temperature = self.role_specific_config["temperature"]
```

#### Showrunner Integration (`src/questfoundry/roles/showrunner.py`)

The Showrunner will be updated to:
1. Load role-specific provider configuration
2. Instantiate each role with its configured provider
3. Fall back to default provider if not specified

```python
class Showrunner:
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._roles: Dict[str, Role] = {}

    def _initialize_role(self, role_class: Type[Role], role_name: str) -> Role:
        """Initialize role with its specific provider"""
        # Get role's provider config
        provider_name = self.config.get_role_provider(role_name, "text")
        provider = self._get_provider(provider_name)

        # Get role-specific config
        role_config = self.config.get_role_config(role_name)

        # Create role with its provider
        return role_class(
            provider=provider,
            config=role_config,
            role_specific_config=role_config
        )
```

### Implementation Files

```
src/questfoundry/providers/config.py  # Extended config handling
src/questfoundry/roles/base.py        # Role config support
src/questfoundry/roles/showrunner.py  # Showrunner integration
tests/roles/test_per_role_config.py   # Configuration tests
```

### Configuration Extension

Extend the existing config.yml with a new `roles` section (see above).

### Testing Strategy

- Load role-specific config
- Verify role gets correct provider
- Test fallback to default
- Test model/temperature override
- Integration test with multiple roles

### Success Criteria

- ✅ Can configure provider per role
- ✅ Configuration falls back to default if not specified
- ✅ All roles respect their configured provider
- ✅ Per-role max_tokens and temperature work

---

## Sub-Epic 15.3: Advanced State Management

### Goal
Provide distributed state management and schema migration capabilities.

### Architecture

#### State Migration System (`src/questfoundry/state/migration.py`)

```python
class Migration(ABC):
    """Base class for state migrations"""
    version: int

    @abstractmethod
    def upgrade(self, state: Dict) -> Dict:
        """Upgrade state from previous version"""
        pass

    @abstractmethod
    def downgrade(self, state: Dict) -> Dict:
        """Downgrade state to previous version"""
        pass

class MigrationManager:
    """Manage state schema versions and migrations"""
    - register_migration(migration: Migration)
    - get_current_version() -> int
    - migrate(state: Dict, target_version: int) -> Dict
    - create_migration_backup(path: Path)
```

#### Redis State Store (`src/questfoundry/state/redis_store.py`)

```python
class RedisStore(StateStore):
    """Redis/Valkey backend for distributed state"""
    - get(key: str) -> Any
    - set(key: str, value: Any)
    - delete(key: str)
    - list_keys(pattern: str) -> List[str]
    - watch(keys: List[str]) -> ContextManager  # Transaction support

    # Connection pooling and TTL support
```

#### State Export/Import (`src/questfoundry/state/store.py` extension)

```python
class StateStore(ABC):
    def export(self, path: Path, include_history: bool = False):
        """Export state to file (JSON/YAML)"""

    def import_state(self, path: Path, merge: bool = False):
        """Import state from file"""
```

### Implementation Files

```
src/questfoundry/state/migration.py           # Migration system
src/questfoundry/state/redis_store.py         # Redis backend
tests/state/test_migration.py                 # Migration tests
tests/state/test_redis_store.py               # Redis tests
tests/state/test_export_import.py             # Export/import tests
```

### Configuration

```yaml
# .questfoundry/config.yml
state:
  backend: file  # or "redis" | "memory"
  file_path: .questfoundry/state.json
  redis:
    host: localhost
    port: 6379
    db: 0
    password: ${REDIS_PASSWORD}  # Optional
  retention:
    keep_backups: 5
    backup_interval_hours: 24
```

### Testing Strategy

- Migration version handling
- State upgrade/downgrade
- Redis connection and operations
- Export/import round-trip
- Distributed state consistency

### Success Criteria

- ✅ Redis backend works
- ✅ Migrations handle version changes
- ✅ Can export/import project state
- ✅ State consistency in distributed scenarios

---

## Sub-Epic 15.4: Comprehensive Test Suite

### Goal
Achieve high test coverage with integration and performance tests.

### Architecture

#### Integration Tests (`tests/integration/`)

```
test_end_to_end.py           # Full workflow tests
test_multi_loop.py           # Multiple loops in sequence
test_error_recovery.py       # Error handling and recovery
```

**test_end_to_end.py**: Complete workflow from project creation to completion
- Create minimal project
- Run all loops in sequence
- Verify artifacts at each step
- Check final output quality

**test_multi_loop.py**: Multiple loops with state preservation
- Run loop A → produce artifacts → Run loop B → verify
- Test artifact dependencies between loops
- Verify session state persistence

**test_error_recovery.py**: Error handling
- Network failures
- Provider errors (auth, rate limit, etc.)
- Invalid input handling
- Retry logic verification

#### Performance Tests (`tests/performance/`)

```
test_large_project.py           # Scale testing
test_provider_performance.py    # Provider-specific benchmarks
test_cache_performance.py       # Caching impact
```

**test_large_project.py**: Performance with larger projects
- Large TUs (many scenes)
- Deep story graphs
- Memory usage monitoring
- Response time benchmarks

**test_provider_performance.py**: Compare providers
- OpenAI vs Ollama response times
- Token efficiency comparison
- Cost comparison

**test_cache_performance.py**: Cache effectiveness
- Cache hit rate
- Response time improvement
- Storage overhead

#### Provider Integration Tests

```
tests/providers/test_openai_integration.py
tests/providers/test_ollama_integration.py
tests/providers/test_gemini_integration.py
tests/providers/test_bedrock_integration.py
tests/providers/test_dalle_integration.py
tests/providers/test_elevenlabs_integration.py
```

### Implementation Strategy

1. **Phase 1**: Unit tests for new modules (cache, rate_limiter, migration)
2. **Phase 2**: Integration tests (end-to-end, multi-loop)
3. **Phase 3**: Performance tests and benchmarks
4. **Phase 4**: Real provider integration tests

### Testing Tools & Practices

- Use `pytest` for test framework
- Use `pytest-asyncio` for async tests
- Use `pytest-benchmark` for performance tests
- Use `responses` library for mocking HTTP
- Use fixtures for common setup
- Aim for >80% code coverage

### Success Criteria

- ✅ Full workflow tested end-to-end
- ✅ Error cases covered
- ✅ Performance acceptable (benchmarks)
- ✅ All providers tested with real APIs
- ✅ >80% code coverage

---

## Implementation Sequencing

### Phase 1: Foundation (Day 1-2)
1. **15.1 - Cache Layer**
   - Create `cache.py` with ResponseCache class
   - File-based storage implementation
   - Configuration integration

2. **15.1 - Rate Limiting**
   - Create `rate_limiter.py` with token bucket
   - CostTracker implementation
   - Config schema

### Phase 2: Provider Integration (Day 2-3)
3. **15.1 - Provider Integration**
   - Integrate cache & rate limiter into Provider base
   - Add retry logic wrapper
   - Update all provider implementations

4. **15.2 - Per-Role Configuration**
   - Extend ProviderConfig
   - Update Role base class
   - Update Showrunner

### Phase 3: Advanced Features (Day 3-4)
5. **15.3 - State Management**
   - Migration system
   - Redis store (optional/future)
   - Export/import utilities

### Phase 4: Testing (Day 4-5)
6. **15.4 - Test Suite**
   - Unit tests for all new modules
   - Integration tests
   - Performance tests

---

## Acceptance Criteria Summary

### 15.1: Caching & Rate Limiting
- ✅ Response caching works with TTL
- ✅ Rate limits enforced (token bucket)
- ✅ API costs tracked accurately
- ✅ Retries work with exponential backoff
- ✅ No requests sent when rate limited
- ✅ Configuration documented

### 15.2: Per-Role Configuration
- ✅ Can specify provider per role in config
- ✅ Falls back to default if not specified
- ✅ All roles use their configured provider
- ✅ Model, temperature overridable per role
- ✅ Backward compatible with existing configs

### 15.3: Advanced State Management
- ✅ Redis backend implemented and tested
- ✅ Migration system handles version changes
- ✅ State can be exported and imported
- ✅ No data loss on schema updates
- ✅ Distributed state consistency

### 15.4: Comprehensive Tests
- ✅ End-to-end workflow tests
- ✅ Error recovery tests
- ✅ Performance benchmarks
- ✅ >80% code coverage
- ✅ Provider integration tests
- ✅ Multi-loop tests

---

## Dependencies & Prerequisites

### Internal
- All previous epics (11-14) must be complete
- Existing provider implementations
- Existing role implementations

### External
- Python 3.10+ with async/await support
- Redis/Valkey (optional, for distributed deployments)
- pytest, pytest-asyncio, pytest-benchmark

### Knowledge
- Token bucket algorithm (rate limiting)
- Cache invalidation strategies
- Database migration patterns
- Python async programming

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Cache invalidation complexity | Keep cache implementation simple, TTL-based |
| Rate limit accuracy | Use well-tested token bucket library or implementation |
| Config schema backward compatibility | Maintain default values, fallback mechanism |
| Redis dependency | Make optional, file-based default works fine |
| Performance regression | Benchmark before/after, profile hotspots |

---

## Success Metrics

1. **Code Quality**: >80% test coverage, 0 critical issues
2. **Performance**: No regression on existing workflows
3. **User Experience**: Config file unchanged (backward compatible)
4. **Reliability**: All tests passing, no flaky tests
5. **Documentation**: README and examples updated

---

## Next Steps

1. Create directory structure for new modules
2. Design and implement cache layer
3. Design and implement rate limiter
4. Integrate with providers
5. Implement per-role configuration
6. Add comprehensive test suite
7. Documentation and examples
8. Final review and PR creation
