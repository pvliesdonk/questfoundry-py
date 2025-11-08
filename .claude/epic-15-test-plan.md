# Epic 15 - Comprehensive Test Plan

## Overview

This test plan covers unit tests, integration tests, and performance tests for all Epic 15 features.

## Test Structure

```
tests/
├── providers/
│   ├── test_cache.py                    # Cache unit tests
│   ├── test_rate_limiter.py             # Rate limiter unit tests
│   ├── test_provider_integration.py     # Provider integration
│   ├── test_openai_integration.py       # Real OpenAI tests (optional)
│   └── test_ollama_integration.py       # Real Ollama tests
├── roles/
│   ├── test_per_role_config.py          # Role configuration tests
│   └── test_role_provider_usage.py      # Verify roles use config
├── state/
│   ├── test_migration.py                # Schema migration tests
│   ├── test_redis_store.py              # Redis backend tests
│   └── test_export_import.py            # Export/import tests
├── integration/
│   ├── test_end_to_end.py               # Full workflow tests
│   ├── test_multi_loop.py               # Multiple loops
│   └── test_error_recovery.py           # Error handling
└── performance/
    ├── test_cache_performance.py        # Cache impact
    ├── test_large_project.py            # Scale testing
    └── test_provider_performance.py     # Provider benchmarks
```

---

## Part 1: Cache Tests (test_cache.py)

### Unit Tests

```python
# Test cache key generation
def test_cache_key_generation_consistent():
    """Same inputs produce same cache key"""
    key1 = generate_cache_key("openai", "gpt-4", "hello")
    key2 = generate_cache_key("openai", "gpt-4", "hello")
    assert key1 == key2

def test_cache_key_generation_different():
    """Different inputs produce different keys"""
    key1 = generate_cache_key("openai", "gpt-4", "hello")
    key2 = generate_cache_key("openai", "gpt-4", "world")
    assert key1 != key2

def test_cache_key_includes_model():
    """Cache key includes model name"""
    key1 = generate_cache_key("openai", "gpt-4", "hello")
    key2 = generate_cache_key("openai", "gpt-3.5", "hello")
    assert key1 != key2

def test_cache_key_includes_temperature():
    """Cache key includes temperature"""
    key1 = generate_cache_key("openai", "gpt-4", "hello", temperature=0.7)
    key2 = generate_cache_key("openai", "gpt-4", "hello", temperature=0.9)
    assert key1 != key2

# Test ResponseCache class
def test_cache_set_get():
    """Basic set and get"""
    cache = ResponseCache()
    try:
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
    finally:
        cache.clear()

def test_cache_miss():
    """Get non-existent key returns None"""
    cache = ResponseCache()
    try:
        assert cache.get("nonexistent") is None
    finally:
        cache.clear()

def test_cache_overwrite():
    """Overwriting key updates value"""
    cache = ResponseCache()
    try:
        cache.set("key", "value1")
        cache.set("key", "value2")
        assert cache.get("key") == "value2"
    finally:
        cache.clear()

def test_cache_expiration():
    """Cached items expire after TTL"""
    cache = ResponseCache(ttl_seconds=1)
    try:
        cache.set("key", "value")
        assert cache.get("key") == "value"
        time.sleep(1.1)
        assert cache.get("key") is None
    finally:
        cache.clear()

def test_cache_expiration_custom_ttl():
    """Custom TTL per item"""
    cache = ResponseCache(ttl_seconds=10)
    try:
        cache.set("key", "value", ttl=1)
        time.sleep(1.1)
        assert cache.get("key") is None
    finally:
        cache.clear()

def test_cache_directory_structure():
    """Cache creates proper directory structure"""
    cache = ResponseCache()
    try:
        cache.set("abcdef123", "test")
        # Should create ab/abcdef123.json
        path = cache._get_cache_path("abcdef123")
        assert path.exists()
        assert path.parent.name == "ab"
    finally:
        cache.clear()

def test_cache_cleanup_expired():
    """cleanup_expired removes stale entries"""
    cache = ResponseCache(ttl_seconds=1)
    try:
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        time.sleep(1.1)

        cache.cleanup_expired()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
    finally:
        cache.clear()

def test_cache_stats():
    """Cache statistics are correct"""
    cache = ResponseCache()
    try:
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()
        assert stats["entries"] == 2
        assert stats["total_size_mb"] > 0
    finally:
        cache.clear()

def test_cache_clear():
    """Clear removes all entries"""
    cache = ResponseCache()
    try:
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    finally:
        cache.clear()

def test_cache_thread_safety():
    """Cache operations are thread-safe"""
    cache = ResponseCache()
    try:
        results = []

        def worker():
            for i in range(100):
                key = f"key_{i}"
                cache.set(key, f"value_{i}")
                results.append(cache.get(key))

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 500
        assert all(r is not None for r in results)
    finally:
        cache.clear()

def test_cache_config_from_dict():
    """CacheConfig can be created from dict"""
    config_dict = {
        "enabled": True,
        "backend": "file",
        "cache_dir": ".questfoundry/cache",
        "ttl_seconds": 86400,
    }
    config = CacheConfig.from_dict(config_dict)
    assert config.enabled is True
    assert config.ttl_seconds == 86400

def test_cache_config_provider_override():
    """Per-provider config overrides work"""
    config = CacheConfig(
        per_provider={
            "openai": {"ttl_seconds": 172800},
            "ollama": {"enabled": False},
        }
    )
    assert config.get_ttl_for_provider("openai") == 172800
    assert config.is_enabled_for_provider("ollama") is False
    assert config.is_enabled_for_provider("gemini") is True
```

