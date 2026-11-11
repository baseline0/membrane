"""Conformance cases C1 to C13 from docs/psystems/SPEC-v1.md, section 8. Expected values are the spec's, derived by hand."""

from collections import Counter

import pytest

from malta.psystem import Region, Rule, Status, System, run
from malta.psystem.model import SystemError


def rule(input_dict: dict[str, int], output: list, **kwargs) -> Rule:
    """Helper to create Rule with dict input/catalyst. Type: ignore needed because Rule.__post_init__ converts dicts to Counter."""
    kwargs_with_counters = {}
    if "catalyst" in kwargs:
        kwargs_with_counters["catalyst"] = Counter(kwargs["catalyst"])
    return Rule(Counter(input_dict), output, **kwargs_with_counters)  # type: ignore[arg-type]


def only(region_name: str, contents: dict[str, int], rules: list | None = None, children: list | None = None) -> Region:
    """Helper to create Region with dict contents. Type: ignore needed because Region.__post_init__ converts dict to Counter."""
    if rules is None:
        rules = []
    if children is None:
        children = []
    return Region(region_name, Counter(contents), list(rules), list(children))


def out_of(config):
    """config: {region name: contents}, as plain dicts for comparison."""
    return {k: dict(v) for k, v in config.items()}


def test_c1_maximal_parallel_rewriting_in_one_region():
    skin = only("0", {"a": 3}, [rule({"a": 1}, [("b", "here"), ("b", "here")])])
    r = run(System(skin), seed=0, max_steps=10, output={"mode": "count", "symbol": "b"})
    assert r.status is Status.HALTED and r.steps == 1
    assert out_of(r.final) == {"0": {"b": 6}}
    assert r.answer == 6


def test_c2_two_rules_competing_for_the_same_input():
    results = set()
    for seed in range(20):
        skin = only("0", {"a": 2}, [rule({"a": 1}, [("b", "here")]), rule({"a": 1}, [("c", "here")])])
        r = run(System(skin), seed=seed, max_steps=10)
        assert r.status is Status.HALTED and r.steps == 1
        contents = out_of(r.final)["0"]
        assert "a" not in contents
        assert sum(contents.values()) == 2
        results.add(tuple(sorted(contents.items())))
    assert results <= {(("b", 2),), (("c", 2),), (("b", 1), ("c", 1))}
    assert len(results) > 1  # the seed matters across these runs


def test_c3_catalyst_is_read_not_consumed():
    skin = only("0", {"c": 1, "a": 3}, [rule({"a": 1}, [("b", "here")], catalyst={"c": 1})])
    r = run(System(skin), seed=0, max_steps=10)
    assert r.status is Status.HALTED and r.steps == 1
    assert out_of(r.final) == {"0": {"c": 1, "b": 3}}


def test_c4_missing_catalyst_blocks_the_rule():
    skin = only("0", {"a": 3}, [rule({"a": 1}, [("b", "here")], catalyst={"c": 1})])
    r = run(System(skin), seed=0, max_steps=10)
    assert r.status is Status.HALTED and r.steps == 0
    assert out_of(r.final) == {"0": {"a": 3}}


def test_c5_synchrony_produced_objects_wait_one_step():
    skin = only("0", {"a": 1}, [rule({"a": 1}, [("b", "here")]), rule({"b": 1}, [("c", "here")])])
    r = run(System(skin), seed=0, max_steps=10, record_trace=True)
    assert r.status is Status.HALTED and r.steps == 2
    assert [out_of(c) for c in r.trace] == [
        {"0": {"a": 1}},
        {"0": {"b": 1}},
        {"0": {"c": 1}},
    ]


def test_c6_target_out_sends_objects_to_the_parent():
    child = only("s", {"a": 2}, [rule({"a": 1}, [("b", "out")])])
    skin = only("0", {}, children=[child])
    r = run(System(skin), seed=0, max_steps=10)
    assert r.status is Status.HALTED and r.steps == 1
    assert out_of(r.final) == {"0": {"b": 2}, "s": {}}


def test_c7_target_in_sends_objects_to_a_child():
    child = only("s", {})
    skin = only("0", {"a": 2}, [rule({"a": 1}, [("b", ("in", "s"))])], children=[child])
    r = run(System(skin), seed=0, max_steps=10)
    assert r.status is Status.HALTED and r.steps == 1
    assert out_of(r.final) == {"0": {}, "s": {"b": 2}}


def test_c8_regions_run_in_the_same_step():
    child = only("s", {"a": 1}, [rule({"a": 1}, [("b", "here")])])
    skin = only("0", {"a": 1}, [rule({"a": 1}, [("b", "here")])], children=[child])
    r = run(System(skin), seed=0, max_steps=10)
    assert r.status is Status.HALTED and r.steps == 1
    assert out_of(r.final) == {"0": {"b": 1}, "s": {"b": 1}}


def test_c9_empty_configuration_halts_immediately():
    skin = only("0", {}, [rule({"a": 1}, [("b", "here")])])
    r = run(System(skin), seed=0, max_steps=10)
    assert r.status is Status.HALTED and r.steps == 0


def test_c10_timeout_reports_no_answer():
    skin = only("0", {"a": 1}, [rule({"a": 1}, [("a", "here"), ("a", "here")])])
    r = run(System(skin), seed=0, max_steps=5, output={"mode": "count", "symbol": "a"})
    assert r.status is Status.TIMEOUT and r.steps == 5
    assert out_of(r.final) == {"0": {"a": 2**5}}
    assert r.answer is None


@pytest.mark.parametrize(
    "rule_outputs, expected",
    [
        ([("yes", "here")], Status.YES),
        ([("no", "here")], Status.NO),
        ([("yes", "here"), ("yes", "here"), ("no", "here")], Status.UNDEFINED),
    ],
)
def test_c11_recognizing_system(rule_outputs, expected):
    skin = only("0", {"a": 1}, [rule({"a": 1}, rule_outputs)])
    r = run(System(skin), seed=0, max_steps=10, output={"mode": "recognize", "yes": "yes", "no": "no"})
    assert r.status is expected and r.steps == 1


def _c2_system():
    return only("0", {"a": 2}, [rule({"a": 1}, [("b", "here")]), rule({"a": 1}, [("c", "here")])])


def test_c12_the_same_seed_gives_the_same_trace():
    first = run(System(_c2_system()), seed=5, max_steps=10, record_trace=True).trace
    second = run(System(_c2_system()), seed=5, max_steps=10, record_trace=True).trace
    assert first == second


def test_c13_invalid_targets_are_rejected_at_construction():
    with pytest.raises(SystemError):
        System(only("0", {"a": 1}, [rule({"a": 1}, [("b", "out")])]))
    with pytest.raises(SystemError):
        System(only("0", {"a": 1}, [rule({"a": 1}, [("b", ("in", "nosuch"))])], children=[only("s", {})]))


def test_a_catalyst_is_never_used_up_by_another_instance_in_the_same_step():
    """Spec section 4, condition 2. Only one c: either the catalysed rule or the consuming rule fires, not both."""
    results = set()
    for seed in range(20):
        skin = only(
            "0",
            {"c": 1, "a": 1},
            [rule({"a": 1}, [("b", "here")], catalyst={"c": 1}), rule({"c": 1}, [("d", "here")])],
        )
        r = run(System(skin), seed=seed, max_steps=1)
        results.add(tuple(sorted(out_of(r.final)["0"].items())))
    assert results <= {(("b", 1), ("c", 1)), (("a", 1), ("d", 1))}
