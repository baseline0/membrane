"""SHA-256 sidecars: a recorded hash matches until the file changes, and a non-git folder is refused."""

from pathlib import Path

import pytest

from benchmarks import artifact_sidecar as sidecar

pytestmark = pytest.mark.unit

FIXED_COMMIT = "4f1c0a9d2e7b8c63a5d0e1f2b3c4d5e6f7a8b9c0"


@pytest.fixture
def repo_commit(monkeypatch: pytest.MonkeyPatch) -> str:
    """Pin producing_commit to a fixed value, so the sidecar records a known commit without a git repository."""
    monkeypatch.setattr(sidecar, "producing_commit", lambda repo_root=None: FIXED_COMMIT)
    return FIXED_COMMIT


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
