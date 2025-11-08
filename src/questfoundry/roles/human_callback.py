"""Agent-to-human communication for interactive mode."""

from typing import Any, Callable

# Type alias for human callback functions
HumanCallback = Callable[[str, dict[str, Any]], str]
"""
Callback function signature for agent-to-human questions.

This callback enables roles to ask humans questions during interactive mode.
In batch/guided mode, roles operate autonomously without human interaction.

Args:
    question: The question text to ask the human
    context: Additional context including:
        - question: The original question (repeated for convenience)
        - context: Domain-specific context dict
        - suggestions: List of suggested answers
        - artifacts: Relevant artifacts
        - role: Name of the role asking

Returns:
    Human's response text

Example:
    >>> def my_callback(question: str, context: dict[str, Any]) -> str:
    ...     suggestions = context.get("suggestions", [])
    ...     print(f"Question: {question}")
    ...     if suggestions:
    ...         print(f"Suggestions: {', '.join(suggestions)}")
    ...     return input("Your answer: ")
    ...
    >>> role = InteractiveRole(provider, human_callback=my_callback)
    >>> answer = role.ask_human("What's the protagonist's name?")
"""


def default_human_callback(question: str, context: dict[str, Any]) -> str:
    """
    Default human callback that prompts via stdin.

    This is a simple reference implementation. Production systems should
    provide their own callback that integrates with their UI (CLI, Web, etc.).

    Args:
        question: The question to ask
        context: Additional context

    Returns:
        Human's response from stdin
    """
    role = context.get("role", "Agent")
    suggestions = context.get("suggestions", [])

    print(f"\n[{role}] {question}")

    if suggestions:
        print("\nSuggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        print()

    return input("Your answer: ")


def batch_mode_callback(question: str, context: dict[str, Any]) -> str:
    """
    Batch mode callback that returns default/empty response.

    Used when no human interaction is desired (automated workflows).

    Args:
        question: The question (ignored)
        context: Additional context

    Returns:
        Empty string or first suggestion if available
    """
    suggestions = context.get("suggestions", [])

    # If there are suggestions, use the first one
    if suggestions:
        return suggestions[0]

    # Otherwise return empty string
    return ""


class HumanInteractionMixin:
    """
    Mixin for roles that need to ask humans questions.

    Add this to a Role subclass to enable human interaction:

    Example:
        >>> class InteractiveShowrunner(HumanInteractionMixin, Showrunner):
        ...     pass
        ...
        >>> role = InteractiveShowrunner(provider, human_callback=my_callback)
        >>> answer = role.ask_human("Proceed with scene generation?")
    """

    def __init__(
        self,
        *args: Any,
        human_callback: HumanCallback | None = None,
        **kwargs: Any
    ):
        """
        Initialize mixin with optional human callback.

        Args:
            human_callback: Optional callback for asking humans questions.
                If None, uses batch_mode_callback (auto-answers)
            *args: Passed to parent class
            **kwargs: Passed to parent class
        """
        super().__init__(*args, **kwargs)
        self.human_callback = human_callback or batch_mode_callback

    def ask_human(
        self,
        question: str,
        context: dict[str, Any] | None = None,
        suggestions: list[str] | None = None,
        artifacts: list[Any] | None = None,
    ) -> str:
        """
        Ask human a question (interactive mode).

        In batch mode (no callback), returns default answer.
        In interactive mode (with callback), prompts human.

        Args:
            question: Question to ask
            context: Optional domain-specific context
            suggestions: Optional list of suggested answers
            artifacts: Optional list of relevant artifacts

        Returns:
            Human's response or default answer

        Example:
            >>> answer = role.ask_human(
            ...     "What tone should this scene have?",
            ...     suggestions=["dark", "lighthearted", "neutral"]
            ... )
        """
        # Build callback context
        callback_context: dict[str, Any] = {
            "question": question,
            "context": context or {},
            "suggestions": suggestions or [],
            "artifacts": artifacts or [],
            "role": getattr(self, "role_name", self.__class__.__name__),
        }

        # Call the callback
        return self.human_callback(question, callback_context)

    def ask_yes_no(
        self,
        question: str,
        default: bool = True,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Ask a yes/no question.

        Args:
            question: Question to ask
            default: Default answer if in batch mode
            context: Optional context

        Returns:
            True for yes, False for no

        Example:
            >>> if role.ask_yes_no("Generate images for this scene?"):
            ...     generate_images()
        """
        response = self.ask_human(
            question,
            context=context,
            suggestions=["yes", "no"],
        )

        # Parse response
        response_lower = response.lower().strip()

        if response_lower in ["yes", "y", "true", "1"]:
            return True
        elif response_lower in ["no", "n", "false", "0"]:
            return False
        else:
            # If unclear, use default
            return default

    def ask_choice(
        self,
        question: str,
        choices: list[str],
        default: int = 0,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Ask human to choose from a list of options.

        Args:
            question: Question to ask
            choices: List of choices
            default: Index of default choice (0-based)
            context: Optional context

        Returns:
            Selected choice

        Example:
            >>> tone = role.ask_choice(
            ...     "Select scene tone:",
            ...     ["dark", "lighthearted", "neutral"]
            ... )
        """
        response = self.ask_human(
            question,
            context=context,
            suggestions=choices,
        )

        # If response matches a choice, return it
        if response in choices:
            return response

        # Try to parse as number (1-indexed)
        try:
            index = int(response) - 1
            if 0 <= index < len(choices):
                return choices[index]
        except ValueError:
            pass

        # Fall back to default
        return choices[default] if choices else ""
