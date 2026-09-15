from funcparserlib.util import pretty_tree

from cyprus.parser import EnvironmentGroup, Grouping, MembraneGroup, ProgramGroup, StatementGroup


# pretty print a parse tree
def get_pretty_tree(tree):

    def kids(x):
        if isinstance(x, Grouping):
            return x.kids
        else:
            return []

    def show(x):
        # print("show(%r)" % x
        if isinstance(x, ProgramGroup):
            return "{Program}"
        elif isinstance(x, EnvironmentGroup):
            return "{Environment}"
        elif isinstance(x, MembraneGroup):
            return "{Membrane}"
        elif isinstance(x, StatementGroup):
            return "{Statement}"
        else:
            return repr(x)

    return pretty_tree(tree, kids, show)
