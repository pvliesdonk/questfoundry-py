"""Version information"""

__version__ = "0.1.0"
__version_tuple__ = tuple(map(int, __version__.split(".")))

def get_version() -> str:
    """Return version string"""
    return __version__
