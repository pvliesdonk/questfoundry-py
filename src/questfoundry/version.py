"""Version information"""

from importlib.metadata import version


def get_version() -> str:
    """Return version string"""
    return version("questfoundry-py")


def get_version_tuple() -> tuple[int, ...]:
    """Return version as tuple"""
    ver = get_version()
    # Handle versions like "0.1.0.dev1" by splitting on "."
    # and taking only numeric parts
    parts = []
    for part in ver.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            break
    return tuple(parts)


__version__ = get_version()
__version_tuple__ = get_version_tuple()
