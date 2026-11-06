import networkx as nx


def demo():
    from networkx.generators.random_graphs import random_lobster

    n = 10
    p1 = 0.5
    p2 = 0.7
    g = random_lobster(n, p1, p2, seed=None)

    adjacency_matrix = nx.adjacency_matrix(g)
    print(adjacency_matrix)

    # get a random graph
    # TODO
