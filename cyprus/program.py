import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from funcparserlib.lexer import Token
from funcparserlib.parser import NoParseError

from cyprus.base import get_base, log_info
from cyprus.utils import get_pretty_tree

base = get_base()

from typing import List

from cyprus.clock import CyprusClock as Clock
from cyprus.dissolve_particle import DissolveParticle
from cyprus.environment import Environment
from cyprus.lexer import tokenize_file
from cyprus.membrane import Membrane
from cyprus.osmose_particle import OsmoseParticle
from cyprus.parser import MembraneGroup, StatementGroup, flatten, parse
from cyprus.particle import Particle
from cyprus.rule import Rule

# -----------------


class SimulationProgram(object):
    # TODO
    # enum kw_exists

    def __init__(self, tree):

        self.tree = tree
        envs = self.objectify()
        log_info(f"length = {len(envs)}")
        log_info(envs)
        self.clock = Clock(envs)

    def objectify(self) -> List[Environment]:
        out = []

        for e in self.tree.kids:
            env = self.build_environment(e)
            out.append(env)

        return out

    def build_container(self, e):

        name = None
        parent = None
        contents = []
        membranes = []
        rules = []
        stmts = []

        for x in e.kids:
            if isinstance(x, Token):
                name = x.value
            if isinstance(x, StatementGroup):
                stmts.append(self.execute_statement(x))

        stmts = flatten(stmts)
        for x in stmts:
            if isinstance(x, Membrane):
                membranes.append(x)

            if isinstance(x, Rule):
                rules.append(x)

            if isinstance(x, Particle):
                contents.append(x)

        return [name, parent, contents, membranes, rules]

    def build_environment(self, e):

        name, parent, contents, membranes, rules = self.build_container(e)
        env = Environment(name, parent, contents, membranes, rules)

        if name:
            # TODO refector to use: base.membrane_name_in_use
            if base.membrane_table.get(name, None):
                msg = f"ERROR: Multiple containers defined with name: {name}"
                raise Exception(msg)
            base.membrane_table[name] = env
        return env

    def build_membrane(self, e):

        name, parent, contents, membranes, rules = self.build_container(e)
        m = Membrane(name, parent, contents, membranes, rules)

        if name:
            if base.membrane_table.get(name, None):
                msg = f"ERROR: Multiple containers defined with name: {name}"
                raise Exception(msg)
            base.membrane_table[name] = m

        return m

    def execute_statement(self, stmt: StatementGroup):

        x = stmt.kids[0]

        if isinstance(x, MembraneGroup):
            return self.build_membrane(x)
        elif isinstance(x, Token):
            if x.type == "kw_exists":
                return self.build_particles(stmt)
            elif x.type == "kw_reaction":
                return self.buildrule(stmt)
            elif x.type == "kw_priority":
                self.set_priority(stmt)
                return None
            else:
                print(f"ERROR: {stmt}")

        else:
            print(f"ERROR: {stmt}")

    def build_particles(self, stmt: StatementGroup):

        particles = stmt.kids[2:]
        out = []

        for p in particles:
            out.append(Particle(p.value))
        return out

    def buildrule(self, stmt: StatementGroup):

        name = None
        req = []
        out = []
        pri = 1

        particulars = stmt.kids[1:]
        if particulars[0] is None:
            particulars = particulars[2:]
        else:
            name = particulars[1].value
            particulars = particulars[3:]

        prod = False
        dissolve = False
        osmose = False
        osmosename = False
        osmoselocation = False

        for x in particulars:
            if x:  ## error...
                if x.type == "op_production":
                    prod = True
                    continue
                elif x.type == "op_dissolve":
                    dissolve = True
                    continue
                elif x.type == "op_osmose":
                    osmose = True
                    continue
            if dissolve:
                if not x:
                    particle = DissolveParticle()
                else:
                    particle = DissolveParticle(x.value)
                dissolve = False
            elif osmose:
                if not osmosename:
                    osmosename = x.value
                    continue
                if osmosename:
                    if not x:
                        particle = OsmoseParticle(osmosename)
                        osmose, osmosename, osmoselocation = False, False, False
                    elif x.type == "op_osmose_location":
                        continue
                    else:
                        osmoselocation = x.value
                        particle = OsmoseParticle(osmosename, osmoselocation)
                        osmose, osmosename, osmoselocation = False, False, False
            else:
                particle = Particle(x.value)

            if prod:
                out.append(particle)
            else:
                req.append(particle)

        rule = Rule(name, req, out, pri)

        if name:
            if base.rule_table.get(name, None):
                msg = "ERROR: Multiple reactions defined with name '%s'" % name
                raise Exception(msg)
            base.rule_table[name] = rule
        return rule

    def set_priority(self, stmt):
        # global cyprus_rule_lookup_table

        greatern, lessern = stmt.kids[2].value, stmt.kids[4].value
        greater = base.rule_table.get(greatern, None)
        lesser = base.rule_table.get(lessern, None)

        if not greater:
            msg = f"ERROR: No reactions defined with name {greatern}"
            raise Exception(msg)

        if not lesser:
            msg = f"ERROR: No reactions defined with name {lessern}"
            raise Exception(msg)

        if greater.priority <= lesser.priority:
            greater.priority += 1

    def run(self, verbose=False):

        if verbose:
            self.clock.log_status()

        while base.state_rule_applied:
            base.state_rule_applied = False
            self.clock.tick()

            if verbose:
                self.clock.log_status()

        self.clock.log_final_contents()


def print_tree(fname: str) -> None:
    try:
        tokens = tokenize_file(fname)
        parsed = parse(tokens)
        tree = get_pretty_tree(parsed)
        print(tree)

    except NoParseError as e:
        print(f"Could not parse file: {e.msg}")


def parse_and_run_tree(fname: str, pverbose: bool) -> None:
    try:
        tokens = tokenize_file(fname)
        tree = parse(tokens)

    except NoParseError as e:
        print(f"Could not parse file: {e.args}")
        return

    try:
        from cyprus.utils import get_pretty_tree

        log_info(get_pretty_tree(tree))
        p = SimulationProgram(tree)
        p.run(verbose=pverbose)

    except Exception as e:
        print(f"error running program: {e.args}")
