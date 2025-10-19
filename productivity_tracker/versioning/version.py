"""
Application version following Semantic Versioning 2.0.0
"""

__version__ = "0.1.0"  # MAJOR.MINOR.PATCH

MAJOR = 0  # Breaking changes
MINOR = 1  # New features, backwards compatible
PATCH = 0  # Bug fixes, backwards compatible

# Version metadata
VERSION_INFO = {
    "version": __version__,
    "major": MAJOR,
    "minor": MINOR,
    "patch": PATCH,
    "release_date": "19-10-2025",  # DD-MM-YYYY
    "git_commit": None,  # Populated at build time
}


def get_version():
    """Returns the current version string"""
    return __version__


def get_version_info():
    """Returns detailed version information"""
    return VERSION_INFO
