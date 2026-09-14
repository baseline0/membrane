import json
import sys
from typing import List, TextIO

from malta.io.dot_colour import get_rand_colour
from malta.core.util import NameGenerator


class Delimited:
    def start(self, name: str = "d") -> str:
        pass

    @classmethod
    def end(cls) -> str:
        pass


class ContentItem:
    # these are the items that live in the membranes

    # in dot/graphviz format,
    #   abc [color = red]

    def __init__(self, name: str = None, colour: str = None) -> None:
        # colour is string but we expect it to be :
        #   str(colour:DotColour.name)

        if name is None:
            self.name = NameGenerator().get_rand_name()
        else:
            self.name = name.replace(" ", "")

        if colour is None:
            # self.colour = str(get_rand_colours(1)[0].name)
            self.colour = get_rand_colour()
        else:
            self.colour = colour

    def __repr__(self) -> str:

        s = "[" + self.name + " = " + self.colour + "]"
        return s


class Base(Delimited):
    def write_contents(self) -> str:
        pass

    def get_label(self) -> str:
        pass


def write_cluster(fp: TextIO, c: Base):
    try:
        fp.writelines(c.start())

        fp.writelines(f"{x} \n" for x in c.contents)

        for subcluster in c.clusters:
            write_cluster(fp, subcluster)

        fp.write(c.get_label())
        fp.writelines(c.end())

    except IOError:
        sys.exit()


class Subgraph(Delimited):
    START = "{"
    END = "}"

    def __init__(self, label=None) -> None:
        if label is None:
            self.label = NameGenerator.get_rand_name()
        else:
            self.label = label

    def start(self) -> str:
        return f"subgraph {self.label} " + Subgraph.START + "\n"

    @classmethod
    def end(cls) -> str:
        return Subgraph.END + "\n"


class Cluster(Delimited):
    START = "{"
    END = "}"

    def __init__(self, name=None, label=None) -> None:

        if name is None:
            self.name = NameGenerator().get_rand_name()
        else:
            # whitespace in names confounds dot
            self.name = name.replace(" ", "")

        # the cluster label in diagram
        if label is None:
            self.label = name
        else:
            self.label = label

            # nesting
        self.clusters = []

        # the objects in the membrane
        self.contents = []

    def add_cluster(self, c):
        self.clusters.append(c)

    def start(self) -> str:
        return f"subgraph cluster_{self.name} {Cluster.START} " + "\n"

    def get_label(self) -> str:
        if self.label is None:
            return ""
        else:
            s = f'label = "{self.label}"'
            return s

    @classmethod
    def end(cls) -> str:
        return Cluster.END + "\n"


class Digraph(Delimited):
    START = "{"
    END = "}"

    def __init__(self, label: str = "d") -> None:
        self.label = label
        self.clusters = []

    @classmethod
    def start(cls, name: str = "d") -> str:
        return f"digraph {name} " + Digraph.START + "\n"

    @classmethod
    def end(cls) -> str:
        return Digraph.END + "\n"

    def add_cluster(self, c: Cluster):
        self.clusters.append(c)


class DigraphGenerator:
    def __init__(self):

        self.data = None
        self.digraph = None
        self.clusters = []
        self._tick_index = 0
        self._reset()

        # self.simulation_prefix
        self.output_dir = "./out/"
        self.png_prefix = "tick_"

    def _get_tick_index(self) -> int:
        return self._tick_index

    def _incr_tick_index(self) -> None:
        self._tick_index += 1

    def _reset(self) -> None:
        self.digraph = Digraph()
        # self.clusters = []
        self._tick_index = 0

    def run(self):
        # graph is loaded from file.
        # internals are configured
        # advance state until max steps or halting condition.
        pass

    def save_json(self, fname: str) -> None:
        try:
            json.load(fname)
        except IOError:
            print(f"unable to load digraph from: {fname}")

        self._reset()

    def load_json(self, fname: str) -> None:

        self._reset()

        try:
            data = json.load(fname)
            self.digraph = data
        except IOError:
            print(f"unable to load digraph from: {fname}")

    # def save_png(self, fname: str) -> None:
    #     idx = self._get_next_tick_index()
    #     pass

    def save_dot(self, fname: str) -> None:
        # use of writelines helps to avoid appending \n
        # save in dot format

        print(f"writing digraph to: {fname}")

        with open(fname, "w") as fp:
            fp.writelines(self.digraph.start())

            for c in self.digraph.clusters:
                write_cluster(fp, c)

            fp.writelines(self.digraph.end())
            # fp.close()


class ClusterFactory:
    """
    for writing out a subgraph cluster_NAME in dot format
    """

    @classmethod
    def get_cluster_1(cls) -> Cluster:
        # simple. small. nested one deep

        c = Cluster(name="top")
        c.contents = ["a", "b", "c"]

        d = Cluster(name="nested")
        d.contents = ["d", "e", "f"]

        c.add_cluster(d)

        return c

    @classmethod
    def get_cluster_2(cls) -> List[Cluster]:
        c = Cluster(name="top")
        c.contents = ["a", "b", "c"]

        peer = Cluster(name="peer")
        peer.contents = ["a1", "b1", "c1"]

        d = Cluster(name="nested")
        d.contents = ["d", "e", "f"]

        e = Cluster(name="nested_2")
        e.contents = ["g", "h", "i"]

        d.add_cluster(e)
        c.add_cluster(d)

        return [c, peer]
