import os
import sys
import unittest

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from cyprus.particle import Particle


class TestParticle(unittest.TestCase):
    def test_same(self):

        # name provided
        p = Particle(name="oizo")
        q = Particle(name="oizo")
        self.assertEqual(p, q)

        # name and charge provided
        p = Particle(name="oizo", charge="positive")
        q = Particle(name="oizo", charge="positive")
        self.assertEqual(p, q)

    def test_different(self):

        # name provided
        p = Particle(name="oizo")
        q = Particle(name="flatbeat")
        self.assertNotEqual(p, q)

    def test_exceptions(self):
        # empty
        # p = Particle()
        pass
