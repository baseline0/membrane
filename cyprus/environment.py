from random import shuffle
from typing import List

from cyprus.base import get_base, log_info
from cyprus.dissolve_particle import DissolveParticle
from cyprus.osmose_particle import OsmoseParticle
from cyprus.particle import Particle

base = get_base()


class Environment(object):
    """
    An environment - a container object for rules and particles
    """

    def __init__(self, name=None, parent=None, contents: List = [], membranes: List = [], rules: List = []) -> None:

        self.name = name
        self.parent = parent
        self.contents = contents
        self.membranes = membranes
        self.staging_area = []
        self.rules = rules
        self.ruleranks = {}

        self.setparents()
        self.setpriorities()

    def log_status(self, depth=0):
        indent = " " * (depth * 2)

        log_info(f"{indent} [name: {self.name}")
        log_info(f"{indent} symbols: {self.contents}")
        log_info(f"{indent} rules: {self.rules}")
        log_info(f"{indent} staging area: {self.staging_area}")

        log_info(f"{indent} Membranes:")
        for m in self.membranes:
            m.log_status(depth + 1)
        log_info(f"{indent}]")

    def tick(self):
        self.stage1()
        self.stage2()
        self.contents.extend(self.staging_area)
        self.staging_area = []

    def setpriorities(self):
        self.ruleranks = {}
        for rule in self.rules:
            r = self.ruleranks.get(rule.priority, [])
            r.append(rule)
            self.ruleranks[rule.priority] = r

    def setparents(self):
        for m in self.membranes:
            m.parent = self

    def dissolve(self):
        pass  # environments cannot dissolve

    def rule_is_applicable(self, rule):
        counts = set([(s.__str__(), rule.requirements.count(s)) for s in rule.requirements])
        s_counts = dict([(s.__str__(), self.contents.count(s)) for s in self.contents])
        for s, c in counts:
            if s_counts.get(s, None) == None or s_counts[s] < c:
                return False
        return True

    def apply_rule(self, rule):

        if self.rule_is_applicable(rule):
            base.state_rule_applied = True

            for s in rule.requirements:
                self.contents.remove(s)

        self.staging_area.extend(rule.output)

    ## apply all rules maximally, non-deterministically
    def stage1(self):
        for m in self.membranes:
            m.stage1()

        for p in sorted(self.ruleranks.keys(), reverse=True):
            rs = self.ruleranks[p]
            shuffle(rs)
            for rule in rs:
                while self.rule_is_applicable(rule):
                    self.apply_rule(rule)

    ## apply changes from stage 1, including dissolutions and osmosis
    def stage2(self):
        global base

        for m in self.membranes:
            m.stage2()

        self.contents.extend(self.staging_area)
        self.staging_area = []
        contentcopy = list(self.contents)

        for s in contentcopy:
            if isinstance(s, DissolveParticle):
                self.contents.remove(s)

                if s.target:
                    if not base.membrane_table.get(s.target, None):
                        msg = "ERROR: No containers defined with name '%s'" % s.target
                        raise Exception(msg)
                    base.membrane_table[s.target].dissolve()
                else:
                    self.dissolve()
                    break

            if isinstance(s, OsmoseParticle):
                self.contents.remove(s)
                if s.target:
                    if not base.membrane_table.get(s.target, None):
                        msg = "ERROR: No containers defined with name '%s'" % s.target
                        raise Exception(msg)
                    base.membrane_table[s.target].contents.append(Particle(s.payload))
                elif self.parent:
                    self.parent.contents.append(Particle(s.payload))
                else:  # environments cannot be osmosed through
                    self.contents.append(s)
