"""
Visualisation utilities for network structure and malware propagation.

This module contains reusable plotting and animation functions used by
the experiment notebook. Experimental interpretation remains in the
notebook, while this module handles presentation of model outputs.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from IPython.display import HTML

from src.states import INFECTED


def plot_network(
    G,
    title,
    highlight_hubs=False,
    seed=42
):
    """
    Plot a network using a spring-layout visualisation.

    For scale-free networks, highly connected nodes can optionally be
    highlighted. Nodes in the top 10 percent of the degree distribution
    are treated as hubs and displayed with larger node sizes.

    Parameters
    ----------
    G : networkx.Graph
        Network to visualise.
    title : str
        Plot title.
    highlight_hubs : bool, optional
        Whether to highlight high-degree nodes.
    seed : int, optional
        Random seed used by the spring layout.
    """
    pos = nx.spring_layout(
        G,
        seed=seed
    )

    plt.figure(figsize=(8, 6))

    if highlight_hubs:
        degrees = dict(G.degree())

        degree_values = np.array(
            list(degrees.values())
        )

        hub_threshold = np.percentile(
            degree_values,
            90
        )

        node_colors = [
            "orange"
            if degrees[node] >= hub_threshold
            else "skyblue"
            for node in G.nodes()
        ]

        node_sizes = [
            50 + degrees[node] * 15
            for node in G.nodes()
        ]

    else:
        node_colors = "skyblue"
        node_sizes = 80

    nx.draw(
        G,
        pos,
        node_color=node_colors,
        node_size=node_sizes,
        width=0.6,
        with_labels=False
    )

    plt.title(title)
    plt.show()


def plot_degree_distribution(G, title):
    """
    Plot the empirical node-degree distribution of a network.

    The bar height represents the fraction of nodes with each degree.

    Parameters
    ----------
    G : networkx.Graph
        Network whose degree distribution is visualised.
    title : str
        Plot title.
    """
    degrees = [
        degree
        for _, degree in G.degree()
    ]

    values, counts = np.unique(
        degrees,
        return_counts=True
    )

    probabilities = (
        counts / counts.sum()
    )

    plt.figure(figsize=(7, 5))

    plt.bar(
        values,
        probabilities
    )

    plt.xlabel("Degree")
    plt.ylabel("Probability")
    plt.title(title)

    plt.show()


def animate_propagation(
    G,
    states_history,
    infected_history,
    pos=None,
    title="Malware Propagation",
    interval=500,
    seed=42
):
    """
    Create an animation of malware propagation through a network.

    Infected nodes are displayed in red and all other nodes are displayed
    in blue. The animation uses previously recorded node-state snapshots,
    so producing the animation does not modify or rerun the simulation.

    Parameters
    ----------
    G : networkx.Graph
        Network used in the simulation.
    states_history : list
        Recorded node-state dictionaries for each simulation step.
    infected_history : list
        Number of infected nodes recorded for each simulation step.
    pos : dict, optional
        Precomputed node positions. If omitted, a spring layout is used.
    title : str, optional
        Base title displayed in the animation.
    interval : int, optional
        Delay between animation frames in milliseconds.
    seed : int, optional
        Random seed used when generating the layout.

    Returns
    -------
    IPython.display.HTML
        HTML representation of the animation for display in Jupyter.
    """
    if pos is None:
        pos = nx.spring_layout(
            G,
            seed=seed
        )

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    def update(frame):
        ax.clear()

        states = states_history[frame]

        node_colors = [
            "red"
            if states[node] == INFECTED
            else "skyblue"
            for node in G.nodes()
        ]

        nx.draw(
            G,
            pos,
            ax=ax,
            node_color=node_colors,
            node_size=100,
            width=0.7,
            with_labels=False
        )

        ax.set_title(
            f"{title} - Step {frame}\n"
            f"Infected: "
            f"{infected_history[frame]}/"
            f"{G.number_of_nodes()}"
        )

    animation = FuncAnimation(
        fig,
        update,
        frames=len(states_history),
        interval=interval,
        repeat=False
    )

    # Prevent Jupyter from displaying a duplicate static figure.
    plt.close(fig)

    return HTML(
        animation.to_jshtml()
    )