---

## Part 2: Rate Limiter Tests (test_rate_limiter.py)

### Unit Tests

```python
def test_rate_limiter_basic_acquire():
    """Basic token acquisition"""
    config = RateLimitConfig(requests_per_minute=10)
    limiter = RateLimiter(config)

    assert limiter.acquire(num_requests=1) is True

def test_rate_limiter_exhaustion():
    """Requests denied when tokens exhausted"""
    config = RateLimitConfig(requests_per_minute=2)
    limiter = RateLimiter(config)

    assert limiter.acquire(num_requests=1) is True
    assert limiter.acquire(num_requests=1) is True
    assert limiter.acquire(num_requests=1) is False

def test_rate_limiter_refill():
    """Tokens refill over time"""
    config = RateLimitConfig(requests_per_minute=10)
    limiter = RateLimiter(config)

    # Exhaust tokens
    for _ in range(10):
        assert limiter.acquire(num_requests=1)

    # Should be empty now
    assert not limiter.acquire(num_requests=1)

    # Simulate 60 seconds passing
    limiter.last_request_refill -= 60

    # Should have tokens again
    assert limiter.acquire(num_requests=1)

def test_rate_limiter_token_limit():
    """Token bucket limits work"""
    config = RateLimitConfig(
        requests_per_minute=100,
        tokens_per_hour=1000
    )
    limiter = RateLimiter(config)

    # Should deny if tokens exceed hourly limit
    assert not limiter.acquire(input_tokens=600, output_tokens=500)

    # Should allow if within limit
    assert limiter.acquire(input_tokens=400, output_tokens=500)

def test_rate_limiter_cost_limit():
    """Cost limits work"""
    config = RateLimitConfig(
        requests_per_minute=100,
        tokens_per_hour=10000,
        cost_per_day=10.0,
        cost_per_input_token=0.001,
        cost_per_output_token=0.002,
    )
    limiter = RateLimiter(config)

    # $10/day = 1000 cents
    # This would cost 1000 + 1000 = 2000 cents (over limit)
    assert not limiter.acquire(input_tokens=1000, output_tokens=500)

    # This would cost 100 + 100 = 200 cents (under limit)
    assert limiter.acquire(input_tokens=100, output_tokens=50)

def test_rate_limiter_check_limit_non_consuming():
    """check_limit doesn't consume tokens"""
    config = RateLimitConfig(requests_per_minute=2)
    limiter = RateLimiter(config)

    # Check limit shouldn't consume
    assert limiter.check_limit(num_requests=1) is True
    assert limiter.check_limit(num_requests=1) is True
    assert limiter.check_limit(num_requests=1) is True

    # But acquire should still work
    assert limiter.acquire(num_requests=1) is True
    assert limiter.acquire(num_requests=1) is True
    assert limiter.acquire(num_requests=1) is False

def test_rate_limiter_usage_tracking():
    """Usage is tracked correctly"""
    config = RateLimitConfig()
    limiter = RateLimiter(config)

    limiter.record_usage(100, 200, 1)
    limiter.record_usage(50, 150, 1)

    stats = limiter.get_stats()
    assert stats["total_requests"] == 2
    assert stats["total_input_tokens"] == 150
    assert stats["total_output_tokens"] == 350

def test_cost_tracker_basic():
    """Cost tracking works"""
    tracker = CostTracker()

    tracker.record_request(
        provider="openai",
        model="gpt-4",
        input_tokens=100,
        output_tokens=200,
        cost_per_input_1k=0.03,
        cost_per_output_1k=0.06,
    )

    assert tracker.get_total_cost() == pytest.approx(0.0063, abs=0.0001)

def test_cost_tracker_by_provider():
    """Cost tracking by provider"""
    tracker = CostTracker()

    tracker.record_request("openai", "gpt-4", 100, 100, 0.01, 0.02)
    tracker.record_request("gemini", "1.5-pro", 100, 100, 0.001, 0.002)

    costs = tracker.get_cost_by_provider()
    assert "openai" in costs
    assert "gemini" in costs
    assert costs["openai"] > costs["gemini"]

def test_cost_tracker_by_model():
    """Cost tracking by model"""
    tracker = CostTracker()

    tracker.record_request("openai", "gpt-4", 100, 100, 0.01, 0.02)
    tracker.record_request("openai", "gpt-3.5", 100, 100, 0.001, 0.002)

    costs = tracker.get_cost_by_model()
    assert "openai/gpt-4" in costs
    assert "openai/gpt-3.5" in costs

def test_cost_tracker_summary():
    """Cost summary includes all info"""
    tracker = CostTracker()

    tracker.record_request("openai", "gpt-4", 100, 100, 0.01, 0.02)

    summary = tracker.get_cost_summary()
    assert "total_cost" in summary
    assert "cost_today" in summary
    assert "cost_this_month" in summary
    assert "by_provider" in summary

def test_rate_limiter_wait_until_available():
    """wait_until_available blocks until ready"""
    config = RateLimitConfig(requests_per_minute=1)
    limiter = RateLimiter(config)

    # Use up token
    limiter.acquire(num_requests=1)

    # Wait should return False immediately (timeout)
    assert limiter.wait_until_available(num_requests=1, max_wait_seconds=0.1) is False

    # After refill, should succeed
    limiter.last_request_refill -= 60
    assert limiter.wait_until_available(num_requests=1, max_wait_seconds=1) is True
```

