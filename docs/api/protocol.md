# Protocol API Reference

The `questfoundry.protocol` module provides the Layer 4 protocol implementation for QuestFoundry agent communication. It implements envelope-based message passing with validation and transport abstraction.

## Overview

The protocol module consists of:

- **Envelope Models**: Pydantic models for protocol messages
- **Protocol Client**: High-level API for sending/receiving messages
- **Transport Layer**: Abstraction for message delivery (file-based, HTTP, etc.)
- **Conformance Validation**: Protocol specification compliance checking

## Quick Start

```python
from questfoundry.protocol import ProtocolClient, HotCold, SpoilerPolicy

# Create a client for the Showrunner role
client = ProtocolClient.from_workspace("./my-project", "SR")

# Create and send a message
envelope = client.create_envelope(
    receiver="LW",  # Lore Weaver
    intent="canon.create",
    payload_type="canon_pack",
    payload_data={
        "pack_id": "PACK-001",
        "title": "World Fundamentals",
        "entries": []
    },
    hot_cold=HotCold.HOT,
    player_safe=False,
    spoilers=SpoilerPolicy.ALLOWED
)

client.send(envelope)

# Send and wait for response
response = client.send_and_wait(envelope, timeout=10.0)
if response:
    print(f"Received response: {response.intent}")
```

## ProtocolClient

The main interface for protocol communication.

### Constructor

```python
ProtocolClient(transport: Transport, sender_role: RoleName)
```

**Parameters:**
- `transport` (Transport): Transport implementation to use
- `sender_role` (RoleName): Role name for this client (e.g., "SR", "GK", "LW")

### Factory Methods

#### `from_workspace()`

```python
@classmethod
def from_workspace(
    cls,
    workspace_dir: Path | str,
    sender_role: RoleName
) -> ProtocolClient
```

Create a client using file-based transport in a workspace directory.

**Parameters:**
- `workspace_dir`: Path to workspace directory (creates `.questfoundry/hot/` subdirs)
- `sender_role`: Role name for this client

**Returns:** ProtocolClient instance

**Example:**
```python
client = ProtocolClient.from_workspace("./my-adventure", "SR")
```

### Core Methods

#### `create_envelope()`

```python
def create_envelope(
    self,
    receiver: RoleName,
    intent: str,
    payload_type: str,
    payload_data: dict[str, Any],
    hot_cold: HotCold = HotCold.HOT,
    player_safe: bool = True,
    spoilers: SpoilerPolicy = SpoilerPolicy.FORBIDDEN,
    correlation_id: str | None = None,
    reply_to: str | None = None,
    tu: str | None = None,
    snapshot: str | None = None,
    refs: list[str] | None = None,
) -> Envelope
```

Create an envelope with sensible defaults. Automatically sets protocol version, message ID, timestamp, and sender.

**Parameters:**
- `receiver`: Receiving role (e.g., "GK", "LW", "SS")
- `intent`: Intent verb (e.g., "scene.write", "hook.create")
- `payload_type`: Artifact type for payload (e.g., "hook_card", "tu_brief")
- `payload_data`: Payload data dictionary
- `hot_cold`: Workspace designation (default: HOT)
- `player_safe`: Whether safe for Player Narrator (default: True)
- `spoilers`: Spoiler policy (default: FORBIDDEN)
- `correlation_id`: Optional correlation ID for request/response
- `reply_to`: Optional message ID this replies to
- `tu`: Optional TU ID (e.g., "TU-2025-11-07-SR01")
- `snapshot`: Optional snapshot reference
- `refs`: Optional list of referenced artifact IDs

**Returns:** Constructed Envelope

**Example:**
```python
envelope = client.create_envelope(
    receiver="SS",
    intent="scene.write",
    payload_type="tu_brief",
    payload_data={
        "brief_id": "BRIEF-001",
        "description": "Opening scene"
    },
    tu="TU-2025-11-07-SR01"
)
```

#### `send()`

```python
def send(self, envelope: Envelope, validate: bool = True) -> None
```

Send an envelope through the transport.

**Parameters:**
- `envelope`: The envelope to send
- `validate`: Whether to validate conformance (default: True)

**Raises:**
- `ValueError`: If envelope fails conformance validation
- `IOError`: If sending fails

**Example:**
```python
try:
    client.send(envelope)
except ValueError as e:
    print(f"Validation failed: {e}")
```

#### `receive()`

```python
def receive(self, validate: bool = True) -> Iterator[Envelope]
```

Receive envelopes from the transport. Returns an iterator that yields envelopes as they are received.

**Parameters:**
- `validate`: Whether to validate conformance (default: True)

