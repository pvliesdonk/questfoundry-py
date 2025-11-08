# Epic 15 - Quick Start Guide

## 📋 What's Been Prepared

5 comprehensive design documents have been created:

1. **epic-15-implementation-plan.md** - Overall roadmap
2. **epic-15-caching-design.md** - Response caching architecture
3. **epic-15-rate-limiting-design.md** - Rate limiting & cost tracking
4. **epic-15-per-role-config-design.md** - Per-role provider selection
5. **epic-15-test-plan.md** - Testing strategy

Plus this summary and quick start guide.

## 🎯 Epic 15 Overview

Four interconnected features for production readiness:

| Feature | Benefit | Complexity |
|---------|---------|-----------|
| **15.1: Caching** | Avoid duplicate API calls | Medium |
| **15.1: Rate Limiting** | Respect API limits, track costs | Medium |
| **15.2: Per-Role Config** | Use different models per role | Low |
| **15.3: State Management** | Distributed state & migrations | Medium |
| **15.4: Tests** | Comprehensive coverage | High |

## 🚀 Implementation Path (5 Days)

### Day 1: Cache Foundation
```python
# Create: src/questfoundry/providers/cache.py
class ResponseCache:
    - File-based storage with TTL
    - Per-provider configuration
    - Automatic cleanup

# Create: tests/providers/test_cache.py
# 12+ unit tests
```

### Day 2: Rate Limiting
```python
# Create: src/questfoundry/providers/rate_limiter.py
class RateLimiter:
    - Token bucket algorithm
    - Multi-level limits (requests, tokens, cost)
    - Usage tracking

class CostTracker:
    - Cost per provider/model
    - Daily/monthly aggregation
    - Cost summaries

# Create: tests/providers/test_rate_limiter.py
# 15+ unit tests
```

### Day 3: Configuration
```python
# Extend: src/questfoundry/providers/config.py
def get_role_provider_name(role_name)
def get_role_config(role_name)
def get_role_parameter(role_name, param)

# Extend: src/questfoundry/roles/base.py
# Add role_config parameter support

# Create: tests/roles/test_per_role_config.py
# 8+ configuration tests
```

### Day 4: State Management
```python
# Create: src/questfoundry/state/migration.py
class MigrationManager:
    - Handle schema version changes
    - Upgrade/downgrade state

# Create: src/questfoundry/state/redis_store.py
# Optional Redis backend

# Create: tests/state/test_migration.py
```

### Day 5: Testing & Polish
```python
# Create: tests/integration/test_end_to_end.py
# Create: tests/integration/test_multi_loop.py
# Create: tests/performance/test_cache_performance.py
# Create: tests/performance/test_large_project.py

# Run full test suite, achieve >80% coverage
```

## 🔧 Key Implementation Details

### Cache Layer
```python
# Simple usage pattern:
cache.set("key", "value", ttl=86400)
cached_value = cache.get("key")  # Returns None if expired

# Automatic integration with providers
class TextProvider:
    def generate_text(self, prompt, **kwargs):
        # 1. Check cache
        if response := self._get_cached(prompt, **kwargs):
            return response
        # 2. Generate
        response = self._generate_uncached(prompt, **kwargs)
        # 3. Cache
        self._cache_response(prompt, response, **kwargs)
        return response
```

### Rate Limiting
```python
# Token bucket pattern:
limiter = RateLimiter(config)

# Check before request
if not limiter.check_limit(tokens=100):
    raise RateLimitError("Would exceed limit")

# Make request
response = provider.generate_text(prompt)

# Record usage
limiter.record_usage(input_tokens=100, output_tokens=50)
```

### Per-Role Config
```yaml
roles:
  scene_smith:
    provider: openai      # Use OpenAI for creative work
    model: gpt-4o
    temperature: 0.8

  gatekeeper:
    provider: ollama      # Use local model for validation
    model: llama3
    temperature: 0.2
```

```python
# Automatic in Showrunner:
role = showrunner.get_role("scene_smith")
# → Uses OpenAI with gpt-4o

role = showrunner.get_role("gatekeeper")
# → Uses Ollama with llama3
```

## 📊 Success Metrics

**Caching**
- ✓ Cache hit rate >50% in typical workflows
- ✓ No expired responses returned
- ✓ Automatic cleanup of stale entries

**Rate Limiting**
- ✓ Requests denied when limits would be exceeded
- ✓ Costs tracked accurately
- ✓ Tokens refill per configured schedule

**Configuration**
- ✓ Each role uses its configured provider
- ✓ Falls back to default if not specified
- ✓ Backward compatible (no breaking changes)

**Testing**
- ✓ >80% code coverage
- ✓ All critical paths tested
- ✓ Performance benchmarks established

## 🧪 Running Tests

```bash
# Unit tests only
pytest tests/providers/test_cache.py -v
pytest tests/providers/test_rate_limiter.py -v
pytest tests/roles/test_per_role_config.py -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v --benchmark-only

# Full suite with coverage
pytest tests/ --cov=src/questfoundry --cov-report=html
```

## 📝 Configuration Example

Minimal config to enable all features:

```yaml
# .questfoundry/config.yml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o

roles:
  scene_smith:
    provider: openai
    temperature: 0.8

caching:
  enabled: true
  ttl_seconds: 86400

rate_limiting:
  global:
    requests_per_minute: 100
  providers:
    openai:
      requests_per_minute: 90
      cost_per_input_token: 0.00002
      cost_per_output_token: 0.00006
```

## 🎓 Key Classes to Implement

### src/questfoundry/providers/cache.py
- `ResponseCache` - Main cache class
- `CacheConfig` - Configuration dataclass
- `generate_cache_key()` - Utility function

### src/questfoundry/providers/rate_limiter.py
- `RateLimiter` - Token bucket rate limiter
- `RateLimitConfig` - Configuration dataclass
- `CostTracker` - Cost tracking utility

### Extended Classes
- `ProviderConfig` - Add role lookup methods
- `Role` - Add role_config parameter
- `Showrunner` - Implement dynamic role initialization

## 💡 Pro Tips

1. **Start Simple**: Begin with file-based cache, add Redis later
2. **Test First**: Write tests as you implement
3. **Backward Compat**: Don't break existing configs
4. **Provider Caching**: Cache provider instances in Showrunner
5. **Monitoring**: Add logging to rate limiter for debugging

## ⚠️ Common Pitfalls to Avoid

- ❌ Don't cache streaming responses (not applicable here)
- ❌ Don't forget to handle cache expiration
- ❌ Don't lose token count accuracy in rate limiter
- ❌ Don't break existing code without migration path
- ❌ Don't skip unit tests

## 📚 Reference Documents

| Document | Contains |
|----------|----------|
| epic-15-implementation-plan.md | Complete overview & sequencing |
| epic-15-caching-design.md | Full cache implementation spec |
| epic-15-rate-limiting-design.md | Rate limiter & cost tracker spec |
| epic-15-per-role-config-design.md | Config & role integration spec |
| epic-15-test-plan.md | All test cases (50+ tests) |

## 🚀 Getting Started

1. Read this quick start guide
2. Skim `epic-15-implementation-plan.md`
3. Review specific design doc for current phase
4. Create the module files
5. Implement following the design spec
6. Write tests from `epic-15-test-plan.md`
7. Repeat for next phase

## ✅ Ready?

All documentation complete. Architecture validated. Tests designed.

Ready to start implementing! 🎯

---

**Questions?** Check the detailed design documents in `.claude/`
**Phase stuck?** Review the corresponding design document
**Tests failing?** See `epic-15-test-plan.md` for test specs
