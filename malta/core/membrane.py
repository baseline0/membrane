from typing import List

from malta.types.mmultiset import MMultiset


class Membrane:
    """
    contents is a list of strings that are the names of the membrane items
    contents needs to be a multiset so it is compatible with set operations for rules.
    """

    # https://pythonhosted.org/multiset/

    __slots__ = ["name", "descr", "contents", "membranes"]

    def __init__(self, name: str, descr: str, contents=List[str]):
        # =List[MembraneItem]):
        if isinstance(name, str):
            self.name = name
        else:
            raise ValueError

        self.descr = descr

        # We expect a Multiset where the items in the multiset are the names of the corresponding
        # MembraneItems
        if not isinstance(contents, MMultiset):
            raise ValueError
        else:
            self.contents = contents

        # TODO - add in submembranes
        self.membranes = None

    def json_serialize(self) -> dict:
        d = {}
        d["name"] = self.name
        d["descr"] = self.descr
        d["contents"] = self.contents
        return d

    def as_dot(self) -> str:
        """
        return a subgraph cluster_NAME which can be used as part of a
        dot digraph file for visualization
        """

        s = f"subgraph cluster_{self.name} {{ \n"

        # TODO - add in indent

        # TODO - add in colour
        # TODO - how to show multiplicity
        # option1: duplicate the visual object
        # option2: use a label on the object with quantity
        for c in self.contents:
            s += f"{c} \n"

        s += "}"

        return s


def deserialize(d: dict) -> Membrane:
    m = Membrane()

    if "name" in d.keys():
        m.name = d["name"]

    if "descr" in d.keys():
        m.descr = d["descr"]

    if "contents" in d.keys():
        m.contents = d["contents"]

    return m
