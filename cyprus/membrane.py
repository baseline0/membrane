from typing import List

from cyprus.base import get_base, log_info
from cyprus.environment import Environment

base = get_base()


class Membrane(Environment):
    def __init__(self, name=None, parent=None, contents: List = ..., membranes: List = ..., rules: List = ...) -> None:
        super().__init__(name, parent, contents, membranes, rules)

    def dissolve(self):
        self.parent.contents.extend(self.contents)
        self.parent.membranes.remove(self)
        self.parent.membranes.extend(self.membranes)
        self.contents = []
        self.staging_area = []
        self.rules = []

        if self.name:
            del base.membrane_table[self.name]

    def log_status(self, depth=0):
        indent = " " * (depth * 4)

        log_info(f"{indent} (name: {self.name}")
        log_info(f"{indent} symbols: {self.contents}")
        log_info(f"{indent} rules: {self.rules}")
        log_info(f"{indent} staging area: {self.staging_area}")

        log_info(f"{indent} Membranes:")
        for m in self.membranes:
            m.log_status(depth + 1)
        log_info(f"{indent}")
