import json
from enum import Enum
from pathlib import Path
from typing import List, TextIO

from anytree import Node, search

from malta.environment import Environment, EnvState
from malta.membrane_item import MembraneItem, load_membrane_items_from_file
from malta.mmultiset import MMultiset, make_mmultiset, multiset_to_dict
from malta.multiset_treenode import get_branches_from_g, get_membrane_tree1, get_membrane_tree2
from malta.rule import Rule, make_rule
from malta.ruleset import RuleSet, get_ruleset_1
from malta.util import CONFIG_DIR


class NodeState(Enum):
    # can close the subgraph structure
    ALL_CHILDREN_COMPLETE = 0

    # look for other children
    CHILDREN_IN_PROGRESS = 1


class BranchManager:
    """
    given a list of branches of a directed tree with root 7 and misc leaf nodes and branches of misc length,
    write the corresponding
        [0, 1, 3]
        [0, 1, 4, 5]
        [0, 1, 6]
        [0, 1, 7]
        [0, 1, 2, 8]
        [0, 1, 2, 9]

        start0
            start1
                start3
                end3
                start4
                    start5
                    end5
                end4
                start6
                end6
                start7
                end7
                start2
                    start8
                    end8
                    start9
                    end9
                end2
            end1
        end0


    """

    # NOTE TO SELF: use anytree walker
    # for node in PostOrderIter(root):
    #     print(f'{node.name} has: {node.contents}')


class Simulation:
    MAX_TICKS = 10
    COMPLETE = False

    def __init__(self, output_dir: str = "./sims/") -> None:
        self.output_dir = output_dir

        # useful for when we use index to trigger file saves or image output
        self.current_index = 0

        # need to load config or programmatically populate: Environment()
        self.environment = None

        # root node of the membrane tree (set alongside self.environment)
        self.root = None

        # networkx graph which forms basis of Nodes
        self.graph = None

        # branches from root to leave
        self.branches = None

    def save(self, fname: str):
        # with open(fname, 'w') as f:
        #     json.dump(self.membrane_env.__dict__, f, indent=4)
        pass

    def load(self, fname: str):
        # # read in config file
        # with open(fname, "r") as f:
        #     data = json.load(f)
        #
        #     prettyprint_json(data=data)
        #
        # print(data)
        # membranes = data['membranes']
        # rules = data['rules']
        # contents = data['contents']
        # self.membrane_env = Environment(membranes, rules, contents)
        # # self._generate_grammar()
        pass

    def next(self):
        # do next tick
        # go through each membrane. apply rules.
        # if no change, is complete or HALT condition.

        print(f"tick: {self.current_index}")
        self.current_index += 1
        self.environment.apply_rules(self.root)

        # if self.current_index == 5:
        #     print('save img')
        if self.branches is not None:
            self.write_simplified_branches()

    def write_simplified_branches(self):

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        prefix = f"{self.output_dir}simplified_branch_"

        for i, b in enumerate(self.branches):
            fname = f"{prefix}{i}.dot"
            self.write_branch(fname, branch=b)

    @staticmethod
    def write_subgraph_starts(fp: TextIO, names: List[str]):
        """
        helper
        pass in the name of the nodes for digraph subcluster.
        """

        TAB = "\t"
        start_clause = "subgraph cluster_"
        depth = 1

        for name in names:
            indent = TAB * depth
            line = f"{indent}{start_clause}{name}"
            fp.write(line + "\t { \n")
            depth += 1

    @staticmethod
    def get_label_string(name: str, multiplicity: int):
        if not name or multiplicity < 1:
            return ""
        s = f'[label = "{name}:{multiplicity}" ]'
        return s

    @staticmethod
    def write_subgraph_end(fp: TextIO, node: Node):

        if not hasattr(node, "contents"):
            print("node must have contents attr for membrane items")
            raise AttributeError

        # constant indent for now
        TAB = "\t"
        indent = TAB * 2
        # node names are integers but we need char to start for dot so use node name as suffix
        suffix = node.name

        # given that dot does not automatically duplicate same named objects within a subgraph,
        # though visually representing the multiplicity with same coloured circles can be appealing,
        # we process the multiset into obj:quantity and generate a label for the circle that indicates
        # the multiplicity of the object.

        d = multiset_to_dict(node.contents)

        # need to have unique name within the membrane so add prefix based on nesting
        for k, v in d.items():
            # TODO - get node colour, label, etc
            descr = Simulation.get_label_string(k, v)
            fp.write(f"{indent} {k}{suffix}{descr}\n")

            # TODO
            # fp.write(f"label = \"membrane\" ")
        fp.write("} \n\n")

    def write_branch(self, fname: str, branch: List[int]):
        """
        branch is a list of node identifiers from leaf to root
        output is a dot file

        note: for dot, node name needs to start w character, not number

        current state: example
                digraph d {

                    subgraph cluster_0	 {
                        subgraph cluster_1	 {
                        subgraph cluster_3	 {
                        }

                        1_g[label = "g:1" ]
                        1_h[label = "h:1" ]
                    }

                 3_g[label = "g:2" ]
                 3_d[label = "d:2" ]
                 3_i[label = "i:3" ]
                 3_h[label = "h:2" ]
                 3_a[label = "a:1" ]
                 3_j[label = "j:1" ]
            }

        }


        """

        print(branch)

        with open(fname, "w") as f:
            f.write("digraph d { \n\n")

            # start all the nesting
            self.write_subgraph_starts(f, branch)

            # get the node and write its contents and close clause
            for node_id in branch:
                try:
                    if node_id == 0:
                        node_id = "root"

                    results = search.findall(self.root, filter_=lambda node: node.name == str(node_id))

                    if not len(results) == 1:
                        raise ValueError
                    node = results[0]
                    # write the contents
                    self.write_subgraph_end(f, node)

                except Exception:
                    print(f"could not access node with id {node_id}")
                    raise ValueError

            # end digraph
            f.write("}\n")

    def run(self):
        self.current_index = 0

        print("running membrane simulation")
        print(f"see output: {self.output_dir}")

        while self.current_index < Simulation.MAX_TICKS and not Simulation.COMPLETE:
            self.next()
            if self.environment.running_state == EnvState.STOPPED:
                print("stopping early based on env state. (no rule fired)")
                break

        print("DONE.")


