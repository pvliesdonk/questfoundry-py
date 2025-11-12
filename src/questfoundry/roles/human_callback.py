"""Agent-to-human communication for interactive mode."""

from abc import ABC, abstractmethod


class AbstractHumanCallback(ABC):
    """
    Abstract base class for agent-to-human communication.

    This class defines the interface for roles to ask humans questions
    during interactive mode.
    """

    @abstractmethod
    def ask_question(self, question: str, options: list[dict[str, str]] | None = None) -> str:
        """
        Ask a question to the human and get a response.

        Args:
            question: The question text to ask the human.
            options: A list of predefined options for the user to choose from.
                     Each option is a dictionary with 'key' and 'label'.

        Returns:
            The human's response as a string.
        """
        pass


class DefaultHumanCallback(AbstractHumanCallback):
    """
    Default human callback that prompts via stdin.

    This is a simple reference implementation. Production systems should
    provide their own callback that integrates with their UI (CLI, Web, etc.).
    """

    def ask_question(self, question: str, options: list[dict[str, str]] | None = None) -> str:
        """
        Ask a question via stdin and return the response.

        Args:
            question: The question to ask.
            options: A list of options to display to the user.

        Returns:
            The user's response from stdin.
        """
        print(f"\n[Agent] {question}")

        if options:
            print("\nPlease choose one of the following options:")
            for option in options:
                print(f"  [{option['key']}] {option['label']}")
            print()

        return input("Your answer: ")


class BatchModeHumanCallback(AbstractHumanCallback):
    """
    Batch mode callback that returns a default/empty response.

    Used when no human interaction is desired (automated workflows).
    """

    def ask_question(self, question: str, options: list[dict[str, str]] | None = None) -> str:
        """
        Return a default response without prompting.

        Args:
            question: The question (ignored).
            options: A list of options. If available, the key of the first
                     option is returned.

        Returns:
            The key of the first option, or an empty string.
        """
        if options:
            return options[0].get("key", "")
        return ""
