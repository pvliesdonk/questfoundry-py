"""QuestFoundry Python Library - Layer 6"""

from importlib.metadata import version

__version__ = version("questfoundry-py")

from .models import Artifact, HookCard, TUBrief  # noqa: F401
from .validators import validate_instance, validate_schema  # noqa: F401

__all__ = [
    "__version__",
    "Artifact",
    "HookCard",
    "TUBrief",
    "validate_schema",
    "validate_instance",
]
