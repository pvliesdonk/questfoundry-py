# Epic 15.1 - Rate Limiting & Cost Tracking Design

## Overview

Rate limiting prevents API quota violations while tracking costs and usage patterns.

## Design Decisions

### 1. Algorithm: Token Bucket

**Decision**: Token bucket algorithm for rate limiting

```
Tokens = min(MaxTokens, Tokens + RechargeRate * TimeSinceLastCheck)
If Tokens >= RequestCost:
    Tokens -= RequestCost
    Allow Request
Else:
    Deny/Queue Request
```

**Rationale**:
- Handles burst traffic gracefully
- Simple and well-tested
- Can represent different types of limits (requests, tokens, cost)
- Allows fine-grained configuration

### 2. Limit Types

**Three-layer approach**:

```
1. Request Rate Limits
   - Max requests per minute (e.g., 90 for OpenAI)

2. Token Limits
   - Max tokens per hour (e.g., 90,000 for OpenAI)

3. Cost Limits
   - Max spend per day/month (optional)
```

### 3. Global vs Per-Provider

**Structure**:
```
Global:
  requests_per_minute: 100
  tokens_per_hour: 100000
  cost_per_day: 100.0

Per-Provider:
  openai:
    requests_per_minute: 90
    tokens_per_hour: 90000
  ollama:
    requests_per_minute: 1000  # Local, no limits
  gemini:
    requests_per_minute: 60
    tokens_per_hour: 60000
```

### 4. Cost Tracking

**Provider-specific pricing**:

```python
PROVIDER_PRICING = {
    "openai": {
        "gpt-4o": {
            "input_per_1k": 0.015,
            "output_per_1k": 0.06,
        },
        "gpt-4-turbo": {
            "input_per_1k": 0.01,
            "output_per_1k": 0.03,
        },
    },
    "gemini": {
        "gemini-1.5-pro": {
            "input_per_1k": 0.00175,
            "output_per_1k": 0.0035,
        },
    },
    "ollama": {
        "*": {  # All models
            "input_per_1k": 0.0,  # Free
            "output_per_1k": 0.0,
        },
    },
}
```

## Implementation Details

### RateLimiter Class

```python
import time
from threading import Lock
from dataclasses import dataclass

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    # Request rate (per minute)
    requests_per_minute: int = 60

    # Token rate (per hour)
    tokens_per_hour: int = 1000

    # Cost limit (per day)
    cost_per_day: float | None = None

    # Provider-specific pricing
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0

class RateLimiter:
    """Token bucket rate limiter with cost tracking"""

    def __init__(self, config: RateLimitConfig):
        self.config = config

        # Token buckets
        self.request_tokens = config.requests_per_minute
        self.token_tokens = config.tokens_per_hour
        self.cost_tokens = config.cost_per_day * 100 if config.cost_per_day else None

        # Last refill times
        self.last_request_refill = time.time()
        self.last_token_refill = time.time()
        self.last_cost_refill = time.time()

        # Thread safety
        self.lock = Lock()

        # Usage tracking
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def _refill_buckets(self):
        """Refill token buckets based on elapsed time"""
        now = time.time()

        # Refill request tokens (per minute)
        minutes_elapsed = (now - self.last_request_refill) / 60.0
        self.request_tokens = min(
            self.config.requests_per_minute,
            self.request_tokens + self.config.requests_per_minute * minutes_elapsed
        )
        self.last_request_refill = now

        # Refill token bucket (per hour)
        hours_elapsed = (now - self.last_token_refill) / 3600.0
        self.token_tokens = min(
            self.config.tokens_per_hour,
            self.token_tokens + self.config.tokens_per_hour * hours_elapsed
        )
        self.last_token_refill = now

        # Refill cost bucket (per day)
        if self.cost_tokens is not None:
            days_elapsed = (now - self.last_cost_refill) / 86400.0
            max_cost_tokens = self.config.cost_per_day * 100
            self.cost_tokens = min(
                max_cost_tokens,
                self.cost_tokens + max_cost_tokens * days_elapsed
            )
            self.last_cost_refill = now

    def acquire(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        num_requests: int = 1
    ) -> bool:
        """
        Check if we can make a request with given token count.
        Returns True if allowed, False if rate limited.
        """
        with self.lock:
            self._refill_buckets()

            # Check request limit
            if self.request_tokens < num_requests:
                return False

            # Check token limit
            if self.token_tokens < (input_tokens + output_tokens):
                return False

            # Check cost limit (approximate)
            estimated_cost = self._estimate_cost(input_tokens, output_tokens)
            if self.cost_tokens is not None and self.cost_tokens < (estimated_cost * 100):
                return False

            # All checks passed, consume tokens
            self.request_tokens -= num_requests
            self.token_tokens -= (input_tokens + output_tokens)
            if self.cost_tokens is not None:
                self.cost_tokens -= (estimated_cost * 100)

            return True

    def check_limit(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        num_requests: int = 1
    ) -> bool:
        """Check if request would be allowed (non-consuming)"""
        with self.lock:
            self._refill_buckets()

            return (
                self.request_tokens >= num_requests
                and self.token_tokens >= (input_tokens + output_tokens)
                and (
                    self.cost_tokens is None
                    or self.cost_tokens >= self._estimate_cost(input_tokens, output_tokens) * 100
                )
            )

    def record_usage(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        num_requests: int = 1
    ):
        """Record actual usage for tracking"""
        with self.lock:
            self.total_requests += num_requests
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

            cost = self._calculate_cost(input_tokens, output_tokens)
            self.total_cost += cost

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost before making request"""
        return self._calculate_cost(input_tokens, output_tokens)

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost of tokens"""
        input_cost = (input_tokens / 1000.0) * self.config.cost_per_input_token
        output_cost = (output_tokens / 1000.0) * self.config.cost_per_output_token
        return input_cost + output_cost

    def get_stats(self) -> dict:
        """Get usage statistics"""
        with self.lock:
            self._refill_buckets()

            return {
                "total_requests": self.total_requests,
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_cost": round(self.total_cost, 4),
                "available_request_tokens": int(self.request_tokens),
                "available_token_tokens": int(self.token_tokens),
            }

    def wait_until_available(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        num_requests: int = 1,
        max_wait_seconds: int = 3600
    ) -> bool:
        """
        Wait until rate limit allows the request.
        Useful for batch operations.
        """
        start_time = time.time()

        while True:
            if self.acquire(input_tokens, output_tokens, num_requests):
                return True

            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                return False

            # Exponential backoff: 1s, 2s, 4s, etc.
            wait_time = min(2 ** (elapsed // 60), 10)
            time.sleep(wait_time)
```

