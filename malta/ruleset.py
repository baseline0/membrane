import random
from typing import List

from malta.rule import Rule, make_rule
from malta.util import NameGenerator


class RuleSet:
    def __init__(self):

        # the list of symbols which are valid
        # this is the list of all catalysts, inputs and outputs
        self.alphabet = []

        # the set of rules
        self.rules = []

    def set_alphabet(self, alphabet: List[str]) -> None:
        self.alphabet = alphabet

    def set_rules(self, rules: List[Rule]) -> None:

        self.rules = rules

        if not self.alphabet:
            # if None or empty list
            # generate the alphabet from their presence in rules
            self.detect_alphabet_from_rules()
            # end state: alphabet and rules are consistent
        else:
            # ensure that the rules match the already existing alphabet
            for r in rules:
                # TODO
                print(r)

    def detect_alphabet_from_rules(self):

        self.alphabet = []

        temp = set()

        for r in self.rules:
            for c in r.catalyst:
                temp.update(c)
            for c in r.input:
                temp.update(c)
            for c in r.output:
                temp.update(c)

        self.alphabet = list(temp)


def make_random_rule_from_alphabet(alphabet: List[str]) -> Rule:
    """
    catalyst CANNOT be an input or output :)

    also, the input CANNOT be the output :)

    a simple rule generator.
        select one letter from alphabet as catalyst
        and a DISTINCT one for input and a DIFFERENT one for output

    CONSTRAINT: multiplicity 1 for all.
    FUTURE: random multiplicity
    """

    name = NameGenerator.get_rand_name()
    catalyst = None
    r_input = None
    r_output = None

    if len(alphabet) < 2:
        # the single letter just multiplies?
        print("add more letters to alphabet")
        return

    if len(alphabet) == 2:
        print("making a rule without a catalyst since alphabet is size:2")
        # coin flip for which letter is input or output
        coin = random.randint(0, 1)
        if coin == 0:
            r_input = {alphabet[0]: 1}
            r_output = {alphabet[1]: 1}
        else:
            r_input = {alphabet[1]: 1}
            r_output = {alphabet[0]: 1}
        descr = "coin flip"
    else:
        selected = random.sample(alphabet, 3)
        s = "".join([x for x in selected])
        descr = f"{name}: {s}"

        catalyst = {selected[0]: 1}
        r_input = {selected[1]: 1}
        r_output = {selected[2]: 1}

    r = make_rule(name=name, descr=descr, catalyst=catalyst, rule_input=r_input, rule_output=r_output)
    return r


def make_random_rules_from_alphabet(alphabet: List[str], n: int = 10) -> List[Rule]:
    """
    alphabet: a list of strings, each of which is the identifier of a membrane item
    n: the number of rules to make. its ok if we end up with duplicate rules here. if this happens,
    the interpretation is that the duplicated rule is more likely
    """

    print(f"making random rules from alphabet: {alphabet}")
    ruleset = RuleSet()

    if n < 0:
        n = 10

    for i in range(1, n):
        r = make_random_rule_from_alphabet(alphabet)
        ruleset.rules.append(r)

    return ruleset


def get_ruleset_1(alphabet: List[str]) -> RuleSet:
    """
    alphabet - ideally this is defined by the json file of membrane items and is the keys (identifiers)

    """

    return make_random_rules_from_alphabet(alphabet)
