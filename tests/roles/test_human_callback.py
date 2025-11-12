"""Tests for agent-to-human communication callbacks."""

import io
from unittest.mock import patch

from questfoundry.roles.human_callback import (
    BatchModeHumanCallback,
    DefaultHumanCallback,
)


def test_batch_mode_callback_with_options():
    """Test batch mode callback returns the key of the first option."""
    callback = BatchModeHumanCallback()
    question = "What color?"
    options = [
        {"key": "r", "label": "Red"},
        {"key": "b", "label": "Blue"},
    ]
    answer = callback.ask_question(question, options)
    assert answer == "r"


def test_batch_mode_callback_without_options():
    """Test batch mode callback returns empty string when no options are provided."""
    callback = BatchModeHumanCallback()
    question = "What color?"
    answer = callback.ask_question(question)
    assert answer == ""


def test_batch_mode_callback_with_empty_options():
    """Test batch mode callback with an empty options list."""
    callback = BatchModeHumanCallback()
    question = "What color?"
    options = []
    answer = callback.ask_question(question, options)
    assert answer == ""


def test_default_human_callback(monkeypatch):
    """Test the default human callback prompts for input."""
    callback = DefaultHumanCallback()
    question = "What is your quest?"
    options = [
        {"key": "a", "label": "To seek the Holy Grail"},
        {"key": "b", "label": "To find a shrubbery"},
    ]

    # Mock stdin and stdout
    monkeypatch.setattr("sys.stdin", io.StringIO("a\n"))
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        answer = callback.ask_question(question, options)

    # Check the output
    output = mock_stdout.getvalue()
    assert "[Agent] What is your quest?" in output
    assert "[a] To seek the Holy Grail" in output
    assert "[b] To find a shrubbery" in output

    # Check the answer
    assert answer == "a"
