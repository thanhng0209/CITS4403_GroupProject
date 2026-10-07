"""
Containment strategies for the IoT malware propagation model.

This module implements three containment approaches:

1. Random centralized patching
2. Degree-targeted centralized patching
3. Decentralized local isolation

The patching strategies are preventive: nodes are patched before the
initial infection is introduced.

Local isolation is reactive: susceptible nodes that are exposed to
infected neighbours may isolate during the simulation.

Patching removes devices from the susceptible population while keeping
them available as protected devices. Isolation instead removes devices
from active communication, so it can reduce infection at the cost of
network availability.
"""

import numpy as np
import networkx as nx

from src.states import (
    SUSCEPTIBLE,
    INFECTED,
    PATCHED,
    ISOLATED
)

from src.propagation import (
    initialise_infection,
    infection_step
)

from utils.metrics import count_infected


def random_patching(G, patch_budget, rng):
    """
    Patch a random subset of susceptible nodes.

    The number of patched nodes is determined by patch_budget as a
    fraction of the total network size. Only currently susceptible nodes
    are eligible for patching.

    Parameters
    ----------
    G : networkx.Graph
        Network containing node states.
    patch_budget : float
        Fraction of the total network that can be patched.
    rng : numpy.random.Generator
        Random-number generator used to select patched nodes.

    Returns
    -------
    list
        Nodes selected for patching.
    """
    susceptible_nodes = [
        node for node in G.nodes()
        if G.nodes[node]["state"] == SUSCEPTIBLE
    ]

    n_patch = int(G.number_of_nodes() * patch_budget)
    n_patch = min(n_patch, len(susceptible_nodes))

    if n_patch == 0:
        return []

    selected_nodes = rng.choice(
        susceptible_nodes,
        size=n_patch,
        replace=False
    )

    for node in selected_nodes:
        G.nodes[node]["state"] = PATCHED

    return list(selected_nodes)


def targeted_patching(G, patch_budget, rng):
    """
    Patch the highest-degree susceptible nodes first.

    Nodes are ranked by degree in descending order, and the available
    patch budget is allocated to the most highly connected devices.

    This represents a centralized strategy with knowledge of network
    connectivity, in contrast to random patch allocation.

    Parameters
    ----------
    G : networkx.Graph
        Network containing node states.
    patch_budget : float
        Fraction of the total network that can be patched.
    rng : numpy.random.Generator
        Included to keep a common interface with random_patching().
        The current targeted strategy itself is deterministic.

    Returns
    -------
    list
        Nodes selected for patching.
    """
    susceptible_nodes = [
        node for node in G.nodes()
        if G.nodes[node]["state"] == SUSCEPTIBLE
    ]

    n_patch = int(G.number_of_nodes() * patch_budget)
    n_patch = min(n_patch, len(susceptible_nodes))

    if n_patch == 0:
        return []

    ranked_nodes = sorted(
        susceptible_nodes,
        key=lambda node: G.degree(node),
        reverse=True
    )

    selected_nodes = ranked_nodes[:n_patch]

    for node in selected_nodes:
        G.nodes[node]["state"] = PATCHED

    return selected_nodes


def initialise_with_patching(
    G,
    patch_strategy,
    patch_budget,
    seed=None
):
    """
    Initialise a simulation with preventive patching.

    All nodes are first reset to susceptible. The selected patching
    strategy is then applied before one remaining susceptible node is
    chosen as the initial infected device.

    Parameters
    ----------
    G : networkx.Graph
        Network on which the simulation is run.
    patch_strategy : callable
        Patching function such as random_patching or targeted_patching.
    patch_budget : float
        Fraction of the total network that can be patched.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    initial_node
        Node selected as the initial infected device.
    patched_nodes : list
        Nodes patched before malware propagation begins.
    """
    rng = np.random.default_rng(seed)

    # Reset all devices before applying the preventive strategy.
    nx.set_node_attributes(
        G,
        SUSCEPTIBLE,
        "state"
    )

    # Preventive patching occurs before the malware is introduced.
    patched_nodes = patch_strategy(
        G,
        patch_budget,
        rng
    )

    susceptible_nodes = [
        node for node in G.nodes()
        if G.nodes[node]["state"] == SUSCEPTIBLE
    ]

    initial_node = rng.choice(susceptible_nodes)
    G.nodes[initial_node]["state"] = INFECTED

    return initial_node, patched_nodes