### CostTracker Class

```python
from collections import defaultdict
from datetime import datetime, timedelta
import json

class CostTracker:
    """Track API costs across providers and time periods"""

    def __init__(self, history_days: int = 30):
        self.history_days = history_days
        self.costs_by_provider: dict[str, float] = defaultdict(float)
        self.costs_by_date: dict[str, float] = defaultdict(float)
        self.costs_by_model: dict[str, float] = defaultdict(float)
        self.lock = Lock()

    def record_request(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_per_input_1k: float,
        cost_per_output_1k: float,
    ):
        """Record a request and its cost"""
        cost = (
            (input_tokens / 1000.0) * cost_per_input_1k +
            (output_tokens / 1000.0) * cost_per_output_1k
        )

        date_key = datetime.now().strftime("%Y-%m-%d")

        with self.lock:
            self.costs_by_provider[provider] += cost
            self.costs_by_date[date_key] += cost
            self.costs_by_model[f"{provider}/{model}"] += cost

    def get_total_cost(self) -> float:
        """Get total cost across all time"""
        with self.lock:
            return sum(self.costs_by_provider.values())

    def get_cost_by_provider(self) -> dict[str, float]:
        """Get costs broken down by provider"""
        with self.lock:
            return dict(self.costs_by_provider)

    def get_cost_by_model(self) -> dict[str, float]:
        """Get costs broken down by provider and model"""
        with self.lock:
            return dict(self.costs_by_model)

    def get_daily_cost(self, date: str = None) -> float:
        """Get cost for a specific day (YYYY-MM-DD)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with self.lock:
            return self.costs_by_date.get(date, 0.0)

    def get_cost_summary(self) -> dict:
        """Get comprehensive cost summary"""
        with self.lock:
            total = sum(self.costs_by_provider.values())
            today = datetime.now().strftime("%Y-%m-%d")

            return {
                "total_cost": round(total, 4),
                "cost_today": round(self.costs_by_date.get(today, 0.0), 4),
                "cost_this_month": round(
                    sum(
                        v for k, v in self.costs_by_date.items()
                        if k.startswith(datetime.now().strftime("%Y-%m"))
                    ),
                    4
                ),
                "by_provider": {k: round(v, 4) for k, v in self.costs_by_provider.items()},
            }
```

### Integration with TextProvider