---

## Part 3: Configuration Tests (test_per_role_config.py)

### Unit Tests

```python
def test_get_role_provider_name():
    """Role-specific provider lookup"""
    config = ProviderConfig()
    config._config = {
        "providers": {
            "text": {"default": "openai"}
        },
        "roles": {
            "scene_smith": {"provider": "ollama"}
        }
    }

    # Configured role should return configured provider
    assert config.get_role_provider_name("scene_smith") == "ollama"

    # Unconfigured role should return default
    assert config.get_role_provider_name("gatekeeper") == "openai"

def test_get_role_config():
    """Get role configuration"""
    config = ProviderConfig()
    config._config = {
        "roles": {
            "scene_smith": {
                "provider": "openai",
                "temperature": 0.8,
                "max_tokens": 3000,
            }
        }
    }

    role_config = config.get_role_config("scene_smith")
    assert role_config["provider"] == "openai"
    assert role_config["temperature"] == 0.8
    assert role_config["max_tokens"] == 3000

def test_get_role_config_missing():
    """Missing role returns empty dict"""
    config = ProviderConfig()
    config._config = {"roles": {}}

    role_config = config.get_role_config("nonexistent")
    assert role_config == {}

def test_get_role_parameter():
    """Get specific role parameter"""
    config = ProviderConfig()
    config._config = {
        "roles": {
            "scene_smith": {"temperature": 0.8}
        }
    }

    temp = config.get_role_parameter("scene_smith", "temperature")
    assert temp == 0.8

    # With default
    model = config.get_role_parameter(
        "scene_smith",
        "model",
        default="gpt-4"
    )
    assert model == "gpt-4"

def test_is_role_configured():
    """Check if role has configuration"""
    config = ProviderConfig()
    config._config = {
        "roles": {
            "scene_smith": {"provider": "openai"}
        }
    }

    assert config.is_role_configured("scene_smith") is True
    assert config.is_role_configured("gatekeeper") is False

def test_infer_provider_type():
    """Provider type is inferred from role name"""
    assert ProviderConfig._infer_provider_type("illustrator") == "image"
    assert ProviderConfig._infer_provider_type("art_director") == "image"
    assert ProviderConfig._infer_provider_type("audio_director") == "audio"
    assert ProviderConfig._infer_provider_type("audio_producer") == "audio"
    assert ProviderConfig._infer_provider_type("scene_smith") == "text"
    assert ProviderConfig._infer_provider_type("gatekeeper") == "text"
```

