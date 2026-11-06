"""Tier 2 counting-threshold check: conformance against docs/psystems/TIER2-counting-threshold.md, section 6."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import malta
from malta.psystem import Status, System, run
from malta.psystem.model import SystemError
from malta.psystem.threshold import YES, counting_threshold, decide


@pytest.mark.parametrize(
    ("n", "k", "steps", "y_count", "answer"),
    [
        (3, 2, 1, 1, True),  # T1
        (4, 2, 1, 2, True),  # T2
        (2, 2, 1, 1, True),  # T3
        (1, 2, 0, 0, False),  # T4
        (0, 1, 0, 0, False),  # T5
        (5, 1, 1, 5, True),  # T6
    ],
)
def test_hand_derived_cases(n, k, steps, y_count, answer):
    yes, result = decide("a", k, n)
    assert result.status is Status.HALTED
    assert result.steps == steps
    assert result.final["0"].get(YES, 0) == y_count
    assert result.answer == y_count
    assert yes is answer


def test_decision_is_n_at_least_k_over_a_grid_and_every_seed():
    for k in range(1, 6):
        for n in range(0, 9):
            for seed in range(5):
                yes, result = decide("a", k, n, seed=seed)
                assert result.status is Status.HALTED
                assert yes == (n >= k), (n, k, seed)
                assert result.final["0"].get("a", 0) == n % k  # the residual is what no full group consumed


def test_the_decision_is_the_same_for_every_seed():
    outcomes = {tuple(decide("a", 3, 7, seed=seed)[1].final["0"].items()) for seed in range(20)}
    assert len(outcomes) == 1


def test_the_trace_is_a_function_of_the_system_alone():
    # run() mutates the system, so each run gets a fresh one built from the same encoding
    traces = {
        json.dumps(run(counting_threshold("a", 2, 5), seed=seed, max_steps=3, record_trace=True).trace)
        for seed in range(10)
    }
    assert len(traces) == 1


def test_determinism_under_different_hash_seeds():
    script = (
        "import json; from malta.psystem.threshold import decide; "
        "print(json.dumps([decide('a', k, n, seed=s)[1].final for k in (1, 2, 3) for n in (0, 4, 7) for s in (0, 1)]))"
    )
    src_dir = str(Path(malta.__file__).resolve().parents[1])
    outputs = []
    for hash_seed in ("0", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": hash_seed, "PYTHONPATH": src_dir}
        proc = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True, timeout=60
        )
        outputs.append(proc.stdout)
    assert outputs[0] == outputs[1]
    assert outputs[0].strip()


def test_recognizing_output_cannot_say_no_in_v1():
    # Documents the open question in the spec, section 5 and 7: with only a^k -> y, the no-side is "undefined".
    system: System = counting_threshold("a", 2, 1)
    result = run(system, seed=0, max_steps=5, output={"mode": "recognize", "yes": YES, "no": "n"})
    assert result.status is Status.UNDEFINED
    assert result.steps == 0


@pytest.mark.parametrize(
    ("symbol", "k", "n"),
    [("", 1, 0), ("a", 0, 1), ("a", -1, 0), ("a", True, 0), ("a", 1.0, 0), ("a", 1, -1), ("a", 1, 2.0), (YES, 1, 1)],
)
def test_bad_encodings_are_rejected_at_construction(symbol, k, n):
    with pytest.raises(SystemError):
        counting_threshold(symbol, k, n)