def get_item_names_from_membrane_items(items: List[MembraneItem], names: List[str] = None) -> List[str]:
    """
    the environment needs a list of MembraneContents
    but the membrane and rule just use the names as identifiers.
    """

    if names is None:
        names = []
        # process the list
        for mi in items:
            names.append(mi.name)

        print(f"number of items is: {len(names)}")
        print(f"{names}")
        return names
    elif isinstance(names, List):
        # we are appending to an existing list
        # convert the existing list into a set.
        # process the list.
        # convert back to a list
        print("TODO")
        raise ValueError("FIXME")
    else:
        raise ValueError


def get_multiset_of_item_names_from_membrane_items(items: List[MembraneItem], names: List[str] = None) -> MMultiset:
    """
    the environment needs a list of MembraneContents
    but the membrane and rule just use the names as identifiers.
    """
    # FIXME - add in multiplicity of items to initialization

    if names is None:
        names = MMultiset()
        # process the list
        for mi in items:
            names.add(mi.name)
        return names
    elif isinstance(names, List):
        # we are appending to an existing list
        # convert the existing list into a set.
        # process the list.
        # convert back to a list
        print("TODO")
        raise ValueError("FIXME")
    else:
        raise ValueError


class SimulationFactory:
    @staticmethod
    def get_sim1() -> Simulation:
        sim = Simulation()

        alphabet = ["a", "b", "c", "w"]

        # details on the membranes items for summary report
        m_a = MembraneItem("a", descr="asset")
        m_b = MembraneItem("b", descr="budget")
        m_c = MembraneItem("c", descr="capital")
        m_w = MembraneItem("w", descr="win")
        all_items = [m_a, m_b, m_c, m_w]

        # ---------------------
        # make rules
        r_catalyst = MMultiset()
        r_catalyst.add("b")

        r_input = MMultiset()
        r_input.add("c")

        r_output = MMultiset()
        r_output.add("w")

        r = Rule(name="r1", descr="", catalyst=r_catalyst, rule_input=r_input, rule_output=r_output)

        ruleset = RuleSet()
        ruleset.rules = [r]

        # ---------------------
        # make membrane tree
        root = Node(name="root", contents=MMultiset())

        contents = MMultiset()
        contents.add("a", 1)
        contents.add("b", 4)
        contents.add("c", 2)
        s0 = Node(name="sub0", parent=root, contents=contents)

        e = Environment(tree=root, rules=ruleset, all_items=all_items)
        sim.environment = e
        sim.root = root

        return sim

    @staticmethod
    def get_sim2() -> Simulation:
        """
        same as sim1 but with more convenience functions
        """

        sim = Simulation()

        # items in alphabet are used explicity in the following rules and contents but
        # the data structure (list) is not yet part of params.
        # Future - generate rules and contents from a defined alphabet
        alphabet = ["a", "b", "c", "w"]

        # details on the membranes items for summary report
        with open(CONFIG_DIR / "sim1_items.json") as f:
            out = json.load(f)

        all_items = []
        for k, v in out.items():
            all_items.append(MembraneItem(k, descr=v))

        # ---------------------
        # make rules
        catalyst = {"b": 1}
        r_input = {"c": 1}
        r_output = {"w": 1}
        r = make_rule(
            name="r1", descr="make w from c when b present", catalyst=catalyst, rule_input=r_input, rule_output=r_output
        )

        ruleset = RuleSet()
        ruleset.rules.append(r)

        # ---------------------
        # make membrane tree
        root = Node(name="root", contents=MMultiset())

        items = {}
        items["a"] = 1
        items["b"] = 2
        items["c"] = 3
        contents = make_mmultiset(items)

        s0 = Node(name="sub0", parent=root, contents=contents)

        e = Environment(tree=root, rules=ruleset, all_items=all_items)
        sim.environment = e
        sim.root = root

        return sim

    @staticmethod
    def get_sim3() -> Simulation:
        """
        now alphabet is used as a param.

        FUTURE - alphabet will be defined/determined by the json file.
        """

        sim = Simulation()

        fname = CONFIG_DIR / "sim3_items.json"
        all_items = load_membrane_items_from_file(fname)

        alphabet = ["a", "b", "c", "w"]
        ruleset = get_ruleset_1(alphabet)
        root = get_membrane_tree1(alphabet)

        e = Environment(tree=root, rules=ruleset, all_items=all_items)
        sim.environment = e
        sim.root = root
        return sim

    @staticmethod
    def get_sim4() -> Simulation:
        """
        now we obtain alphabet from the items listed in the json file
        """
        sim = Simulation()

        fname = CONFIG_DIR / "sim4_items.json"
        all_items, alphabet = load_membrane_items_from_file(fname)

        ruleset = get_ruleset_1(alphabet)
        root, g = get_membrane_tree2(alphabet)

        # TODO clean up all this
        e = Environment(tree=root, rules=ruleset, all_items=all_items)
        sim.environment = e
        sim.root = root
        sim.graph = g

        # sim.membrane_struct = convert_tree_to_membranes(g)
        sim.branches = get_branches_from_g(g)
        # walk_dfs_post_order(g)

        return sim