**Yields:** Envelope objects

**Raises:**
- `IOError`: If receiving fails

**Example:**
```python
for envelope in client.receive():
    print(f"Received {envelope.intent} from {envelope.sender.role}")
    if envelope.intent == "scene.complete":
        break
```

#### `send_and_wait()`

```python
def send_and_wait(
    self,
    envelope: Envelope,
    timeout: float = 10.0,
    validate: bool = True,
) -> Envelope | None
```

Send an envelope and wait for a correlated response. Automatically adds a correlation_id if not present.

**Parameters:**
- `envelope`: The envelope to send
- `timeout`: Timeout in seconds (default: 10.0)
- `validate`: Whether to validate conformance (default: True)

**Returns:** Response envelope if received, None if timeout

**Raises:**
- `ValueError`: If envelope fails conformance validation
- `IOError`: If sending/receiving fails

**Example:**
```python
response = client.send_and_wait(envelope, timeout=30.0)
if response:
    result = response.payload.data
    print(f"Got result: {result}")
else:
    print("Request timed out")
```

#### `subscribe()`

```python
def subscribe(
    self,
    intent_pattern: str,
    callback: Callable[[Envelope], None]
) -> None
```

Subscribe to messages matching an intent pattern. The callback will be invoked for each matching message during `receive()`.

**Parameters:**
- `intent_pattern`: Regex pattern to match intents (e.g., `"scene\..*"`, `"hook\.(create|update)"`)
- `callback`: Function to call with matching envelopes

**Example:**
```python
def handle_scene_messages(envelope: Envelope):
    print(f"Scene message: {envelope.intent}")

client.subscribe(r"scene\..*", handle_scene_messages)

# Now when you receive, callbacks are automatically invoked
for envelope in client.receive():
    # Callbacks already called for matching envelopes
    pass
```

#### `unsubscribe_all()`

```python
def unsubscribe_all() -> None
```

Remove all subscriptions.

### Context Manager Support

ProtocolClient supports Python's context manager protocol:

```python
with ProtocolClient.from_workspace("./my-project", "SR") as client:
    envelope = client.create_envelope(...)
    client.send(envelope)
# Transport is automatically closed when exiting the context
```

## Envelope Models

### Envelope

The main protocol envelope wrapping all messages.

**Fields:**
- `protocol` (Protocol): Protocol metadata with name and version
- `id` (str): Unique message ID (typically URN format)
- `time` (datetime): Message creation timestamp
- `sender` (Sender): Message sender information
- `receiver` (Receiver): Message receiver information
- `intent` (str): Intent verb (e.g., "scene.write", "hook.create")
- `correlation_id` (str | None): Correlation identifier for request/response
- `reply_to` (str | None): Message ID this is replying to
- `context` (Context): Message context and traceability
- `safety` (Safety): Safety and spoiler policies
- `payload` (Payload): Message payload with type and data
- `refs` (list[str]): Referenced artifact IDs

**Example:**
```python
from questfoundry.protocol import Envelope

# Typically created via EnvelopeBuilder or ProtocolClient.create_envelope()
envelope = Envelope(
    protocol=Protocol(name="qf-protocol", version="1.0.0"),
    id="urn:uuid:550e8400-e29b-41d4-a716-446655440000",
    time=datetime.now(),
    sender=Sender(role="SR"),
    receiver=Receiver(role="LW"),
    intent="canon.create",
    context=Context(hot_cold=HotCold.HOT, tu="TU-2025-11-07-SR01"),
    safety=Safety(player_safe=False, spoilers=SpoilerPolicy.ALLOWED),
    payload=Payload(type="canon_pack", data={"pack_id": "PACK-001"})
)
```

### EnvelopeBuilder

Fluent builder for constructing envelopes. Provides a chainable interface for setting all envelope fields.

**Methods:**
- `with_protocol(version: str)` - Set protocol version
- `with_id(message_id: str)` - Set message ID
- `with_time(time: datetime)` - Set message time
- `with_sender(role: RoleName, agent: str | None = None)` - Set sender
- `with_receiver(role: RoleName)` - Set receiver
- `with_intent(intent: str)` - Set intent
- `with_correlation_id(correlation_id: str)` - Set correlation ID
- `with_reply_to(reply_to: str)` - Set reply_to
- `with_context(hot_cold, tu, snapshot, loop)` - Set context
- `with_safety(player_safe, spoilers)` - Set safety
- `with_payload(artifact_type, data)` - Set payload
- `with_refs(refs: list[str])` - Set references
- `build()` - Build and validate the envelope

