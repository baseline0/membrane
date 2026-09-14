from enum import Enum
from typing import List, TextIO

from anytree import Node, PostOrderIter

from malta.core.membrane import Membrane
from malta.core.membrane_item import MembraneItem
from malta.core.rule import apply, rule_will_fire
from malta.core.ruleset import RuleSet


class EnvState(Enum):
    STOPPED = 0
    RUNNING = 1


class Environment:
    """
    This contains the multiset tree
        the root of the tree is the top level (most external) membrane
    """

    # FUTURE - make ENUM and do proper hook
    STOP_CRITERION = "NO_RULES_FIRED"

    def __init__(self, tree: Node, rules: RuleSet, all_items: List[MembraneItem]):

        self.tree = tree

        self.rules = rules

        # the details on the items that are in the membranes and in the environment.
        # useful for legends, status updates.
        self.all_items = all_items

        # stopping criterion counter
        self.rule_fired = False
        # FUTURE - enables delayed results
        # self.no_rules_fired_counter=0

        self.running_state = EnvState.RUNNING

        # use this structure for nested membrane visuals
        self.membrane_struct = None

    def apply_rules(self, root: Node):
        # TODO - randomize rule order or add in rule priority
        # TODO - randomize membrane selection ?

        # reset stopping criterion
        self.rule_fired = False

        for node in PostOrderIter(root):
            print(f"{node.name} has: {node.contents}")

            for r in self.rules.rules:
                # does it apply? run it. update contents of the respective membrane
                if rule_will_fire(r, node.contents):
                    self.rule_fired = True
                    node.contents = apply(r, node.contents)

        # Future: wrap in condition: STOP_CRITERION == "NO_RULES_FIRED"
        if not self.rule_fired:
            self.running_state = EnvState.STOPPED

    def save_as_dot_digraph(self, fname: str):
        """
        create a .dot file with a digraph which corresponds
        to the membrane structure and contents.
        """

        with open(fname, "w") as f:
            f.write("update for use of anytree")

        raise Exception

        # with open(fname, 'w') as f:
        #     f.write('digraph d {\n')
        #
        #     f.write('\nnode[style=filled];\n')
        #
        #     if not isinstance(self.contents, MMultiset):
        #         raise ValueError
        #     else:
        #         for c in self.contents:
        #             s = self.get_items_details_as_dot(c)
        #             f.write(s)
        #
        #     for m in self.membranes:
        #         self.process_membrane_as_dot(f, m)
        #
        #     f.write('}')

    def process_membrane_as_dot(self, f: TextIO, m: Membrane):
        """
        process a single membrane,
            its contents and its submembranes
        """

        if not isinstance(m, Membrane):
            raise ValueError

        for c in m.contents:
            s = self.get_items_details_as_dot(c)
            f.write(s)

        # TODO
        try:
            if hasattr(m, "membranes"):
                for mm in m.membranes:
                    self.process_membrane_as_dot(f, mm)
        except Exception:
            raise ValueError("recursive membranes is wip. TODO")

    def get_membrane_item_by_name(self, name) -> MembraneItem:
        """
        all_items needs to include any unique items that, at start up, only exist in
        the environment.
        """

        for mi in self.all_items:
            if mi.name == name:
                return mi

        return None

    def get_items_details_as_dot(self, name: str):
        """
        the membrane has the name of the content in its multiset
        however, when drawing the dot diagram, we would like the colour for the node
        """

        mi = self.get_membrane_item_by_name(name)
        if isinstance(mi, MembraneItem):
            c = mi.colour
        else:
            raise ValueError

        if isinstance(c, str):
            if c:
                s = f"\n{name}[color={c}]\n"
            else:
                s = f"{name}\n"
        return s
