"""SHA-256 sidecars: a recorded hash matches until the file changes, and a non-git folder is refused."""

import os
import subprocess
from pathlib import Path

import pytest

from benchmarks import artifact_sidecar as sidecar

pytestmark = pytest.mark.unit

IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def make_repo(root: Path) -> str:
    """A git repo with one commit. Returns its HEAD."""
    env = {**os.environ, **IDENTITY}
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "seed.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True, env=env)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()


@pytest.fixture
def repo_commit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Point producing_commit at the temporary repo, so the sidecar records that repo's HEAD."""
    commit = make_repo(tmp_path)
    monkeypatch.setattr(sidecar, "producing_commit", lambda repo_root=None: commit)
    return commit


def test_sidecar_records_the_hash_and_the_producing_commit(tmp_path: Path, repo_commit: str) -> None:
    output = tmp_path / "out.csv"
    output.write_text("a,b\n1,2\n", encoding="utf-8")

    sidecar.write_sidecar(output)

    fields = sidecar.read_sidecar(output)
    assert fields == {"sha256": sidecar.sha256_of(output), "commit": repo_commit}


def test_hash_matches_until_the_file_changes(tmp_path: Path, repo_commit: str) -> None:
    output = tmp_path / "out.csv"
    output.write_text("a,b\n1,2\n", encoding="utf-8")
    sidecar.write_sidecar(output)
    assert sidecar.sidecar_matches(output) is True

    output.write_text("a,b\n1,3\n", encoding="utf-8")

    assert sidecar.sidecar_matches(output) is False


def test_producing_commit_refuses_a_folder_that_is_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="cannot record producing commit"):
        sidecar.producing_commit(tmp_path)
