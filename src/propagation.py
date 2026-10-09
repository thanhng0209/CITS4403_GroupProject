"""
Baseline malware propagation model.

This module contains the core infection dynamics used throughout the
project. Devices are represented as nodes in a NetworkX graph, and
malware spreads probabilistically across graph edges.

The baseline model uses synchronous updating: infection attempts for a
time step are evaluated first, and newly infected nodes are updated only
after all attempts for that step have been completed.
"""

import numpy as np
import networkx as nx

from src.states import (
    SUSCEPTIBLE,
    INFECTED
)

from utils.metrics import count_infected


def initialise_infection(G, seed=None):
    """
    Reset all nodes to susceptible and infect one randomly selected node.

    Parameters
    ----------
    G : networkx.Graph
        Network on which the malware propagation model is run.
    seed : int, optional
        Random seed used when selecting the initial infected node.

    Returns
    -------
    node
        The node selected as the initial infected device.
    """
    rng = np.random.default_rng(seed)

    # Reset all devices before starting a new simulation.
    nx.set_node_attributes(
        G,
        SUSCEPTIBLE,
        "state"
    )

    initial_node = rng.choice(
        list(G.nodes())
    )

    G.nodes[initial_node]["state"] = INFECTED

    return initial_node


def infection_step(G, beta, rng):
    """
    Perform one synchronous malware propagation step.

    Each infected node independently attempts to infect each susceptible
    neighbour with probability beta.

    New infections are collected first and applied only after all
    transmission attempts have been evaluated. This prevents nodes that
    become infected during the current step from transmitting again
    within the same step.

    Parameters
    ----------
    G : networkx.Graph
        Network containing node infection states.
    beta : float
        Probability that an infected node successfully transmits malware
        to a susceptible neighbour during one simulation step.
    rng : numpy.random.Generator
        Random-number generator used for transmission attempts.

    Returns
    -------
    int
        Number of nodes newly infected during this step.
    """
    # Store new infections before changing any node states so that the
    # update remains synchronous.
    newly_infected = set()

    for node in G.nodes():

        if G.nodes[node]["state"] != INFECTED:
            continue

        for neighbour in G.neighbors(node):

            if G.nodes[neighbour]["state"] != SUSCEPTIBLE:
                continue

            susceptibility = G.nodes[neighbour].get("susceptibility", 1.0)
            transmission_probability = min(1.0, beta * susceptibility)
            if rng.random() < transmission_probability:
                newly_infected.add(neighbour)

    # Apply all infections only after every transmission attempt for the
    # current step has been evaluated.
    for node in newly_infected:
        G.nodes[node]["state"] = INFECTED

    return len(newly_infected)


def run_simulation(
    G,
    beta,
    steps,
    seed=None
):
    """
    Run the baseline malware propagation model.

    The network is initialised with one infected node and the infection
    rule is then applied repeatedly for the requested number of steps.

    Both the number of infected devices and a snapshot of every node
    state are recorded at each step. The state snapshots are later used
    for visualisation and animation.

    Parameters
    ----------
    G : networkx.Graph
        Network on which the simulation is run.
    beta : float
        Infection probability for each infected-susceptible edge.
    steps : int
        Number of simulation steps.
    seed : int, optional
        Random seed used for reproducibility.

    Returns
    -------
    infected_history : list
        Number of infected nodes at the initial state and after each step.
    states_history : list
        Copies of all node states at the initial state and after each step.
    """
    rng = np.random.default_rng(seed)

    initialise_infection(
        G,
        seed=seed
    )

    infected_history = [
        count_infected(G)
    ]

    # Store independent copies because node states continue changing
    # throughout the simulation.
    states_history = [
        nx.get_node_attributes(
            G,
            "state"
        ).copy()
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

        states_history.append(
            nx.get_node_attributes(
                G,
                "state"
            ).copy()
        )

    return infected_history, states_history