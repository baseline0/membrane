import os
import sys
import unittest

from cyprus.program import tokenize_file

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)


class LexerTest(unittest.TestCase):
    def test_unicode(self):
        ts = tokenize_file("./examples/example1.cyp")
        print(ts[0])
        self.assertEqual(str(ts[0]), "3,1-3,1: env_open '['")

        correct = """
    3,1-3,1: env_open '['
    3,2-3,4: name 'env'
    4,3-4,3: membrane_open '('
    4,4-4,4: number '1'
    5,5-5,5: membrane_open '('
    5,6-5,6: number '2'
    6,7-6,7: membrane_open '('
    6,8-6,8: number '3'
    7,9-7,14: kw_exists 'exists'
    7,15-7,15: op_tilde '~'
    7,19-7,19: name 'a'
    7,21-7,21: name 'c'
    8,9-8,16: kw_reaction 'reaction'
    8,17-8,17: op_tilde '~'
    8,21-8,21: name 'a'
    8,23-8,24: op_production '::'
    8,26-8,26: name 'a'
    8,28-8,28: name 'b'
    9,9-9,16: kw_reaction 'reaction'
    9,17-9,17: op_tilde '~'
    9,21-9,21: name 'a'
    9,23-9,24: op_production '::'
    9,26-9,26: name 'b'
    9,28-9,28: op_dissolve '$'
    10,9-10,16: kw_reaction 'reaction'
    10,17-10,17: op_tilde '~'
    10,21-10,21: name 'c'
    10,23-10,24: op_production '::'
    10,26-10,26: name 'c'
    10,28-10,28: name 'c'
    11,7-11,7: membrane_close ')'
    13,7-13,14: kw_reaction 'reaction'
    13,15-13,15: op_tilde '~'
    13,25-13,25: name 'b'
    13,27-13,28: op_production '::'
    13,30-13,30: name 'd'
    14,7-14,14: kw_reaction 'reaction'
    14,15-14,15: op_tilde '~'
    14,25-14,25: name 'd'
    14,27-14,28: op_production '::'
    14,30-14,30: name 'd'
    14,32-14,32: name 'e'
    15,7-15,14: kw_reaction 'reaction'
    15,16-15,17: kw_as 'as'
    15,19-15,20: name 'c1'
    15,21-15,21: op_tilde '~'
    15,23-15,23: name 'c'
    15,25-15,25: name 'c'
    15,27-15,28: op_production '::'
    15,30-15,30: name 'c'
    16,7-16,14: kw_reaction 'reaction'
    16,16-16,17: kw_as 'as'
    16,19-16,20: name 'c2'
    16,21-16,21: op_tilde '~'
    16,25-16,25: name 'c'
    16,27-16,28: op_production '::'
    16,30-16,30: op_dissolve '$'
    17,7-17,14: kw_priority 'priority'
    17,15-17,15: op_tilde '~'
    17,24-17,25: name 'c1'
    17,27-17,28: op_priority_maximal '>>'
    17,30-17,31: name 'c2'
    18,5-18,5: membrane_close ')'
    20,5-20,12: kw_reaction 'reaction'
    20,13-20,13: op_tilde '~'
    20,15-20,15: name 'e'
    20,17-20,18: op_production '::'
    20,20-20,20: op_osmose '!'
    20,21-20,21: name 'e'
    21,3-21,3: membrane_close ')'
    22,1-22,1: env_close ']'
    """

        # self.assertEqual(t, correct)
