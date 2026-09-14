import json
import unittest

from cyprus.generator import MembraneConcept


class TestMembraneConcept(unittest.TestCase):
    def test_1(self):
        m = MembraneConcept()
        m.name = "m1"
        m.rules = "rule1"
        m.contents = ["a", "b", "x"]
        m.membranes = []

        print(m.to_dict())
        print(json.dumps(m.to_dict()))
