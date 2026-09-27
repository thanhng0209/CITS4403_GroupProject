"""
Network-generation functions for the IoT malware propagation model.

The project uses three network topologies:

- Erdős–Rényi random network
- Watts–Strogatz small-world network
- Barabási–Albert scale-free network

Network parameters are supplied by the experiment notebook rather than
being fixed in this module.
"""

import networkx as nx


def create_random_network(n, p, seed=None):
    """
    Create an Erdős–Rényi random network.

    Each possible pair of nodes is connected independently with
    probability p.

    Parameters
    ----------
    n : int
        Number of nodes in the network.
    p : float
        Probability that an edge exists between a pair of nodes.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    networkx.Graph
        Generated random network.
    """
    return nx.erdos_renyi_graph(
        n=n,
        p=p,
        seed=seed
    )


def create_small_world_network(n, k, rewiring_prob, seed=None):
    """
    Create a Watts–Strogatz small-world network.

    Each node is initially connected to k nearby neighbours, after which
    edges are rewired with probability rewiring_prob. This produces a
    network with local clustering and occasional long-range connections.

    Parameters
    ----------
    n : int
        Number of nodes in the network.
    k : int
        Number of nearest neighbours connected to each node.
    rewiring_prob : float
        Probability of rewiring each edge.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    networkx.Graph
        Generated small-world network.
    """
    return nx.watts_strogatz_graph(
        n=n,
        k=k,
        p=rewiring_prob,
        seed=seed
    )


def create_scale_free_network(n, m, seed=None):
    """
    Create a Barabási–Albert scale-free network.

    New nodes are added using preferential attachment, making highly
    connected nodes more likely to receive additional links.

    Parameters
    ----------
    n : int
        Number of nodes in the network.
    m : int
        Number of edges created by each newly added node.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    networkx.Graph
        Generated scale-free network.
    """
    return nx.barabasi_albert_graph(
        n=n,
        m=m,
        seed=seed
    )