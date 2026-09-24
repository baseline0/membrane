"""
Artifact manifest management for generated PDFs.

Implements Artifact Contract v1.0:
- Manages generated/manifest.json as a build receipt
- Records PDF artifacts with SHA-256, git metadata, build command
- Provides atomic writes and safe upserts
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def get_git_metadata() -> Dict[str, Any]:
    """Capture current git commit, branch, and dirty state."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        # Check if working tree is dirty
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        dirty = len(status_result.stdout.strip()) > 0

        return {"commit": commit, "branch": branch, "dirty": dirty}
    except Exception as e:
        print(f"⚠️  Failed to capture git metadata: {e}", file=sys.stderr)
        return {"commit": "unknown", "branch": "unknown", "dirty": False}


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load existing manifest or create empty structure."""
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  Corrupt manifest: {e}", file=sys.stderr)
            return _empty_manifest()
    return _empty_manifest()


def _empty_manifest() -> Dict[str, Any]:
    """Create empty manifest structure."""
    return {
        "schema_version": "1.0",
        "repository": {"id": "membrane", "root": "."},
        "build": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "command": "",
            "git": {"commit": "", "branch": "", "dirty": False},
        },
        "artifacts": [],
    }


def record_artifact(
    pdf_path: Path,
    logical_id: str,
    build_command: str,
    manifest_path: Optional[Path] = None,
    title: Optional[str] = None,
    status: str = "draft",
    relative_to: Optional[Path] = None,
) -> bool:
    """
    Record a generated PDF artifact in the manifest.

    Args:
        pdf_path: Path to the generated PDF
        logical_id: Unique identifier for this artifact (e.g., "presentation-pdf", "paper-typst")
        build_command: The command used to build it (e.g., "just present")
        manifest_path: Path to manifest.json (default: ../generated/manifest.json, repo root)
        title: Human-readable title for the artifact
        status: Status indicator (default: "draft")
        relative_to: Calculate relative path from this directory (default: repo root)

    Returns:
        True if successful, False otherwise
    """
    # Resolve paths
    if manifest_path is None:
        manifest_path = Path("..") / "generated" / "manifest.json"

    if relative_to is None:
        relative_to = Path("..")  # Parent of paper/ directory = repo root

    # Ensure pdf_path is absolute for existence check
    abs_pdf_path = Path(pdf_path).resolve()
    if not abs_pdf_path.exists():
        print(f"❌ PDF not found: {abs_pdf_path}", file=sys.stderr)
        return False

    # Ensure PDF is non-empty
    if abs_pdf_path.stat().st_size == 0:
        print(f"❌ PDF is empty: {abs_pdf_path}", file=sys.stderr)
        return False

    # Calculate SHA-256
    sha256 = calculate_sha256(abs_pdf_path)

    # Capture git metadata
    git_meta = get_git_metadata()

    # Load existing manifest
    manifest = load_manifest(manifest_path)

    # Update build metadata
    manifest["build"]["generated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["build"]["command"] = build_command
    manifest["build"]["git"] = git_meta

    # Upsert artifact entry
    artifacts = manifest["artifacts"]
    existing_idx = next((i for i, a in enumerate(artifacts) if a["logical_id"] == logical_id), None)

    # Calculate relative path to repo root
    try:
        rel_path_str = str(abs_pdf_path.relative_to(relative_to.resolve()))
    except ValueError:
        # If relative_to is not an ancestor, just use the original path
        rel_path_str = str(pdf_path)

    artifact_entry = {
        "logical_id": logical_id,
        "path": rel_path_str,
        "sha256": sha256,
        "status": status,
    }
    if title:
        artifact_entry["title"] = title

    if existing_idx is not None:
        artifacts[existing_idx] = artifact_entry
        print(f"📝 Updated artifact: {logical_id}")
    else:
        artifacts.append(artifact_entry)
        print(f"✅ Recorded artifact: {logical_id}")

    # Write manifest atomically
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file, then rename (atomic)
        temp_path = manifest_path.with_suffix(".json.tmp")
        with open(temp_path, "w") as f:
            json.dump(manifest, f, indent=2)
        temp_path.replace(manifest_path)

        print(f"📄 Manifest updated: {manifest_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to write manifest: {e}", file=sys.stderr)
        return False


def display_manifest(manifest_path: Optional[Path] = None) -> None:
    """Display manifest in human-readable format."""
    if manifest_path is None:
        manifest_path = Path("generated") / "manifest.json"

    if not manifest_path.exists():
        print("No manifest found.")
        return

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to read manifest: {e}")
        return

    print("\n📋 Artifact Manifest")
    print("=" * 60)

    build = manifest.get("build", {})
    print(f"Repository: {manifest['repository']['id']}")
    print(f"Generated:  {build.get('generated_at', '?')}")
    print(f"Command:    {build.get('command', '?')}")
    git = build.get("git", {})
    print(f"Git commit: {git.get('commit', '?')[:12]}...")
    print(f"Git branch: {git.get('branch', '?')}")
    print(f"Dirty:      {git.get('dirty', '?')}")
    print()

    artifacts = manifest.get("artifacts", [])
    if not artifacts:
        print("No artifacts recorded.")
        return

    print("Artifacts:")
    print("-" * 60)
    for artifact in artifacts:
        logical_id = artifact.get("logical_id", "?")
        path = artifact.get("path", "?")
        sha256 = artifact.get("sha256", "?")
        status = artifact.get("status", "?")
        title = artifact.get("title", "")

        print(f"  ID:     {logical_id}")
        if title:
            print(f"  Title:  {title}")
        print(f"  Path:   {path}")
        print(f"  SHA256: {sha256[:32]}...")
        print(f"  Status: {status}")
        print()