### Integration Tests

```python
def test_role_uses_configured_temperature():
    """Role uses temperature from config"""
    mock_provider = Mock(spec=TextProvider)
    mock_provider.generate_text.return_value = "output"

    role_config = {"temperature": 0.5}
    role = SceneSmith(provider=mock_provider, role_config=role_config)

    context = RoleContext(task="test")
    role.execute_task(context)

    # Verify provider was called with configured temperature
    mock_provider.generate_text.assert_called()
    call_kwargs = mock_provider.generate_text.call_args.kwargs
    assert call_kwargs["temperature"] == 0.5

def test_role_uses_configured_max_tokens():
    """Role uses max_tokens from config"""
    mock_provider = Mock(spec=TextProvider)
    mock_provider.generate_text.return_value = "output"

    role_config = {"max_tokens": 500}
    role = SceneSmith(provider=mock_provider, role_config=role_config)

    context = RoleContext(task="test")
    role.execute_task(context)

    call_kwargs = mock_provider.generate_text.call_args.kwargs
    assert call_kwargs["max_tokens"] == 500

def test_role_uses_configured_model():
    """Role uses model from config"""
    mock_provider = Mock(spec=TextProvider)
    mock_provider.generate_text.return_value = "output"

    role_config = {"model": "custom-model"}
    role = SceneSmith(provider=mock_provider, role_config=role_config)

    context = RoleContext(task="test")
    role.execute_task(context)

    call_kwargs = mock_provider.generate_text.call_args.kwargs
    assert call_kwargs["model"] == "custom-model"
```

---

## Part 4: Integration Tests

### End-to-End Tests (test_end_to_end.py)

```python
def test_simple_workflow_with_caching():
    """Test full workflow with caching enabled"""
    # Create minimal project
    project = create_minimal_project()

    # Run multiple loops
    for _ in range(2):
        # First iteration: cache miss
        # Second iteration: cache hit
        result = showrunner.execute_loop("scene_forge", project)
        assert result.success

    # Verify cache was used
    cache = ResponseCache()
    assert cache.get_stats()["entries"] > 0

def test_workflow_respects_role_config():
    """Different roles use different providers"""
    config = ProviderConfig()
    config._config = {
        "providers": {
            "text": {
                "default": "openai",
                "openai": {"model": "gpt-4"},
                "ollama": {"base_url": "localhost", "model": "llama3"},
            }
        },
        "roles": {
            "scene_smith": {"provider": "openai"},
            "gatekeeper": {"provider": "ollama"},
        }
    }

    project = create_minimal_project()

    # scene_smith should use OpenAI
    scene_smith = showrunner.get_role("scene_smith")
    assert scene_smith.provider.__class__.__name__ == "OpenAIProvider"

    # gatekeeper should use Ollama
    gatekeeper = showrunner.get_role("gatekeeper")
    assert gatekeeper.provider.__class__.__name__ == "OllamaProvider"

def test_error_recovery_retries():
    """Errors trigger retry logic"""
    # Mock provider that fails then succeeds
    mock_provider = Mock(spec=TextProvider)
    mock_provider.generate_text.side_effect = [
        Exception("Network error"),
        "success"
    ]

    # With retry logic enabled
    result = generate_with_retry(mock_provider, "prompt")
    assert result == "success"
    assert mock_provider.generate_text.call_count == 2
```

