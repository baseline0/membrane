"""Malta constants and paths. All paths validated at import time."""

from pathlib import Path


def _validate_path(path: Path, name: str) -> Path:
    """Validate a path exists; raise RuntimeError if not."""
    if not path.exists():
        raise RuntimeError(f"{name} not found at {path} (package installation corrupted?)")
    return path


# Root directory of the malta package
REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = _validate_path(REPO_ROOT, "REPO_ROOT")

# Malta package root
MALTA_ROOT = Path(__file__).resolve().parent
MALTA_ROOT = _validate_path(MALTA_ROOT, "MALTA_ROOT")

# Commonly used paths
CONFIG_DIR = _validate_path(MALTA_ROOT / "config", "CONFIG_DIR")
EXAMPLES_DIR = _validate_path(MALTA_ROOT / "examples", "EXAMPLES_DIR")