**Example:**
```python
from questfoundry.protocol import EnvelopeBuilder
from datetime import datetime
import uuid

envelope = (
    EnvelopeBuilder()
    .with_protocol("1.0.0")
    .with_id(f"urn:uuid:{uuid.uuid4()}")
    .with_time(datetime.now())
    .with_sender("SR", agent="human:author1")
    .with_receiver("GK")
    .with_intent("hook.validate")
    .with_context(HotCold.HOT, tu="TU-2025-11-07-SR01")
    .with_safety(player_safe=True, spoilers=SpoilerPolicy.FORBIDDEN)
    .with_payload("hook_card", {"hook_id": "HOOK-001"})
    .with_refs(["CANON-001", "STYLE-001"])
    .build()
)
```

### Protocol

Protocol version information.

**Fields:**
- `name` (str): Protocol name (always "qf-protocol")
- `version` (str): Semantic version string (e.g., "1.0.0")

### Sender

Message sender information.

**Fields:**
- `role` (RoleName): Sending role (e.g., "SR", "GK", "LW")
- `agent` (str | None): Optional human/agent identifier (e.g., "human:alice")

### Receiver

Message receiver information.

**Fields:**
- `role` (RoleName): Receiving role (e.g., "SR", "GK", "LW")

### Context

Message context and traceability.

**Fields:**
- `hot_cold` (HotCold): Workspace designation ("hot" or "cold")
- `tu` (str | None): Thematic Unit ID (format: "TU-YYYY-MM-DD-ROLEXX")
- `snapshot` (str | None): Cold snapshot reference (format: "Cold @ YYYY-MM-DD")
- `loop` (str | None): Loop/playbook context

### Safety

Safety and spoiler policies.

**Fields:**
- `player_safe` (bool): Whether content is safe for Player Narrator (PN boundary)
- `spoilers` (SpoilerPolicy): Spoiler content policy ("forbidden", "allowed", "redacted")

### Payload

Message payload with type and data.

**Fields:**
- `type` (str): Payload artifact type (e.g., "hook_card", "tu_brief")
- `data` (dict[str, Any]): Payload data dictionary

## Type Enums

### HotCold

Workspace designation.

**Values:**
- `HotCold.HOT` - "hot" - Work in progress
- `HotCold.COLD` - "cold" - Curated, stable

### SpoilerPolicy

Spoiler content policy.

**Values:**
- `SpoilerPolicy.FORBIDDEN` - "forbidden" - No spoilers allowed
- `SpoilerPolicy.ALLOWED` - "allowed" - Spoilers permitted
- `SpoilerPolicy.REDACTED` - "redacted" - Spoilers removed/masked

### RoleName

Role identifiers (strings). Common roles:

- `"SR"` - Showrunner (orchestrator)
- `"GK"` - Gatekeeper (quality validation)
- `"LW"` - Lore Weaver (canon management)
- `"SS"` - Scene Smith (scene writing)
- `"PW"` - Plotwright (plot development)
- `"CC"` - Codex Curator (codex management)
- `"SL"` - Style Lead (style management)
- `"AD"` - Art Director (art direction)
- `"IL"` - Illustrator (image generation)
- `"AUD"` - Audio Director (audio direction)
- `"AP"` - Audio Producer (audio generation)
- `"PN"` - Player Narrator (player interface)
- `"BB"` - Book Binder (export/rendering)
- `"RS"` - Researcher (research tasks)
- `"TR"` - Translator (translation tasks)

## Conformance Validation

### `validate_envelope_conformance()`

```python
def validate_envelope_conformance(envelope: Envelope) -> ConformanceResult
```

Validate envelope against protocol conformance rules.

**Parameters:**
- `envelope`: Envelope to validate

**Returns:** ConformanceResult with conformance status and any violations

**Example:**
```python
from questfoundry.protocol import validate_envelope_conformance

result = validate_envelope_conformance(envelope)
if result.conformant:
    print("Envelope is conformant")
else:
    for violation in result.violations:
        print(f"Violation: {violation.message}")
        print(f"  Rule: {violation.rule}")
        print(f"  Severity: {violation.severity}")
```

### ConformanceResult

Result of conformance validation.

**Fields:**
- `conformant` (bool): Whether envelope is conformant
- `violations` (list[ConformanceViolation]): List of violations found

### ConformanceViolation

A single conformance violation.

**Fields:**
- `rule` (str): Rule identifier (e.g., "PN_BOUNDARY")
- `message` (str): Human-readable violation message
- `severity` (str): "error" or "warning"
- `field` (str | None): Field path where violation occurred

## Transport Layer

### Transport (Abstract Base Class)

Abstract interface for message delivery.

