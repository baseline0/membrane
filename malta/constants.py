"""Malta constants and paths."""

from pathlib import Path

# Root directory of the malta package
REPO_ROOT = Path(__file__).resolve().parent.parent

# Malta package root
MALTA_ROOT = Path(__file__).resolve().parent

# Commonly used paths
CONFIG_DIR = MALTA_ROOT / "config"
EXAMPLES_DIR = MALTA_ROOT / "examples"