def run(idx: int = 1):
    if idx == 1:
        sim = SimulationFactory.get_sim1()
    elif idx == 2:
        sim = SimulationFactory.get_sim2()
    elif idx == 3:
        sim = SimulationFactory.get_sim3()
    elif idx == 4:
        sim = SimulationFactory.get_sim4()

    sim.run()


# --------------------


if __name__ == "__main__":
    run(4)

# CURRENT STATE - sim4
#   m -= r.rule_input
# TypeError: unsupported operand type(s) for -=: 'dict' and 'MMultiset'

# CURRENT STATE - sim3
# making random rules from alphabet: ['a', 'b', 'c', 'w']
# running membrane simulation
# see output: ./sims/
# tick: 0
# sub0 has: {a, b, b, c, c, c, w, w, w, w}
# firing rule: rule
# 	catalysts: {b}
# 	input: {a}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {c}
# 	output: {a}
#
# firing rule: rule
# 	catalysts: {a}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {b}
# 	input: {a}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {c}
# 	input: {w}
# 	output: {b}
#
# root has: {}
# tick: 1
# sub0 has: {c, c, c, c, c, c, w, w, w, b}
# firing rule: rule
# 	catalysts: {w}
# 	input: {c}
# 	output: {a}
#
# firing rule: rule
# 	catalysts: {a}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {a}
# 	output: {b}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {c}
# 	input: {w}
# 	output: {b}
#
# root has: {}
# tick: 2
# sub0 has: {c, c, c, c, c, c, c, w, w, b}
# firing rule: rule
# 	catalysts: {w}
# 	input: {c}
# 	output: {a}
#
# firing rule: rule
# 	catalysts: {a}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {a}
# 	output: {b}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {c}
# 	input: {w}
# 	output: {b}
#
# root has: {}
# tick: 3
# sub0 has: {c, c, c, c, c, c, c, c, w, b}
# firing rule: rule
# 	catalysts: {w}
# 	input: {c}
# 	output: {a}
#
# firing rule: rule
# 	catalysts: {a}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {a}
# 	output: {b}
#
# firing rule: rule
# 	catalysts: {w}
# 	input: {b}
# 	output: {c}
#
# firing rule: rule
# 	catalysts: {c}
# 	input: {w}
# 	output: {b}
#
# root has: {}
# tick: 4
# sub0 has: {c, c, c, c, c, c, c, c, c, b}
# root has: {}
# tick: 5
# sub0 has: {c, c, c, c, c, c, c, c, c, b}
# root has: {}
# tick: 6
# sub0 has: {c, c, c, c, c, c, c, c, c, b}
# root has: {}
# tick: 7
# sub0 has: {c, c, c, c, c, c, c, c, c, b}
# root has: {}
# tick: 8
# sub0 has: {c, c, c, c, c, c, c, c, c, b}
# root has: {}
# tick: 9
# sub0 has: {c, c, c, c, c, c, c, c, c, b}
# root has: {}
# DONE.

# ====================================

# CURRENT STATE - sim2
# running membrane simulation
# see output: ./sims/
# tick: 0
# sub0 has: {a, b, b, c, c, c}
# firing rule: rule
# 	catalysts: {b}
# 	input: {c}
# 	output: {w}
#
# root has: {}
# tick: 1
# sub0 has: {a, b, b, c, c, w}
# firing rule: rule
# 	catalysts: {b}
# 	input: {c}
# 	output: {w}
#
# root has: {}
# tick: 2
# sub0 has: {a, b, b, c, w, w}
# firing rule: rule
# 	catalysts: {b}
# 	input: {c}
# 	output: {w}
#
# root has: {}
# tick: 3
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# tick: 4
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# tick: 5
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# tick: 6
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# tick: 7
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# tick: 8
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# tick: 9
# sub0 has: {a, b, b, w, w, w}
# root has: {}
# DONE.
