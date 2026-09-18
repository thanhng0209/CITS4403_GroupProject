"""
Utility functions for measuring network and simulation outcomes.
"""

import numpy as np

from src.states import INFECTED


def count_infected(G):
    """
    Count the number of infected nodes in the network.

    Parameters
    ----------
    G : networkx.Graph
        Network containing node states.

    Returns
    -------
    int
        Number of nodes currently in the infected state.
    """
    return sum(
        G.nodes[node]["state"] == INFECTED
        for node in G.nodes()
    )


def count_state(G, state):
    """
    Count the number of nodes currently in a specified state.

    Parameters
    ----------
    G : networkx.Graph
        Network containing node states.
    state : str
        Node state to count.

    Returns
    -------
    int
        Number of nodes matching the requested state.
    """
    return sum(
        G.nodes[node]["state"] == state
        for node in G.nodes()
    )


def average_degree(G):
    """
    Calculate the mean node degree of a network.

    Parameters
    ----------
    G : networkx.Graph
        Network whose average degree is calculated.

    Returns
    -------
    float
        Mean degree across all nodes.
    """
    return np.mean(
        [degree for _, degree in G.degree()]
    )