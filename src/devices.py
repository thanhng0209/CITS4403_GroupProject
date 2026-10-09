"""Illustrative device profiles for heterogeneous IoT simulations."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DeviceProfile:
    """Relative device characteristics used by the propagation model."""

    name: str
    susceptibility: float
    isolation_multiplier: float


# These are scenario assumptions, not empirically calibrated device data.
DEVICE_PROFILES = (
    DeviceProfile("constrained", susceptibility=1.5, isolation_multiplier=0.5),
    DeviceProfile("standard", susceptibility=1.0, isolation_multiplier=1.0),
    DeviceProfile("hardened", susceptibility=0.5, isolation_multiplier=1.5),
)


def assign_device_profiles(G, seed=None, profiles=DEVICE_PROFILES):
    """Assign an approximately even, reproducible mix of device profiles."""
    if not profiles:
        raise ValueError("At least one device profile is required.")
    if any(
        profile.susceptibility < 0 or profile.isolation_multiplier < 0
        for profile in profiles
    ):
        raise ValueError("Device profile multipliers must be non-negative.")

    rng = np.random.default_rng(seed)
    nodes = list(G.nodes())
    profile_indices = np.resize(
        rng.permutation(len(profiles)),
        len(nodes),
    )
    rng.shuffle(profile_indices)

    for node, profile_index in zip(nodes, profile_indices):
        profile = profiles[int(profile_index)]
        G.nodes[node].update(
            device_type=profile.name,
            susceptibility=profile.susceptibility,
            isolation_multiplier=profile.isolation_multiplier,
        )

    return {
        profile.name: sum(
            G.nodes[node]["device_type"] == profile.name
            for node in nodes
        )
        for profile in profiles
    }
