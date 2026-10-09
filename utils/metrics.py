"""
Utility functions for measuring network and simulation outcomes.
"""

import numpy as np
import networkx as nx

from src.states import INFECTED, ISOLATED


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


def post_containment_connectivity(G):
    """
    Measure connected availability after removing locally isolated devices.

    Patched and infected devices remain in the active graph: patching
    protects devices without taking them offline, while infected devices
    remain connected in the SI model.
    """
    active_nodes = [
        node
        for node in G.nodes()
        if G.nodes[node].get("state") != ISOLATED
    ]
    active_graph = G.subgraph(active_nodes)
    component_sizes = [
        len(component)
        for component in nx.connected_components(active_graph)
    ]
    largest_component_size = max(component_sizes, default=0)
    active_count = len(active_nodes)
    total_count = G.number_of_nodes()

    return {
        "active_devices": active_count,
        "isolated_devices": total_count - active_count,
        "component_count": len(component_sizes),
        "largest_component_size": largest_component_size,
        "largest_component_fraction_active": (
            largest_component_size / active_count if active_count else 0.0
        ),
        "largest_component_fraction_total": (
            largest_component_size / total_count if total_count else 0.0
        ),
    }