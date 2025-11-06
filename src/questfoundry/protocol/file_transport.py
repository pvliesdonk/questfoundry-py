"""File-based transport for QuestFoundry protocol messages"""

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterator

from pydantic import ValidationError

from .envelope import Envelope
from .transport import Transport


class FileTransport(Transport):
    """
    File-based transport implementation.

    Messages are written to and read from filesystem directories.
    This implementation is suitable for local development and testing,
    as well as simple inter-process communication.

    Directory structure:
        workspace_dir/
            messages/
                inbox/       - Incoming messages to be received
                outbox/      - Outgoing messages sent by this transport
                processed/   - Acknowledged messages (archived)

    Message files are named: {timestamp}-{uuid}.json

    Example:
        >>> transport = FileTransport("/path/to/workspace")
        >>> envelope = Envelope(...)
        >>> transport.send(envelope)
        >>> for received in transport.receive():
        ...     print(f"Received: {received.intent}")
    """

    def __init__(self, workspace_dir: str | Path):
        """
        Initialize file transport.

        Args:
            workspace_dir: Path to workspace directory
        """
        self.workspace_dir = Path(workspace_dir)
        self.messages_dir = self.workspace_dir / "messages"
        self.inbox_dir = self.messages_dir / "inbox"
        self.outbox_dir = self.messages_dir / "outbox"
        self.processed_dir = self.messages_dir / "processed"

        # Create directories if they don't exist
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def send(self, envelope: Envelope) -> None:
        """
        Send an envelope by writing it to the outbox directory.

        Uses atomic write operation (temp file + rename) to prevent
        corruption from concurrent access.

        Args:
            envelope: The envelope to send

        Raises:
            IOError: If writing fails
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        message_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}-{message_id}.json"
        file_path = self.outbox_dir / filename

        # Serialize envelope to JSON
        envelope_json = envelope.model_dump_json(indent=2)

        # Atomic write: write to temp file, then rename
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=self.outbox_dir,
            delete=False,
            suffix=".tmp",
        ) as tmp_file:
            tmp_file.write(envelope_json)
            tmp_path = Path(tmp_file.name)

        # Atomic rename
        tmp_path.replace(file_path)

    def receive(self) -> Iterator[Envelope]:
        """
        Receive envelopes from the inbox directory.

        Yields envelopes in order (sorted by filename timestamp).
        After yielding, messages are moved to processed/ directory
        for acknowledgment.

        Yields:
            Envelope: Received envelopes

        Raises:
            IOError: If reading or moving files fails
            ValidationError: If envelope JSON is invalid
        """
        # Get all message files sorted by name (which includes timestamp)
        message_files = sorted(self.inbox_dir.glob("*.json"))

        for message_file in message_files:
            # Skip if file no longer exists (already processed by another iteration)
            if not message_file.exists():
                continue

            try:
                # Read envelope
                with open(message_file, "r") as f:
                    envelope_data = json.load(f)

                # Parse envelope
                envelope = Envelope.model_validate(envelope_data)

                # Yield envelope
                yield envelope

                # Acknowledge by moving to processed
                # Handle race condition where file might have been moved by
                # another process
                try:
                    processed_path = self.processed_dir / message_file.name
                    message_file.replace(processed_path)
                except FileNotFoundError:
                    # File was already moved by another process/thread, skip
                    pass

            except (FileNotFoundError, json.JSONDecodeError, ValidationError):
                # Skip if file was moved/deleted or is invalid
                # Don't raise error for these cases
                pass
            except Exception as e:
                # For other exceptions, try to move to error and raise
                if message_file.exists():
                    try:
                        error_path = self.processed_dir / f"{message_file.name}.error"
                        message_file.replace(error_path)
                    except FileNotFoundError:
                        pass
                raise IOError(
                    f"Failed to process message {message_file.name}: {e}"
                ) from e

    def close(self) -> None:
        """
        Close the transport.

        FileTransport doesn't hold open resources, so this is a no-op.
        """
        pass

    def clear_outbox(self) -> int:
        """
        Clear all messages from outbox (useful for testing).

        Returns:
            Number of messages cleared
        """
        count = 0
        for message_file in self.outbox_dir.glob("*.json"):
            message_file.unlink()
            count += 1
        return count

    def clear_inbox(self) -> int:
        """
        Clear all messages from inbox (useful for testing).

        Returns:
            Number of messages cleared
        """
        count = 0
        for message_file in self.inbox_dir.glob("*.json"):
            message_file.unlink()
            count += 1
        return count

    def clear_processed(self) -> int:
        """
        Clear all messages from processed directory (useful for testing).

        Returns:
            Number of messages cleared
        """
        count = 0
        for message_file in self.processed_dir.glob("*"):
            message_file.unlink()
            count += 1
        return count
