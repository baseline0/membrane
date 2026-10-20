"""SHA-256 sidecars for benchmark pipeline outputs.

Every pipeline stage that writes an output file calls write_sidecar() after the write.
The sidecar <file>.sha256 holds two lines:

    sha256: <hex digest of the file>
    commit: <git commit HEAD of the repo when the file was written>

A later run can call sidecar_matches() to confirm the file is still the one recorded.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

SIDECAR_SUFFIX = ".sha256"
REPO_ROOT = Path(__file__).resolve().parent.parent


def sha256_of(path: Path) -> str:
    """SHA-256 hex digest of a file, read in blocks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def producing_commit(repo_root: Path = REPO_ROOT) -> str:
    """Return `git rev-parse HEAD` for the repo. Raises if the repo has no HEAD."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cannot record producing commit: git rev-parse HEAD failed in {repo_root}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def sidecar_path(path: Path) -> Path:
    """Path of the sidecar for an output file: <file>.sha256 next to it."""
    path = Path(path)
    return path.with_name(path.name + SIDECAR_SUFFIX)


def write_sidecar(path: Path) -> Path:
    """Write <path>.sha256 with the file's SHA-256 and the producing commit. Returns the sidecar path."""
    path = Path(path)
    sidecar = sidecar_path(path)
    sidecar.write_text(
        f"sha256: {sha256_of(path)}\ncommit: {producing_commit()}\n",
        encoding="utf-8",
    )
    return sidecar


def read_sidecar(path: Path) -> dict[str, str]:
    """Parse the sidecar for an output file into {'sha256': ..., 'commit': ...}."""
    fields: dict[str, str] = {}
    for line in sidecar_path(path).read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition(": ")
        fields[key] = value
    return fields


def sidecar_matches(path: Path) -> bool:
    """True when the file's current SHA-256 equals the hash recorded in its sidecar."""
    return read_sidecar(path)["sha256"] == sha256_of(path)
