# monkey patch to fix:
#   AttributeError: 'Multiset' object has no attribute 'json_serialize'

from multiset import Multiset


class MMultiset(Multiset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def json_serialize(self) -> dict:
        d = {}
        s = self.__str__()
        s = s.replace("{", "")
        s = s.replace("}", "")
        s = s.replace("'", "")
        s = s.replace(":", "")
        s = s.replace(",", "")

        # may need to split into tuples here?
        tokens = s.split(" ")

        for t in tokens:
            if t in d.keys():
                d[t] += 1
            else:
                d[t] = 1
        return d

    def as_simple_string(self) -> str:
        s = self.__str__()
        s = s.replace("{", "")
        s = s.replace("}", "")
        s = s.replace("'", "")
        s = s.replace(":", "")
        s = s.replace(",", "")

        return s

    def as_dot(self) -> str:
        """
        helper for writing digraph content
        but for colour, access through environment
        """
        s = self.as_simple_string()

        formatted = ""

        tokens = s.split(" ")

        for t in tokens:
            formatted += f"{t}\n"

        return formatted


def json_serialize(m: Multiset) -> dict:
    d = {}
    s = m.__str__()
    s = s.replace("{", "")
    s = s.replace("}", "")
    s = s.replace("'", "")
    s = s.replace(":", "")
    s = s.replace(",", "")

    # may need to split into tuples here?
    tokens = s.split(" ")

    for t in tokens:
        if t in d.keys():
            d[t] += 1
        else:
            d[t] = 1
    return d


def multiset_to_dict(m: Multiset) -> dict:
    # multiset does not have __dict__
    # but we want to use json load/dump
    # works for m.__str__ = {'a'}

    d = {}

    for k, v in m.items():
        d[k] = v
    return d


def make_mmultiset(d: dict) -> MMultiset:
    """
    we do intend that multiplicity is > 0
    but not testing for it.
    """

    mm = MMultiset()

    for k, v in d.items():
        mm.add(k, v)

    return mm