**Methods:**
- `send(envelope: Envelope) -> None` - Send an envelope
- `receive() -> Iterator[Envelope]` - Receive envelopes
- `close() -> None` - Close transport and release resources

### FileTransport

File-based transport implementation using workspace directories.

```python
from questfoundry.protocol import FileTransport
from pathlib import Path

transport = FileTransport(Path("./my-project"))

# Send envelope
transport.send(envelope)

# Receive envelopes
for envelope in transport.receive():
    print(f"Received: {envelope.intent}")

transport.close()
```

**Directory Structure:**
```
my-project/
  .questfoundry/
    hot/
      envelopes/
        inbound/
          <role>/
            <timestamp>-<uuid>.json
        outbound/
          <role>/
            <timestamp>-<uuid>.json
```

## Usage Patterns

### Request-Response Pattern

```python
client = ProtocolClient.from_workspace("./project", "SR")

# Create request
request = client.create_envelope(
    receiver="GK",
    intent="hook.validate",
    payload_type="hook_card",
    payload_data={"hook_id": "HOOK-001", "title": "Dragon's Lair"}
)

# Send and wait for response
response = client.send_and_wait(request, timeout=30.0)
if response:
    validation_result = response.payload.data
    if validation_result.get("valid"):
        print("Hook is valid!")
    else:
        print(f"Validation errors: {validation_result.get('errors')}")
```

### Event Broadcasting Pattern

```python
# Broadcaster
client = ProtocolClient.from_workspace("./project", "SR")

event = client.create_envelope(
    receiver="*",  # Broadcast to all roles
    intent="loop.started",
    payload_type="loop_event",
    payload_data={"loop": "hook_harvest", "tu": "TU-2025-11-07-SR01"}
)

client.send(event)
```

### Subscription Pattern

```python
client = ProtocolClient.from_workspace("./project", "GK")

# Set up handlers for different intent patterns
def handle_hook_validation(envelope: Envelope):
    hook_data = envelope.payload.data
    # Validate hook...
    # Send response...

def handle_scene_validation(envelope: Envelope):
    scene_data = envelope.payload.data
    # Validate scene...

client.subscribe(r"hook\.(validate|check)", handle_hook_validation)
client.subscribe(r"scene\.validate", handle_scene_validation)

# Process messages
for envelope in client.receive():
    # Subscribed handlers are automatically invoked
    pass
```

### Async Message Processing

```python
import threading
import queue

message_queue = queue.Queue()

def receive_loop(client):
    """Background thread for receiving messages"""
    for envelope in client.receive():
        message_queue.put(envelope)

client = ProtocolClient.from_workspace("./project", "SR")

# Start receiving in background
receiver_thread = threading.Thread(target=receive_loop, args=(client,))
receiver_thread.daemon = True
receiver_thread.start()

# Process messages from queue
while True:
    try:
        envelope = message_queue.get(timeout=1.0)
        print(f"Processing: {envelope.intent}")
    except queue.Empty:
        continue
```

## Error Handling

```python
from questfoundry.protocol import ProtocolClient
from pydantic import ValidationError

client = ProtocolClient.from_workspace("./project", "SR")

try:
    envelope = client.create_envelope(
        receiver="INVALID",  # Invalid role
        intent="test",
        payload_type="test",
        payload_data={}
    )
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    client.send(envelope)
except ValueError as e:
    print(f"Conformance error: {e}")
except IOError as e:
    print(f"Transport error: {e}")
```

## Best Practices

1. **Always use context managers** when possible to ensure resources are cleaned up:
   ```python
   with ProtocolClient.from_workspace("./project", "SR") as client:
       # Use client...
   ```

2. **Enable validation by default** - Only disable for performance-critical code paths:
   ```python
   client.send(envelope, validate=True)  # Default
   ```

3. **Use correlation IDs** for request-response patterns:
   ```python
   response = client.send_and_wait(request)
   ```

4. **Set appropriate timeouts** for send_and_wait:
   ```python
   response = client.send_and_wait(request, timeout=30.0)
   if not response:
       print("Timeout - no response received")
   ```

5. **Use subscriptions** for event-driven architectures:
   ```python
   client.subscribe(r"hook\..*", handler)
   ```

6. **Set player_safe carefully** to enforce PN boundaries:
   ```python
   envelope = client.create_envelope(
       ...,
       player_safe=False,  # Contains GM-only information
       spoilers=SpoilerPolicy.ALLOWED
   )
   ```

## See Also

- [State Management API](state.md) - SQLite and file-based state management
- [Validation API](validation.md) - Schema and conformance validation
- [Export API](export.md) - View generation and export
