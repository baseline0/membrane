import unittest

from anytree import Node, PostOrderIter, RenderTree
from anytree.exporter import DotExporter
from anytree.walker import Walker

from malta.core.util import get_alphabet1
from malta.types.mmultiset import MMultiset
from malta.types.multiset_treenode import (
    MultisetTreeFactory,
    get_random_selection_from_alphabet,
    show_multiset_tree,
)


class TestMembraneTree(unittest.TestCase):
    def test_leaf_order(self):
        """
        known small 10 node polytree

        actually, easist to construct branches from root to each leaf
            0-1-3-8
            0-1-4
            0-1-5
            0-2-9
            0-6
            0-7

        then, randomly a branch, start at end, write multi-set up to common parent node, write that node.

        roots = (v for v, d in G.in_degree() if d == 0)
        leaves = [v for v, d in G.out_degree() if d == 0]
        all_paths = []
        for root in roots:
            paths = nx.all_simple_paths(G, root, leaves)
            all_paths.extend(paths)
        all_paths

        """
        leaf_order = []
        leaf_order.append([4, 5, 6, 7, 8, 9])
        leaf_order.append([2, 3])
        leaf_order.append([1])

        # dict of lists. 0 is root
        node_connections = {}
        node_connections["0"] = []
        node_connections["1"] = [0]
        node_connections["2"] = [0]
        node_connections["3"] = [1]
        node_connections["4"] = [1]
        node_connections["5"] = [1]
        node_connections["6"] = [0]
        node_connections["7"] = [0]
        node_connections["8"] = [3]
        node_connections["9"] = [2]

        # TODO
        # ms = MemStruct(node_connections, leaf_order)
        # print(ms)
        # ms.save_to_file('test_leaf_order.dot')

    def test_anytree(self):

        udo = MultisetTreeFactory().get_mt1()
        print(udo)

        for pre, fill, node in RenderTree(udo):
            print("%s%s" % (pre, node.name))

        DotExporter(udo).to_picture("./udo.png")

    def test_walk(self):

        udo = MultisetTreeFactory().get_mt1()

        w = Walker()
        w.walk(udo, udo)

        print([node.name for node in PostOrderIter(udo)])

    def test_multiset_in_tree(self):

        mt2 = MultisetTreeFactory().get_mt2()
        show_multiset_tree(mt2)
        # alphabet = get_alphabet1(10)

        items = {}
        items["a"] = 2
        items["b"] = 5
        items["w"] = 1

    def test_get_random_selection_from_alphabet(self):

        alphabet = get_alphabet1(15)
        x = get_random_selection_from_alphabet(5, alphabet)
        print(x)

    def test2(self):

        root = Node(name="root", contents=MMultiset())

        contents = MMultiset()
        contents.add("a", 1)
        contents.add("b", 4)
        # s0 = Node(name="sub0", parent=root, contents=contents)

        print([node.name for node in PostOrderIter(root)])

        for node in PostOrderIter(root):
            print(f"{node.name} has: {node.contents}")
