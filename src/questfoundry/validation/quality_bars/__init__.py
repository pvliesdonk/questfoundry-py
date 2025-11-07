"""Quality bar validators for gatekeeper checks."""

from .base import QualityBar, QualityBarResult, QualityIssue
from .integrity import IntegrityBar
from .reachability import ReachabilityBar
from .style import StyleBar
from .gateways import GatewaysBar
from .nonlinearity import NonlinearityBar
from .determinism import DeterminismBar
from .presentation import PresentationBar
from .spoiler_hygiene import SpoilerHygieneBar

__all__ = [
    "QualityBar",
    "QualityBarResult",
    "QualityIssue",
    "IntegrityBar",
    "ReachabilityBar",
    "StyleBar",
    "GatewaysBar",
    "NonlinearityBar",
    "DeterminismBar",
    "PresentationBar",
    "SpoilerHygieneBar",
]

# Registry of all quality bars
QUALITY_BARS = {
    "integrity": IntegrityBar,
    "reachability": ReachabilityBar,
    "style": StyleBar,
    "gateways": GatewaysBar,
    "nonlinearity": NonlinearityBar,
    "determinism": DeterminismBar,
    "presentation": PresentationBar,
    "spoiler_hygiene": SpoilerHygieneBar,
}


def get_quality_bar(name: str) -> type[QualityBar]:
    """Get a quality bar class by name."""
    if name not in QUALITY_BARS:
        raise ValueError(f"Unknown quality bar: {name}")
    return QUALITY_BARS[name]
