"""Tests for agent-to-human communication."""

from typing import Any

from questfoundry.roles.human_callback import (
    HumanInteractionMixin,
    batch_mode_callback,
)


def test_batch_mode_callback_with_suggestions():
    """Test batch mode callback returns first suggestion."""
    question = "What color?"
    context = {"suggestions": ["red", "blue", "green"]}

    answer = batch_mode_callback(question, context)

    assert answer == "red"


def test_batch_mode_callback_without_suggestions():
    """Test batch mode callback returns empty string when no suggestions."""
    question = "What color?"
    context = {}

    answer = batch_mode_callback(question, context)

    assert answer == ""


def test_human_interaction_mixin_with_callback():
    """Test HumanInteractionMixin with custom callback."""

    # Custom callback that always returns "test answer"
    def mock_callback(question: str, context: dict[str, Any]) -> str:
        return "test answer"

    class TestRole(HumanInteractionMixin):
        """Test role with human interaction."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)
            self.role_name = "test_role"

    role = TestRole(human_callback=mock_callback)

    answer = role.ask_human("What's your name?")

    assert answer == "test answer"


def test_human_interaction_mixin_without_callback():
    """Test HumanInteractionMixin defaults to batch mode."""

    class TestRole(HumanInteractionMixin):
        """Test role with human interaction."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)
            self.role_name = "test_role"

    role = TestRole()  # No callback provided

    # Should use batch_mode_callback and return first suggestion
    answer = role.ask_human(
        "What color?",
        suggestions=["red", "blue"],
    )

    assert answer == "red"


def test_ask_human_with_context():
    """Test ask_human passes context correctly."""

    captured_context = {}

    def capture_callback(question: str, context: dict[str, Any]) -> str:
        captured_context.update(context)
        return "answer"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)
            self.role_name = "test_role"

    role = TestRole(human_callback=capture_callback)

    role.ask_human(
        "Test question?",
        context={"key": "value"},
        suggestions=["a", "b"],
        artifacts=[{"type": "test"}],
    )

    assert captured_context["question"] == "Test question?"
    assert captured_context["context"] == {"key": "value"}
    assert captured_context["suggestions"] == ["a", "b"]
    assert captured_context["artifacts"] == [{"type": "test"}]
    assert captured_context["role"] == "test_role"


def test_ask_yes_no_with_yes():
    """Test ask_yes_no with 'yes' response."""

    def yes_callback(question: str, context: dict[str, Any]) -> str:
        return "yes"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=yes_callback)

    result = role.ask_yes_no("Continue?")

    assert result is True


def test_ask_yes_no_with_no():
    """Test ask_yes_no with 'no' response."""

    def no_callback(question: str, context: dict[str, Any]) -> str:
        return "no"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=no_callback)

    result = role.ask_yes_no("Continue?")

    assert result is False


def test_ask_yes_no_variations():
    """Test ask_yes_no recognizes various yes/no formats."""

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    # Test various "yes" formats
    for yes_response in ["yes", "YES", "y", "Y", "true", "TRUE", "1"]:

        def yes_cb(q: str, ctx: dict[str, Any]) -> str:
            return yes_response

        role = TestRole(human_callback=yes_cb)
        assert role.ask_yes_no("Test?") is True

    # Test various "no" formats
    for no_response in ["no", "NO", "n", "N", "false", "FALSE", "0"]:

        def no_cb(q: str, ctx: dict[str, Any]) -> str:
            return no_response

        role = TestRole(human_callback=no_cb)
        assert role.ask_yes_no("Test?") is False


def test_ask_yes_no_with_default():
    """Test ask_yes_no falls back to default for unclear answer."""

    def unclear_callback(question: str, context: dict[str, Any]) -> str:
        return "maybe"  # Unclear answer

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=unclear_callback)

    # Default is True
    result = role.ask_yes_no("Continue?", default=True)
    assert result is True

    # Default is False
    result = role.ask_yes_no("Continue?", default=False)
    assert result is False


def test_ask_choice_with_direct_match():
    """Test ask_choice with direct string match."""

    def choice_callback(question: str, context: dict[str, Any]) -> str:
        return "blue"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=choice_callback)

    result = role.ask_choice(
        "Pick a color:",
        choices=["red", "blue", "green"],
    )

    assert result == "blue"


def test_ask_choice_with_number():
    """Test ask_choice with number (1-indexed)."""

    def number_callback(question: str, context: dict[str, Any]) -> str:
        return "2"  # Select second option (1-indexed)

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=number_callback)

    result = role.ask_choice(
        "Pick a color:",
        choices=["red", "blue", "green"],
    )

    assert result == "blue"


def test_ask_choice_with_default():
    """Test ask_choice falls back to default for invalid input."""

    def invalid_callback(question: str, context: dict[str, Any]) -> str:
        return "invalid"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=invalid_callback)

    result = role.ask_choice(
        "Pick a color:",
        choices=["red", "blue", "green"],
        default=1,  # Default to "blue"
    )

    assert result == "blue"


def test_ask_choice_empty_choices():
    """Test ask_choice with empty choices list."""

    def callback(question: str, context: dict[str, Any]) -> str:
        return "anything"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=callback)

    result = role.ask_choice("Pick:", choices=[])

    assert result == ""


def test_ask_choice_suggestions_passed():
    """Test ask_choice passes choices as suggestions."""

    captured_suggestions = []

    def capture_callback(question: str, context: dict[str, Any]) -> str:
        captured_suggestions.extend(context.get("suggestions", []))
        return "red"

    class TestRole(HumanInteractionMixin):
        """Test role."""

        def __init__(self, human_callback=None):
            super().__init__(human_callback=human_callback)

    role = TestRole(human_callback=capture_callback)

    role.ask_choice("Pick:", choices=["red", "blue", "green"])

    assert captured_suggestions == ["red", "blue", "green"]


def test_mixin_inheritance():
    """Test HumanInteractionMixin works with inheritance."""

    class BaseRole:
        """Base role class."""

        def __init__(self, name: str):
            self.name = name

    class InteractiveRole(HumanInteractionMixin, BaseRole):
        """Role combining HumanInteractionMixin with BaseRole."""

        def __init__(self, name: str, human_callback=None):
            super().__init__(name, human_callback=human_callback)

    role = InteractiveRole("test", human_callback=batch_mode_callback)

    assert role.name == "test"
    assert callable(role.ask_human)


def test_batch_mode_in_practice():
    """Test typical batch mode usage."""

    class AutomatedRole(HumanInteractionMixin):
        """Automated role for batch processing."""

        def __init__(self):
            super().__init__()  # No callback = batch mode

        def process(self) -> dict[str, Any]:
            """Simulated automated processing."""
            tone = self.ask_choice(
                "Select tone:",
                choices=["dark", "light"],
                default=0,
            )

            proceed = self.ask_yes_no("Continue?", default=True)

            return {"tone": tone, "proceed": proceed}

    role = AutomatedRole()
    result = role.process()

    # In batch mode, should use first suggestion and default
    assert result["tone"] == "dark"  # First choice
    assert result["proceed"] is True  # Default
