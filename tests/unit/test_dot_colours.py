import unittest

from malta.io.dot_colour import get_rand_colours


class TestDotColour(unittest.TestCase):
    def test_1(self):
        palette = get_rand_colours()
        print(palette)
