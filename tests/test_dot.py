import os
import sys
import unittest

from malta.dot import ContentItem
from malta.dot_colour import DotColour
from malta.factory import ContentItemFactory
from malta.util import NameGenerator

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)


class TestDigraphGenerator(unittest.TestCase):
    def test_1(self):

        color = str(DotColour.aliceblue.name)

        c = ContentItem(name="cod", colour=color)
        print(c)

    def test_2(self):

        factory = ContentItemFactory()

        items = factory.get_items(4)

        for i in items:
            print(i)

    def test_3(self):

        ng = NameGenerator()

        names = []
        for i in range(5):
            names.append(ng.get_rand_name())

        print(names)

    # def test_demo1(self):
    #
    #     c = ClusterFactory.get_cluster_1()
    #
    #     dg = DigraphGenerator()
    #     dg.digraph.add_cluster(c)
    #
    #     dg.save_dot(fname='./out/graph1.dot')

    # def test_demo2(self):
    #
    #     [c, peer] = ClusterFactory.get_cluster_2()
    #
    #     dg = DigraphGenerator()
    #     dg.digraph.add_cluster(c)
    #     dg.digraph.add_cluster(peer)
    #
    #     dg.save_dot(fname='./tests/out/graph2.dot')

    # def test_membrane_to_dot(self):
    #
    #     fname = './out/test_membrane.dot'
    #
    #     mi1 = MembraneItem(name='a', descr='apple')
    #     mi2 = MembraneItem(name='b', descr='bread')
    #     contents = get_multiset_of_item_names_from_membrane_items([mi1, mi2])
    #     m = Membrane('membrane', descr='descr', contents=contents)
    #
    #     s = m.as_dot()
    #     print(s)
    #
    #     self.assertTrue('subgraph ' in s)
    #     self.assertTrue('cluster_membrane ' in s)
    #     self.assertTrue('a ' in s)
    #     self.assertTrue('b ' in s)
    #
    #     with open(fname, 'w') as f:
    #         f.write('digraph d {')
    #         f.write(s)
    #         f.write('}')
