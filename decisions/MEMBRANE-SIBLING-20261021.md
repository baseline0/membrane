# Membrane: declare tool-lit-review as a runner sibling (2026-10-21)

## Declaration

`pyproject.toml` now carries:

```toml
[tool.fleet-runner]
siblings = ["tool-lit-review"]
```

Dependency lines are unchanged. The existing `[tool.uv.sources]` entry
(`tool-lit-review = { path = "../tool-lit-review", editable = true }`) is what needs the sibling.

Commit: `c4ffd4870ef8630e4f5ffb67173467bff2dcebf3` on `agent/membrane-sibling`.

## Tests that need the sibling

- `tests/unit/test_paper_fetcher.py` builds the `uv run --project .../tool-lit-review tool-lit-review fetch-list` command.
  It asserts on the command shape with a fake `subprocess.run`, so it does not execute the sibling.
- `scripts/paper_fetcher.py` resolves `TOOL_LIT_REVIEW_PROJECT` as `parent.parent.parent / "tool-lit-review"`.
  In the container this is `/tool-lit-review`, which matches the runner layout.
- The real need is at provisioning: `uv sync --frozen` resolves the `../tool-lit-review` path source.
  Without the sibling, the lock cannot be installed.
- `tests/host/test_benchmark_reproducibility.py` mentions the sibling only in a string. It is outside the container run.

No `tool_lit_review` module is imported by membrane's source or tests.

## Host run (workspace, `just test-unit`)

- Exit code: 0
- Result: 190 passed in 2.36s
- The sibling resolved from the workspace read checkout at `/home/mark/.fleet/worktrees/membrane-sibling/tool-lit-review`.

## LXD run (`infrastructure/scripts/lxc/run-experiment.sh`)

Image: `test-runner-313`, fingerprint `2781bbfeee5d7a2a52058d5c0f0ba7b6ef7105158d9ccdb787ecf37c439eff48`.
Network: `none` (profile `isolated-net`, no NIC, no name resolution verified before the command).

Attempt 1, `uv run pytest tests/unit -m unit -q`: exit 2, no tests ran. `uv run` tried to rebuild the
project and fetch `hatchling` from PyPI, which the offline container cannot reach. The sibling was built
(`Building tool-lit-review @ file:///tool-lit-review`). Outputs: `/tmp/claude-1004/membrane-lxd-out`.

Attempt 2, `uv run --no-sync pytest tests/unit -m unit -q`: exit 1. Result: 189 passed, 1 failed.
- Failing test: `tests/unit/test_multiset_treenode.py::TestMembraneTree::test_anytree`
- Cause: `FileNotFoundError: [Errno 2] No such file or directory: 'dot'` (anytree DotExporter). Blocked on the
  graphviz change in the infrastructure image. Not worked around.
- Outputs: `/tmp/claude-1004/membrane-lxd-out-2/runner.json`, log `/tmp/claude-1004/membrane-lxd-2.log`.

Container cleanup: `lxc list` shows no `exp-membrane-*` containers after both runs (both were deleted on exit; `--keep` was off).

## Sibling-present evidence

`runner.json` (attempt 2):
- `"declared": {"siblings": ["tool-lit-review"], "files": []}`
- `"siblings": {"tool-lit-review": {"path": ".../tool-lit-review", "commit": "d65343c7e10b5af775b395c512e0ec1646289b8f"}}`
- `"git_metadata": "commit"`, `"network": "none"`

Attempt 1 log shows `Building tool-lit-review @ file:///tool-lit-review` inside the container, which shows the
sibling was unpacked at `/tool-lit-review` and resolved by the path source.

## Notes

- The `--no-sync` flag was needed because the offline container cannot rebuild the project. This is a
  runner finding, not a membrane change: a `uv run` without `--no-sync` triggers a build that needs PyPI.
- No change was made to tool-lit-review, tool-rag, or infrastructure.
