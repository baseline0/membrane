# a tool to create membranes for cyprus

import json
from io import FileIO
from string import ascii_lowercase
from typing import List, TextIO

# concept
# have the generator write json files.
# the json files can convert to dot.
# the json files are written into cyp format for grammar and simulation.


## grammar
#
# program        := {env}
# env            := "[", body, "]"
# membrane       := "(", body, ")"
# body           := <name>, {statement}
# statement      := membrane | expr
# expr           := exists | reaction | priority
# exists         := "exists", "~", name, {name}
# reaction       := "reaction", <"as", name>, "~", name, {name}, "::",
#                    {symbol}
# priority       := "priority", "~", name, ">>", name
# name           := number | atom
# atom           := [A-Za-z], {[A-Za-z0-9]}
# number         := [0-9], {[0-9]} | {[0-9]}, ".", [0-9], {[0-9]}
# symbol         := atom | "!", name, <"!!", name> | "$", [name]

ENV_START = "[\n"
ENV_END = "]\n"

MEM_START = "(\n"
MEM_END = ")\n"


class AtomConcept:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


class AtomQuantity:
    def __init__(self, a: AtomConcept) -> None:
        self.atom = a
        self.count = 0


class Contents:
    # things that are in a environment or membrane at the start.

    def __init__(self) -> None:

        # a dict of tuples -the atom name and its quantity
        self.inventory = {}

    def add(self, atom: AtomConcept, count: int):

        if count < 0:
            raise ValueError

        if atom.name not in self.inventory:
            self.inventory[atom.name] = count
        else:
            self.inventory[atom.name] = self.inventory[atom.name] + count


class MembraneConcept:
    def __init__(self):
        self.name = 1
        self.contents = []
        self.rules = []
        self.membranes = []

    def __repr__(self) -> str:
        pass

    def to_file(self, fp: FileIO):

        if fp is None:
            raise ValueError

        fp.write(MEM_START)

        for c in self.contents:
            c.to_file(fp)

        for m in self.membranes:
            m.to_file(fp)

        fp.write(MEM_END)

    def to_dict(self) -> dict:
        d = {}

        d["name"] = self.name
        d["exists"] = self.contents
        d["rules"] = self.rules
        d["membranes"] = []

        for m in self.membranes:
            d["membranes"].append(m.to_dict())

        return d


class RuleConcept:
    # for reactions

    def __init__(self) -> None:
        self.catalyst = []
        self.input = []
        self.output = []

    def __repr__(self) -> str:
        pass


class EnvironmentConcept:
    def __init__(self) -> None:
        self.membranes = []

        # a list of atoms
        self.contents = []

        self.name = "env1"

    def __repr__(self) -> str:
        pass

    def add_membrane(self, m: MembraneConcept) -> None:
        self.membranes.append(m)

    def add_contents(self, atoms: List[AtomConcept]) -> None:
        self.contents = atoms

    def to_json(self) -> dict:

        d = {}

        d[self.name] = []

        for m in self.membranes:
            d[self.name].append(m.name)

        return json.dumps(d)

    def to_file(self, fp: TextIO) -> None:

        if fp is None:
            raise ValueError

        fp.write(ENV_START)

        for m in self.membranes:
            m.to_file(fp)

        for c in self.contents:
            c.to_file(fp)

        fp.write(ENV_END)


class Generator:
    def __init__(self) -> None:
        self.OUT_DIR = "./sims/"

        self.envs = []

        self.n_atoms = 0
        # self.n_membranes=0

    def set_n_atoms(self, num: int = 10):

        if num < 0:
            raise ValueError

        if num > 26:
            print("max 26 atoms at this time")
            num = 26

        self.n_atoms = num
        self.atoms = []

        names = ascii_lowercase[:num]

        for n in names:
            self.atoms.append(AtomConcept(n))

    def generate_2_atom_rule(self):

        r = RuleConcept()

        return r

    def run(self, fname_prefix: str = "generated"):

        # TODO - adopt json

        # generate:
        #   a random number of atoms
        #   a random number of membranes
        #   a random number of rules that convert atoms into other atoms with a catalyst (unchanging atom)
        #   a random number of rules that dissolve a membrane
        #   a random number of rules that osmose (simplified: just move across membrane)
        #   TODO a random number of rules that osmose (actual gradient must exist for atom to move across membrane)

        self.save(fname_prefix=fname_prefix)

    def save(self, fname_prefix: str):

        # write to file

        with open(self.OUT_DIR + fname_prefix + ".cyp", "w") as fp:
            fp.write("// this is a generated file\n")

            for e in self.envs:
                e.to_file(fp)

    def to_dot(self, fname_prefix: str):
        # write in dot format

        with open(fname_prefix + ".png", "w") as fp:
            fp.write("digraph d {")

            fp.write("}")


def convert_dot_to_png(fname: str):
    import os

    os.system("dot -Tpng generated.dot -o generated.png")


# ---------------

if __name__ == "__main__":
    g = Generator()

    # configure an environment

    e = EnvironmentConcept()

    m = MembraneConcept()

    e.membranes.append(m)

    g.envs.append(e)

    g.run(fname_prefix="test_generated")
