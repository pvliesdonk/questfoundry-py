"""Shared test fixtures and utilities for QuestFoundry tests."""

from questfoundry.providers.base import TextProvider


class MockTextProvider(TextProvider):
    """
    Mock text provider for testing.

    Supports two modes:
    1. Simple mode: Single response for all prompts (set via `response` param)
    2. Dict mode: Task-specific responses (set via `responses` param)

    Attributes:
        response: Single response to return for all prompts
        responses: Dict mapping task identifiers to specific responses
        default_response: Fallback response when no match found
        last_prompt: Last prompt received (for test assertions)
    """

    def __init__(
        self,
        response: str | None = None,
        responses: dict[str, str] | None = None,
    ):
        """
        Initialize mock provider.

        Args:
            response: Single response for all prompts (simple mode)
            responses: Dict of task-specific responses (dict mode)
        """
        super().__init__({"api_key": "test"})
        self.response = response
        self.responses = responses or {}
        self.default_response = '{"status": "ok"}'
        self.last_prompt = None

    def validate_config(self) -> None:
        """No validation needed for mock."""
        pass

    def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs,
    ) -> str:
        """
        Generate mock text response.

        In simple mode (response set), returns that response.
        In dict mode (responses set), matches prompt against task patterns.

        Args:
            prompt: Input prompt
            model: Model name (ignored)
            max_tokens: Max tokens (ignored)
            temperature: Temperature (ignored)
            **kwargs: Additional arguments (ignored)

        Returns:
            Mock response text
        """
        self.last_prompt = prompt

        # Simple mode: return fixed response
        if self.response is not None:
            return self.response

        # Dict mode: match prompt patterns to return appropriate response
        prompt_lower = prompt.lower()

        # Showrunner tasks
        if "task: select loop" in prompt_lower:
            return self.responses.get(
                "select_loop",
                (
                    "**Selected Loop**: story_spark\n\n"
                    "Rationale: This is the foundational loop..."
                ),
            )

        # Loop execution tasks
        if "# task: pre-gate check" in prompt_lower:
            return self.responses.get(
                "pre_gate",
                (
                    '{"status": "pass", "blockers": [], '
                    '"quick_wins": [], "review_needed": []}'
                ),
            )
        elif "# task: generate quest hooks" in prompt_lower:
            return self.responses.get(
                "generate_hooks",
                (
                    '{"hooks": [{"title": "Test Hook", '
                    '"summary": "A test hook", "tags": ["test"]}]}'
                ),
            )
        elif "# task: design narrative topology" in prompt_lower:
            return self.responses.get("create_topology", "Test topology content")
        elif "# task: create tu brief" in prompt_lower:
            return self.responses.get("create_tu_brief", "Test TU brief content")
        elif "# task: create section briefs" in prompt_lower:
            return self.responses.get(
                "create_section_briefs", "Test section briefs content"
            )
        elif "# task: draft scene" in prompt_lower:
            return self.responses.get("draft_scene", "Test scene content")

        # Fallback: check if any response key matches
        for task_key, response_text in self.responses.items():
            if task_key in prompt_lower:
                return response_text

        return self.default_response

    def generate_text_streaming(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs,
    ):
        """Mock streaming by yielding generate_text result."""
        yield self.generate_text(
            prompt, model, max_tokens, temperature, **kwargs
        )

    def close(self) -> None:
        """No cleanup needed for mock."""
        pass