### Multi-Loop Tests (test_multi_loop.py)

```python
def test_multiple_loops_preserve_state():
    """State preserved between loops"""
    project = create_minimal_project()

    # Run loop A
    result_a = showrunner.execute_loop("story_spark", project)
    assert result_a.success
    assert result_a.artifacts  # Should produce artifacts

    # Run loop B using artifacts from A
    result_b = showrunner.execute_loop("hook_harvest", project)
    assert result_b.success

    # Artifacts from A should still be available
    assert len(project.artifacts) > 0

def test_loop_artifact_dependencies():
    """Loop B can use artifacts from loop A"""
    project = create_minimal_project()

    # Setup artifacts from first loop
    loop_a_result = showrunner.execute_loop("scene_forge", project)

    # Second loop should see those artifacts
    loop_b_result = showrunner.execute_loop("gatecheck", project)

    # Both should succeed and produce results
    assert loop_a_result.success
    assert loop_b_result.success
```

---

## Part 5: Performance Tests

### Cache Performance (test_cache_performance.py)

```python
def test_cache_hit_performance(benchmark):
    """Cache hit is much faster than cache miss"""
    cache = ResponseCache()
    key = "test_key"
    value = "x" * 1000

    # Pre-populate cache
    cache.set(key, value)

    # Measure cache hit
    def cache_hit():
        return cache.get(key)

    hit_time = benchmark(cache_hit)

    # Cache hit should be very fast (< 1ms)
    assert hit_time < 0.001

def test_cache_size_limits(benchmark):
    """Cache respects size limits"""
    cache = ResponseCache()

    # Fill cache with large responses
    for i in range(100):
        key = f"key_{i}"
        value = "x" * 10000  # 10KB each
        cache.set(key, value)

    stats = cache.get_stats()
    # Should be limited to max size
    assert stats["total_size_mb"] <= 100  # Or configured limit

def test_cache_throughput(benchmark):
    """Benchmark cache throughput"""
    cache = ResponseCache()

    def cache_operations():
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")

    # Should complete in reasonable time
    benchmark(cache_operations)
```

### Large Project Testing (test_large_project.py)

```python
def test_large_project_performance():
    """Performance with large projects"""
    # Create project with many scenes
    project = create_large_project(num_scenes=50)

    start_time = time.time()
    result = showrunner.execute_full_workflow(project)
    elapsed = time.time() - start_time

    assert result.success
    # Should complete in reasonable time (< 5 minutes)
    assert elapsed < 300

def test_large_project_memory_usage():
    """Memory usage reasonable for large projects"""
    project = create_large_project(num_scenes=50)

    import tracemalloc
    tracemalloc.start()

    result = showrunner.execute_full_workflow(project)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory should be reasonable (< 500MB)
    assert peak < 500 * 1024 * 1024

def test_cost_tracking_large_workflow():
    """Cost tracking accurate for large workflows"""
    project = create_large_project(num_scenes=10)

    # Execute workflow with cost tracking
    result = showrunner.execute_full_workflow(project)

    # Get cost summary
    cost_summary = showrunner.get_cost_summary()

    # Costs should be reasonable and tracked
    assert cost_summary["total_cost"] > 0
    assert "by_provider" in cost_summary
```