```python
class TextProvider(Provider):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.rate_limiter = self._create_rate_limiter(config)
        self.cost_tracker = CostTracker()

    def _create_rate_limiter(self, config: dict) -> RateLimiter:
        """Create rate limiter from config"""
        rate_config = RateLimitConfig(
            requests_per_minute=config.get("requests_per_minute", 60),
            tokens_per_hour=config.get("tokens_per_hour", 10000),
            cost_per_day=config.get("cost_per_day"),
            cost_per_input_token=config.get("cost_per_input_token", 0.0),
            cost_per_output_token=config.get("cost_per_output_token", 0.0),
        )
        return RateLimiter(rate_config)

    def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text with rate limiting"""
        # Estimate token count
        estimated_tokens = self._estimate_token_count(prompt)

        # Check rate limit (non-blocking)
        if not self.rate_limiter.check_limit(
            input_tokens=estimated_tokens,
            output_tokens=1000  # Assume ~1000 token response
        ):
            raise RateLimitError(
                f"Rate limit would be exceeded. "
                f"Available: {self.rate_limiter.get_stats()}"
            )

        # Generate text
        response = self._generate_text_uncached(prompt, model, **kwargs)

        # Record actual token usage
        actual_input_tokens = self._count_tokens(prompt)
        actual_output_tokens = self._count_tokens(response)

        self.rate_limiter.record_usage(actual_input_tokens, actual_output_tokens)
        self.cost_tracker.record_request(
            provider=self.__class__.__name__,
            model=model or self.default_model,
            input_tokens=actual_input_tokens,
            output_tokens=actual_output_tokens,
            cost_per_input_1k=self.config.get("cost_per_input_token", 0.0),
            cost_per_output_1k=self.config.get("cost_per_output_token", 0.0),
        )

        return response

    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count (rough: ~4 chars per token)"""
        return len(text) // 4

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text (override in subclass for accuracy)"""
        return len(text) // 4
```

## Testing Strategy

### Unit Tests

```python
def test_rate_limiter_basic():
    """Test basic rate limiting"""
    config = RateLimitConfig(requests_per_minute=10)
    limiter = RateLimiter(config)

    # Should allow up to 10 requests
    for _ in range(10):
        assert limiter.acquire(num_requests=1)

    # 11th request should be denied
    assert not limiter.acquire(num_requests=1)

def test_rate_limiter_refill():
    """Test token bucket refill"""
    config = RateLimitConfig(requests_per_minute=10)
    limiter = RateLimiter(config)

    # Exhaust tokens
    for _ in range(10):
        assert limiter.acquire(num_requests=1)

    # Wait a minute and should be refilled
    limiter.last_request_refill -= 60
    assert limiter.acquire(num_requests=1)

def test_cost_tracking():
    """Test cost tracking"""
    tracker = CostTracker()

    tracker.record_request(
        provider="openai",
        model="gpt-4",
        input_tokens=100,
        output_tokens=200,
        cost_per_input_1k=0.03,
        cost_per_output_1k=0.06,
    )

    cost = tracker.get_total_cost()
    assert cost == pytest.approx(0.0063, abs=0.0001)
```

## Configuration Example

```yaml
# .questfoundry/config.yml
rate_limiting:
  global:
    requests_per_minute: 100
    tokens_per_hour: 100000

  providers:
    openai:
      requests_per_minute: 90
      tokens_per_hour: 90000
      cost_per_input_token: 0.00002
      cost_per_output_token: 0.00006

    ollama:
      requests_per_minute: 1000
      tokens_per_hour: 1000000
      cost_per_input_token: 0.0
      cost_per_output_token: 0.0

    gemini:
      requests_per_minute: 60
      tokens_per_hour: 60000
      cost_per_input_token: 0.00000175
      cost_per_output_token: 0.0000035

cost_limits:
  daily: 50.0  # Optional: max $50/day
  monthly: 500.0  # Optional: max $500/month
```

## Error Handling

```python
class RateLimitError(Exception):
    """Raised when rate limit would be exceeded"""
    pass

class CostLimitExceededError(Exception):
    """Raised when cost limit exceeded"""
    pass

# Usage
try:
    provider.generate_text(prompt)
except RateLimitError as e:
    # Handle rate limit
    wait_time = provider.rate_limiter.get_wait_time()
    print(f"Rate limited. Retry in {wait_time} seconds")
except CostLimitExceededError as e:
    # Handle cost limit
    print(f"Cost limit exceeded: {e}")
```

## Future Enhancements

1. **Adaptive Rate Limiting**: Adjust limits based on API responses
2. **Cost Forecasting**: Predict costs based on usage patterns
3. **Budget Alerts**: Notify when approaching limits
4. **Multi-Account Support**: Distribute load across API keys
5. **Intelligent Caching**: Use cache to reduce token usage
