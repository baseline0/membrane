"""P-system path: rules and trees are reproducible from a seed, and the rule set's alphabet is correct."""

import pytest

from malta.core.rng import make_rng
from malta.core.rule import make_rule
from malta.core.ruleset import RuleSet, get_ruleset_1, make_random_rule_from_alphabet
from malta.core.simulation import Simulation, SimulationFactory
from malta.types.mmultiset import multiset_to_dict
from malta.types.multiset_treenode import get_polytree


def _rule(catalyst, rule_input, rule_output):
    return make_rule("r", "", catalyst=catalyst, rule_input=rule_input, rule_output=rule_output)


def test_alphabet_is_detected_from_whole_names_in_sorted_order():
    rs = RuleSet()
    rs.rules = [_rule({"gene1": 1}, {"c": 1}, {"w": 1})]
    rs.detect_alphabet_from_rules()
    assert rs.alphabet == ["c", "gene1", "w"]


def test_set_rules_without_an_alphabet_builds_it_from_the_rules():
    rs = RuleSet()
    rs.set_rules([_rule({"gene1": 1}, {"c": 1}, {"w": 1})])
    assert rs.alphabet == ["c", "gene1", "w"]


def test_a_random_rule_needs_at_least_two_letters():
    with pytest.raises(ValueError, match="at least two letters"):
        make_random_rule_from_alphabet(["a"])


def test_the_same_seed_gives_the_same_rules():
    first = [repr(r) for r in get_ruleset_1(["a", "b", "c", "w"], rng=make_rng(7)).rules]
    second = [repr(r) for r in get_ruleset_1(["a", "b", "c", "w"], rng=make_rng(7)).rules]
    assert first == second


def test_the_same_seed_gives_the_same_polytree():
    g1 = get_polytree(10, rng=make_rng(3))
    g2 = get_polytree(10, rng=make_rng(3))
    assert sorted(g1.edges) == sorted(g2.edges)


def _final_state(idx: int, seed: int) -> dict:
    sim = getattr(SimulationFactory, f"get_sim{idx}")(seed)
    while sim.current_index < Simulation.MAX_TICKS and not Simulation.COMPLETE:
        sim.next()
        if sim.environment.running_state.name == "STOPPED":
            break

    def walk(node, out):
        out[node.name] = dict(multiset_to_dict(node.contents))
        for child in node.children:
            walk(child, out)
        return out

    return walk(sim.root, {})


@pytest.mark.parametrize("idx", [3, 4])
def test_a_seeded_random_simulation_reproduces_from_its_seed(idx):
    assert _final_state(idx, 7) == _final_state(idx, 7)


def test_a_different_seed_gives_a_different_random_simulation():
    assert _final_state(3, 7) != _final_state(3, 8)
