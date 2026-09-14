import json
import random
import string
from pathlib import Path
from string import ascii_lowercase
from typing import List

import networkx
import networkx as nx

# package-relative directory for bundled config/example data, so callers
# work the same regardless of the process's current working directory.
PACKAGE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_DIR / "config"


def prettyprint_json(data):
    json.dumps(data, indent=4, sort_keys=True)


class NameGenerator:
    # use as prefix for cluster items

    @staticmethod
    def get_rand_name(letters=string.ascii_lowercase, num_chars: int = 4, prefix: str = None) -> str:
        if prefix:
            name = prefix + "_"
        else:
            name = ""

        for i in range(num_chars):
            name += random.choice(letters)
        return name


def get_alphabet1(num: int) -> List[str]:
    """
    return a list of 1 character strings
    """

    if num > 26:
        num = 26
        print("limiting to ascii lowercase. write a new alphabet getter")

    return ascii_lowercase[0 : num - 1]


def hierarchy_pos(g: networkx.Graph, root=None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    """

    if not nx.is_tree(g):
        raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

    if root is None:
        root = random.choice(list(g.nodes))

    def _hierarchy_pos(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        """
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        """

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(g, root, width, vert_gap, vert_loc, xcenter)
