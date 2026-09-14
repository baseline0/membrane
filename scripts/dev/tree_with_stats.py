#!/usr/bin/env python3
"""
Visual tree of repo respecting .gitignore, with file/line counts.

Usage:
    python scripts/dev/tree_with_stats.py [root_dir]
    python scripts/dev/tree_with_stats.py .
"""

import fnmatch
import sys
from pathlib import Path
from typing import Set


def parse_gitignore(root: Path) -> Set[str]:
    """Parse .gitignore patterns into a set."""
    patterns = set()
    gitignore = root / ".gitignore"

    if not gitignore.exists():
        return patterns

    with open(gitignore) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.add(line)

    return patterns


def should_ignore(path: Path, root: Path, patterns: Set[str]) -> bool:
    """Check if path should be ignored based on .gitignore patterns or system dirs."""
    # Always skip VCS and system directories regardless of .gitignore
    always_skip = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", ".env"}
    if path.name in always_skip:
        return True

    rel_path = path.relative_to(root)

    for pattern in patterns:
        # Handle directory patterns
        if pattern.endswith("/"):
            pattern = pattern.rstrip("/")
            if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(str(rel_path), f"{pattern}/*"):
                return True
        else:
            # Match both filename and full path
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(rel_path), pattern):
                return True

    return False


def count_lines(filepath: Path) -> int:
    """Count lines in a text file."""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def tree_with_stats(root: Path, prefix: str = "", patterns: Set[str] = None, root_path: Path = None):
    """Recursively print tree with stats."""
    if patterns is None:
        patterns = set()
    if root_path is None:
        root_path = root

    try:
        entries = sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return

    dirs = [e for e in entries if e.is_dir()]
    files = [e for e in entries if e.is_file()]

    # Filter by gitignore
    dirs = [d for d in dirs if not should_ignore(d, root_path, patterns)]
    files = [f for f in files if not should_ignore(f, root_path, patterns)]

    # Count stats
    file_count = len(files)  # noqa: F841
    dir_count = len(dirs)  # noqa: F841
    total_lines = sum(count_lines(f) for f in files)  # noqa: F841

    # Print dirs first
    for i, directory in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1) and len(files) == 0
        connector = "└── " if is_last_dir else "├── "
        next_prefix = prefix + ("    " if is_last_dir else "│   ")

        print(f"{prefix}{connector}{directory.name}/")
        tree_with_stats(directory, next_prefix, patterns, root_path)

    # Then files with line counts
    for i, filepath in enumerate(files):
        is_last = i == len(files) - 1
        connector = "└── " if is_last else "├── "
        lines = count_lines(filepath)
        line_str = f" ({lines}L)" if lines > 0 else ""

        print(f"{prefix}{connector}{filepath.name}{line_str}")


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)

    patterns = parse_gitignore(root)

    print(f"📁 {root.name}/")
    tree_with_stats(root, patterns=patterns, root_path=root)


if __name__ == "__main__":
    main()
