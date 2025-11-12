"""Tests for Role base class integration with sessions and human callbacks."""
import io
from pathlib import Path
from typing import Any

import pytest

from questfoundry.providers.base import TextProvider
from questfoundry.roles.base import Role, RoleContext, RoleResult
from questfoundry.roles.human_callback import DefaultHumanCallback
from questfoundry.roles.session import RoleSession


class MockTextProvider(TextProvider):
    """Mock text provider for testing."""

    def __init__(self):
        """Initialize with empty config."""
        super().__init__(config={})

    def generate_text(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Return a simple test response."""
        return "Mock response"

    def generate_text_streaming(self, prompt: str, **kwargs) -> Any:
        """Not implemented for tests."""
        raise NotImplementedError()

    def validate_config(self) -> bool:
        """Always valid for tests."""
        return True


class SampleRole(Role):
    """Test role for testing base class functionality."""

    @property
    def role_name(self) -> str:
        return "test_role"

    @property
    def display_name(self) -> str:
        return "Test Role"

    def execute_task(self, context: RoleContext) -> RoleResult:
        """Execute test task."""
        return RoleResult(
            success=True,
            output="Test output",
            metadata={"task": context.task},
        )


@pytest.fixture
def mock_provider():
    """Create a mock text provider."""
    return MockTextProvider()


@pytest.fixture
def test_role(mock_provider):
    """Create a test role."""
    return SampleRole(provider=mock_provider)


def test_role_without_session(test_role):
    """Test role without session (backward compatibility)."""
    assert test_role.session is None
    assert test_role.human_callback is None


def test_role_with_session(mock_provider, tmp_path):
    """Test role with session attached."""
    session = RoleSession(
        role="test_role",
        workspace_path=tmp_path,
    )

    role = SampleRole(
        provider=mock_provider,
        session=session,
    )

    assert role.session is session
    assert role.session.role == "test_role"


def test_role_without_human_callback_batch_mode(test_role):
    """Test ask_human in batch mode (no callback)."""
    # Should return first suggestion in batch mode
    options = [
        {"key": "red", "label": "Red"},
        {"key": "blue", "label": "Blue"},
    ]
    answer = test_role.ask_human(
        "What color?",
        options=options,
    )

    assert answer == "red"


def test_role_without_human_callback_no_suggestions(test_role):
    """Test ask_human in batch mode with no suggestions."""
    # Should return empty string
    answer = test_role.ask_human("What color?")

    assert answer == ""


def test_role_with_human_callback(mock_provider, monkeypatch):
    """Test role with custom human callback."""
    monkeypatch.setattr("sys.stdin", io.StringIO("custom answer\n"))
    role = SampleRole(
        provider=mock_provider,
        human_callback=DefaultHumanCallback(),
    )

    answer = role.ask_human("Test question?")

    assert answer == "custom answer"


def test_ask_yes_no_batch_mode(test_role):
    """Test ask_yes_no in batch mode returns first suggestion (yes)."""
    # In batch mode, first suggestion is "yes", so always returns True
    assert test_role.ask_yes_no("Continue?", default=True) is True
    assert test_role.ask_yes_no("Continue?", default=False) is True


def test_ask_yes_no_with_callback(mock_provider, monkeypatch):
    """Test ask_yes_no with callback."""
    monkeypatch.setattr("sys.stdin", io.StringIO("yes\n"))
    role = SampleRole(
        provider=mock_provider,
        human_callback=DefaultHumanCallback(),
    )

    assert role.ask_yes_no("Continue?") is True


def test_ask_choice_batch_mode(test_role):
    """Test ask_choice in batch mode returns first choice."""
    choice = test_role.ask_choice(
        "Pick a color:",
        choices=["red", "blue", "green"],
    )

    assert choice == "red"


def test_ask_choice_with_callback(mock_provider, monkeypatch):
    """Test ask_choice with callback."""
    monkeypatch.setattr("sys.stdin", io.StringIO("blue\n"))
    role = SampleRole(
        provider=mock_provider,
        human_callback=DefaultHumanCallback(),
    )

    choice = role.ask_choice(
        "Pick a color:",
        choices=["red", "blue", "green"],
    )

    assert choice == "blue"


def test_role_repr_without_session(test_role):
    """Test __repr__ without session or callback."""
    repr_str = repr(test_role)

    assert "SampleRole" in repr_str
    assert "test_role" in repr_str
    assert "session" not in repr_str
    assert "interactive" not in repr_str


def test_role_repr_with_session(mock_provider, tmp_path):
    """Test __repr__ with session."""
    session = RoleSession(
        role="test_role",
        workspace_path=tmp_path,
    )

    role = SampleRole(
        provider=mock_provider,
        session=session,
    )

    repr_str = repr(role)

    assert "SampleRole" in repr_str
    assert "session=True" in repr_str


def test_role_repr_with_callback(mock_provider):
    """Test __repr__ with human callback."""
    role = SampleRole(
        provider=mock_provider,
        human_callback=DefaultHumanCallback(),
    )

    repr_str = repr(role)

    assert "SampleRole" in repr_str
    assert "interactive=True" in repr_str


def test_role_execute_task_backward_compatible(test_role):
    """Test execute_task works without session (backward compatibility)."""
    context = RoleContext(
        task="test_task",
        workspace_path=Path.cwd(),
    )

    result = test_role.execute_task(context)

    assert result.success is True
    assert result.output == "Test output"


def test_role_with_both_session_and_callback(mock_provider, tmp_path, monkeypatch):
    """Test role with both session and callback."""
    session = RoleSession(
        role="test_role",
        workspace_path=tmp_path,
    )
    monkeypatch.setattr("sys.stdin", io.StringIO("answer\n"))
    role = SampleRole(
        provider=mock_provider,
        session=session,
        human_callback=DefaultHumanCallback(),
    )

    assert role.session is session
    assert isinstance(role.human_callback, DefaultHumanCallback)

    # Test human interaction works
    answer = role.ask_human("Question?")
    assert answer == "answer"
