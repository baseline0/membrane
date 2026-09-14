import json
from typing import List

from malta.io.dot_colour import get_rand_colour


class MembraneItem:
    """
    an object that lives within a membrane,
    interacts with other objects with respect to defined rules

    The complete list of membrane items is useful for a legend for a diagram.
    The environment contains this description list (to avoid duplicating in every membrane)
    The membrane itself, in the contents attr, contains the multiset of identifiers (membrane_item.name)
    The rules operate on  membrane_item.name.
    Thus, the apply_rule(r, m) method that is called by Environment has the same types for set operations on catalyst, rule_inputs and rule_outputs.
    """

    __slots__ = ["name", "symbol", "descr", "colour"]

    def __init__(self, name: str, descr: str = None, colour: str = None):
        #
        if isinstance(name, str):
            self.name = name
        elif isinstance(name, dict):
            # via json loads. find better way
            self.set_from_dict(name)
        else:
            raise ValueError

        # short name for visualizations
        # truncate name
        if len(name) > 5:
            self.symbol = name[0:4]
        else:
            self.symbol = name

        # more details as needed
        self.descr = descr

        # the dot colour string.
        if colour is None:
            c = get_rand_colour()
            if c is list:
                # list of one?!
                self.colour = c[0]
            else:
                self.colour = c
        else:
            self.colour = colour

    def set_from_dict(self, d: dict):
        if "name" in d.keys():
            self.name = d["name"]
        if "descr" in d.keys():
            self.descr = d["descr"]
        if "symbol" in d.keys():
            self.symbol = d["symbol"]
        if "colour" in d.keys():
            self.colour = d["colour"]

    def __eq__(self, other):

        if isinstance(other, MembraneItem):
            return self.name == other.name
        return False

    def json_serialize(self) -> dict:
        d = {}
        d["name"] = self.name
        d["symbol"] = self.symbol
        d["descr"] = self.descr
        d["colour"] = self.colour
        return d


def membrane_item_deserialize(d: dict) -> MembraneItem:
    mi = MembraneItem("temp")

    if "name" in d.keys():
        mi.name = d["name"]
    if "descr" in d.keys():
        mi.descr = d["descr"]
    if "symbol" in d.keys():
        mi.symbol = d["symbol"]
    if "colour" in d.keys():
        mi.colour = d["colour"]

    return mi


def load_membrane_items_from_file(fname: str) -> (List[MembraneItem], List[str]):
    """
    file is in json format.
        key must be from alphabet that is used in rules
        value must be a positive integer and is multiplicity of the key in the membrane
    """

    alphabet = []

    # details on the membranes items for summary report
    with open(fname) as f:
        out = json.load(f)

    all_items = []
    for k, v in out.items():
        all_items.append(MembraneItem(k, descr=v))
        alphabet.append(k)

    return all_items, alphabet
