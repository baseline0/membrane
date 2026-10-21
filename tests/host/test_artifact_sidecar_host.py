"""Sidecar producing_commit runs real git: a folder that is not a repository is refused. Runs on the host only."""

from pathlib import Path

import pytest

from benchmarks import artifact_sidecar as sidecar


def test_producing_commit_refuses_a_folder_that_is_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="cannot record producing commit"):
        sidecar.producing_commit(tmp_path)
