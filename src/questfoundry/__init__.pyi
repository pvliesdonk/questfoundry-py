"""Type stubs for questfoundry package"""

from .models import Artifact as Artifact, HookCard as HookCard, TUBrief as TUBrief
from .validators import (
    validate_instance as validate_instance,
    validate_schema as validate_schema,
)

__version__: str

__all__ = [
    "__version__",
    "Artifact",
    "HookCard",
    "TUBrief",
    "validate_schema",
    "validate_instance",
]
