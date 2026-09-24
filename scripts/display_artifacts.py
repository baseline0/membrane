#!/usr/bin/env python3
"""Display artifact manifest from paper/generated/manifest.json."""

import sys
from pathlib import Path

# Add paper directory to path so we can import artifact_manifest
sys.path.insert(0, str(Path(__file__).parent.parent / "paper"))

from artifact_manifest import display_manifest

if __name__ == "__main__":
    manifest_path = Path(__file__).parent.parent / "generated" / "manifest.json"
    display_manifest(manifest_path)