def run_patching_simulation(
    G,
    beta,
    steps,
    patch_strategy,
    patch_budget,
    seed=None
):
    """
    Run malware propagation after preventive patching.

    The selected patching strategy is applied once before infection
    begins. Malware then spreads through the remaining susceptible nodes
    using the baseline infection rule.

    Parameters
    ----------
    G : networkx.Graph
        Network on which the simulation is run.
    beta : float
        Infection probability for each infected-susceptible edge.
    steps : int
        Number of simulation steps.
    patch_strategy : callable
        Patching function applied before propagation.
    patch_budget : float
        Fraction of the total network that can be patched.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    list
        Number of infected nodes at the initial state and after each step.
    """
    rng = np.random.default_rng(seed)

    initialise_with_patching(
        G,
        patch_strategy,
        patch_budget,
        seed
    )

    infected_history = [
        count_infected(G)
    ]

    for _ in range(steps):
        infection_step(
            G,
            beta,
            rng
        )

        infected_history.append(
            count_infected(G)
        )

    return infected_history


def infection_isolation_step(
    G,
    beta,
    isolation_prob,
    rng
):
    """
    Perform one malware propagation step with local isolation.

    Each susceptible node exposed to at least one infected neighbour
    first attempts to isolate with probability isolation_prob.

    If isolation does not occur, each infected neighbour independently
    attempts to transmit malware with probability beta.

    All infection and isolation decisions are based on node states at the
    start of the current step. State changes are applied only after all
    nodes have been evaluated, preserving synchronous updating.

    Parameters
    ----------
    G : networkx.Graph
        Network containing node states.
    beta : float
        Infection probability for each infected-susceptible edge.
    isolation_prob : float
        Probability that an exposed susceptible node isolates before
        transmission occurs.
    rng : numpy.random.Generator
        Random-number generator used for isolation and infection events.

    Returns
    -------
    nodes_to_infect : list
        Nodes infected during the current step.
    nodes_to_isolate : list
        Nodes isolated during the current step.
    """
    nodes_to_infect = []
    nodes_to_isolate = []

    for node in G.nodes():

        if G.nodes[node]["state"] != SUSCEPTIBLE:
            continue

        infected_neighbours = [
            neighbour
            for neighbour in G.neighbors(node)
            if G.nodes[neighbour]["state"] == INFECTED
        ]

        if not infected_neighbours:
            continue

        # Local response is attempted before malware transmission.
        isolation_multiplier = G.nodes[node].get("isolation_multiplier", 1.0)
        effective_isolation_prob = min(
            1.0,
            isolation_prob * isolation_multiplier,
        )
        if rng.random() < effective_isolation_prob:
            nodes_to_isolate.append(node)
            continue

        # If isolation fails, each infected neighbour gets an independent
        # opportunity to transmit malware.
        for _ in infected_neighbours:
            susceptibility = G.nodes[node].get("susceptibility", 1.0)
            transmission_probability = min(1.0, beta * susceptibility)
            if rng.random() < transmission_probability:
                nodes_to_infect.append(node)
                break

    # Apply all state changes only after every susceptible node has been
    # evaluated, preserving synchronous updating.
    for node in nodes_to_isolate:
        G.nodes[node]["state"] = ISOLATED

    for node in nodes_to_infect:
        G.nodes[node]["state"] = INFECTED

    return nodes_to_infect, nodes_to_isolate


def run_isolation_simulation(
    G,
    beta,
    isolation_prob,
    steps,
    seed=None
):
    """
    Run malware propagation with decentralized local isolation.

    Unlike preventive patching, isolation is evaluated dynamically during
    every simulation step in response to nearby infected devices.

    The simulation records both infection growth and the cumulative number
    of isolated devices so that containment effectiveness can later be
    compared with its availability cost.

    Parameters
    ----------
    G : networkx.Graph
        Network on which the simulation is run.
    beta : float
        Infection probability for each infected-susceptible edge.
    isolation_prob : float
        Probability that an exposed susceptible node isolates.
    steps : int
        Number of simulation steps.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    infected_history : list
        Number of infected nodes at the initial state and after each step.
    isolated_history : list
        Number of isolated nodes at the initial state and after each step.
    """
    rng = np.random.default_rng(seed)

    initialise_infection(
        G,
        seed=seed
    )

    infected_history = [
        count_infected(G)
    ]

    isolated_history = [0]

    for _ in range(steps):
        infection_isolation_step(
            G,
            beta,
            isolation_prob,
            rng
        )

        infected_history.append(
            count_infected(G)
        )

        isolated_history.append(
            sum(
                G.nodes[node]["state"] == ISOLATED
                for node in G.nodes()
            )
        )

    return infected_history, isolated_history