### Provider Performance (test_provider_performance.py)

```python
def test_provider_response_time():
    """Benchmark provider response times"""
    # Skip if provider not available
    pytest.skip_if_no_api_key("OPENAI_API_KEY")

    provider = OpenAIProvider({"api_key": os.getenv("OPENAI_API_KEY")})

    def generate():
        return provider.generate_text("Hello, world!")

    # Benchmark real API call
    # Expected: 1-5 seconds for real API
    import timeit
    time_taken = timeit.timeit(generate, number=1)

    assert 1 < time_taken < 10

def test_provider_comparison():
    """Compare provider efficiency"""
    pytest.skip_if_no_api_key("OPENAI_API_KEY")
    pytest.skip_if_no_api_key("GEMINI_API_KEY")

    openai_provider = OpenAIProvider(...)
    gemini_provider = GeminiProvider(...)

    prompt = "Generate a 100-word story"

    # Compare response times
    openai_time = measure_response_time(openai_provider, prompt)
    gemini_time = measure_response_time(gemini_provider, prompt)

    # Both should respond in reasonable time
    assert openai_time < 10
    assert gemini_time < 10

    # Can print comparison
    print(f"OpenAI: {openai_time:.2f}s, Gemini: {gemini_time:.2f}s")
```

---

## Test Execution Strategy

### Phase 1: Unit Tests (Day 1-2)
```bash
pytest tests/providers/test_cache.py
pytest tests/providers/test_rate_limiter.py
pytest tests/roles/test_per_role_config.py
```

### Phase 2: Integration Tests (Day 2-3)
```bash
pytest tests/roles/test_role_provider_usage.py
pytest tests/integration/test_end_to_end.py
pytest tests/integration/test_multi_loop.py
```

### Phase 3: Performance Tests (Day 3-4)
```bash
pytest tests/performance/ -v --benchmark-only
```

### Phase 4: Provider Tests (Day 4)
```bash
pytest tests/providers/test_provider_integration.py
pytest tests/providers/test_openai_integration.py  # With API key
pytest tests/providers/test_ollama_integration.py  # With local Ollama
```

### Full Test Run
```bash
pytest tests/ -v --cov=src/questfoundry --cov-report=html
```

---

## Coverage Goals

- **Overall**: >80% code coverage
- **Providers**: >85% coverage
- **Roles**: >80% coverage
- **State**: >85% coverage
- **Critical paths**: 100% coverage

---

## Test Data & Fixtures

### Fixtures (conftest.py)

```python
@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider"""
    provider = Mock(spec=TextProvider)
    provider.generate_text.return_value = "mocked response"
    return provider

@pytest.fixture
def minimal_project():
    """Minimal valid project for testing"""
    return create_minimal_project()

@pytest.fixture
def test_cache(tmp_path):
    """Test cache with temp directory"""
    return ResponseCache(cache_dir=tmp_path / "cache")

@pytest.fixture
def test_rate_limiter():
    """Test rate limiter"""
    config = RateLimitConfig(
        requests_per_minute=10,
        tokens_per_hour=1000,
    )
    return RateLimiter(config)
```

---

## Continuous Integration

### Pre-commit Hooks
- Run unit tests
- Check code coverage
- Lint and format checks

### CI Pipeline
- Run all tests
- Generate coverage report
- Performance regression tests
- Integration tests with real APIs (optional)

---

## Test Metrics

- **Coverage**: Track code coverage percentage
- **Pass Rate**: Aim for 100% pass rate
- **Performance**: Benchmark against baseline
- **Flakiness**: Track and eliminate flaky tests

---

## Known Limitations & Skips

Tests that may need to be skipped:
- Real provider API tests (require API keys)
- Redis tests (require Redis instance)
- Performance tests (machine-dependent)
- Large project tests (time-consuming)

Use markers:
```python
@pytest.mark.skipif(not OPENAI_API_KEY, reason="No OpenAI API key")
@pytest.mark.requires_redis
@pytest.mark.slow
@pytest.mark.performance
```
