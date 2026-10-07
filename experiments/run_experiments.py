"""Run repeated, parameter-sweep experiments and write comparative results."""

import argparse
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from src.containment import (
    random_patching,
    run_isolation_simulation,
    run_patching_simulation,
    targeted_patching,
)
from src.devices import assign_device_profiles
from src.networks import (
    create_random_network,
    create_scale_free_network,
    create_small_world_network,
)
from src.propagation import run_simulation
from utils.metrics import post_containment_connectivity


TOPOLOGIES = ("Random", "Small-World", "Scale-Free")
PATCH_STRATEGIES = {
    "random_patching": random_patching,
    "targeted_patching": targeted_patching,
}
STRATEGY_ORDER = (
    "no_containment",
    "random_patching",
    "targeted_patching",
    "local_isolation",
)
METRIC_COLUMNS = (
    "final_infected_fraction",
    "peak_infected_fraction",
    "active_device_fraction",
    "largest_component_fraction_active",
    "largest_component_fraction_total",
    "component_count",
)


def _derive_seed(*parts):
    """Derive stable independent seeds without relying on Python hash()."""
    return int(
        np.random.SeedSequence(parts).generate_state(1, dtype=np.uint32)[0]
    )


def _create_network(topology, n, average_degree, seed):
    if topology == "Random":
        return create_random_network(
            n=n,
            p=average_degree / (n - 1),
            seed=seed,
        )
    if topology == "Small-World":
        k = min(n - 1, max(2, int(round(average_degree))))
        if k % 2:
            k -= 1
        return create_small_world_network(
            n=n,
            k=k,
            rewiring_prob=0.1,
            seed=seed,
        )
    if topology == "Scale-Free":
        return create_scale_free_network(
            n=n,
            m=max(1, min(n - 1, int(round(average_degree / 2)))),
            seed=seed,
        )
    raise ValueError(f"Unknown topology: {topology}")


def _validate_experiment_inputs(
    n,
    average_degree,
    steps,
    seeds,
    betas,
    patch_budgets,
    isolation_probabilities,
):
    if n < 3:
        raise ValueError("n must be at least 3.")
    if not 0 < average_degree < n - 1:
        raise ValueError("average_degree must be greater than 0 and less than n - 1.")
    if steps < 0:
        raise ValueError("steps must be non-negative.")
    if not seeds or any(seed < 0 for seed in seeds):
        raise ValueError("Provide at least one non-negative random seed.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Random seeds must be unique.")
    for name, values in (
        ("betas", betas),
        ("patch_budgets", patch_budgets),
        ("isolation_probabilities", isolation_probabilities),
    ):
        if not values:
            raise ValueError(f"{name} must contain at least one value.")
        if any(not np.isfinite(value) or not 0 <= value <= 1 for value in values):
            raise ValueError(f"All {name} values must be finite and between 0 and 1.")
    if any(value >= 1 for value in patch_budgets):
        raise ValueError("Patch budgets must be less than 1 to leave a seed node.")


def run_parameter_sweep(
    n=1000,
    average_degree=6,
    steps=50,
    seeds=tuple(range(42, 52)),
    betas=(0.05, 0.1, 0.2, 0.3),
    patch_budgets=(0.1, 0.2, 0.3),
    isolation_probabilities=(0.1, 0.3, 0.5),
    heterogeneous=True,
):
    """
    Run each topology/seed/beta combination under all four strategies.

    Patching budgets and local isolation probabilities are swept only for
    the strategy that uses each control, avoiding duplicate experiments
    for irrelevant parameters.
    """
    _validate_experiment_inputs(
        n,
        average_degree,
        steps,
        seeds,
        betas,
        patch_budgets,
        isolation_probabilities,
    )

    rows = []
    for topology_index, topology in enumerate(TOPOLOGIES):
        for seed in seeds:
            network_seed = _derive_seed(seed, topology_index, 0)
            base_graph = _create_network(
                topology,
                n,
                average_degree,
                network_seed,
            )
            if heterogeneous:
                assign_device_profiles(
                    base_graph,
                    seed=_derive_seed(seed, topology_index, 1),
                )

            for beta_index, beta in enumerate(betas):
                run_index = 0
                scenarios = [("no_containment", None, None)]
                scenarios.extend(
                    (strategy, patch_budget, None)
                    for patch_budget in patch_budgets
                    for strategy in PATCH_STRATEGIES
                )
                scenarios.extend(
                    ("local_isolation", None, isolation_probability)
                    for isolation_probability in isolation_probabilities
                )

                for strategy, patch_budget, isolation_probability in scenarios:
                    graph = nx.Graph(base_graph)
                    simulation_seed = _derive_seed(
                        seed,
                        topology_index,
                        beta_index,
                        run_index,
                        2,
                    )
                    run_index += 1

                    if strategy == "no_containment":
                        infected_history, _ = run_simulation(
                            graph,
                            beta=beta,
                            steps=steps,
                            seed=simulation_seed,
                        )
                    elif strategy in PATCH_STRATEGIES:
                        infected_history = run_patching_simulation(
                            graph,
                            beta=beta,
                            steps=steps,
                            patch_strategy=PATCH_STRATEGIES[strategy],
                            patch_budget=patch_budget,
                            seed=simulation_seed,
                        )
                    else:
                        infected_history, _ = run_isolation_simulation(
                            graph,
                            beta=beta,
                            isolation_prob=isolation_probability,
                            steps=steps,
                            seed=simulation_seed,
                        )

                    connectivity = post_containment_connectivity(graph)
                    rows.append(
                        {
                            "topology": topology,
                            "seed": seed,
                            "network_seed": network_seed,
                            "beta": beta,
                            "steps": steps,
                            "strategy": strategy,
                            "patch_budget": patch_budget,
                            "isolation_probability": isolation_probability,
                            "device_model": (
                                "heterogeneous" if heterogeneous else "homogeneous"
                            ),
                            "final_infected_fraction": (
                                infected_history[-1] / n
                            ),
                            "peak_infected_fraction": max(infected_history) / n,
                            "active_device_fraction": (
                                connectivity["active_devices"] / n
                            ),
                            "largest_component_fraction_active": connectivity[
                                "largest_component_fraction_active"
                            ],
                            "largest_component_fraction_total": connectivity[
                                "largest_component_fraction_total"
                            ],
                            "component_count": connectivity["component_count"],
                            "isolated_devices": connectivity["isolated_devices"],
                        }
                    )

    return pd.DataFrame(rows)


def summarize_runs(runs):
    """Aggregate replicate-level outcomes and approximate 95% confidence intervals."""
    group_columns = [
        "topology",
        "beta",
        "strategy",
        "patch_budget",
        "isolation_probability",
        "device_model",
    ]
    summary = (
        runs.groupby(group_columns, dropna=False)[list(METRIC_COLUMNS)]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    summary.columns = [
        "_".join(str(part) for part in column if part != "")
        if isinstance(column, tuple)
        else column
        for column in summary.columns
    ]
    for metric in METRIC_COLUMNS:
        standard_error = summary[f"{metric}_std"].fillna(0) / np.sqrt(
            summary[f"{metric}_count"]
        )
        summary[f"{metric}_ci95"] = 1.96 * standard_error
    return summary


def _best_setting(rows):
    """Select the lowest-infection setting, breaking ties by availability."""
    return rows.sort_values(
        [
            "final_infected_fraction_mean",
            "largest_component_fraction_total_mean",
        ],
        ascending=[True, False],
    ).iloc[0]


def build_comparison_report(runs, summary):
    """Create a concise, seed-aggregated comparison in Markdown."""
    seeds = sorted(int(seed) for seed in runs["seed"].unique())
    model = str(runs["device_model"].iloc[0])
    betas = sorted(float(beta) for beta in runs["beta"].unique())
    lines = [
        "# Final comparative analysis",
        "",
        f"- Device model: **{model}**.",
        f"- Independent random seeds: **{len(seeds)}** "
        f"({', '.join(map(str, seeds))}).",
        f"- Infection probabilities: **{', '.join(f'{beta:g}' for beta in betas)}**.",
        "- Infection outcomes are the final infected fraction after the configured "
        "number of synchronous steps.",
        "- Connectivity excludes isolated devices; patched and infected devices "
        "remain online. The reported giant-component fraction is relative to all "
        "devices, including isolated devices.",
        "- 95% intervals use the normal approximation (mean ± 1.96 × standard error).",
        "",
        "Each strategy is represented by its lowest-mean-infection setting for "
        "that topology and beta. This is a descriptive comparison of the swept "
        "settings, not an out-of-sample optimum.",
        "",
        "| Topology | beta | Strategy | Setting | Final infected | 95% CI | "
        "Online | Largest component |",
        "|---|---:|---|---|---:|---:|---:|---:|",
    ]

    for topology in TOPOLOGIES:
        for beta in betas:
            group = summary[
                (summary["topology"] == topology)
                & np.isclose(summary["beta"], beta)
            ]
            for strategy in STRATEGY_ORDER:
                candidates = group[group["strategy"] == strategy]
                if candidates.empty:
                    continue
                row = _best_setting(candidates)
                if strategy == "random_patching" or strategy == "targeted_patching":
                    setting = f"patch budget {row['patch_budget']:g}"
                elif strategy == "local_isolation":
                    setting = f"isolation probability {row['isolation_probability']:g}"
                else:
                    setting = "none"
                mean = row["final_infected_fraction_mean"]
                ci = row["final_infected_fraction_ci95"]
                lines.append(
                    f"| {topology} | {beta:g} | {strategy} | {setting} | "
                    f"{mean:.3f} | ±{ci:.3f} | "
                    f"{row['active_device_fraction_mean']:.3f} | "
                    f"{row['largest_component_fraction_total_mean']:.3f} |"
                )

    lines.extend(
        [
            "",
            "## Interpretation notes",
            "",
            "- Compare infection control alongside online fraction and largest-component "
            "fraction: isolation can reduce infections by taking devices offline.",
            "- Device profiles are deliberately illustrative and should be calibrated "
            "against evidence before making real-world claims.",
            "- Use `experiment_summary.csv` for every swept intervention setting and "
            "`experiment_runs.csv` for seed-level observations.",
            "",
        ]
    )
    return "\n".join(lines)


def write_experiment_outputs(runs, output_dir):
    """Write raw observations, replicate summaries, and the final report."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_runs(runs)
    runs.to_csv(output_dir / "experiment_runs.csv", index=False)
    summary.to_csv(output_dir / "experiment_summary.csv", index=False)
    (output_dir / "final_comparison.md").write_text(
        build_comparison_report(runs, summary),
        encoding="utf-8",
    )
    return summary


def _parse_values(value):
    try:
        return tuple(float(item.strip()) for item in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Values must be comma-separated numbers."
        ) from error


def main():
    parser = argparse.ArgumentParser(
        description="Run reproducible IoT malware containment sweeps."
    )
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--average-degree", type=float, default=6)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seeds", type=int, default=10, help="Number of replicates.")
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument("--betas", type=_parse_values, default=(0.05, 0.1, 0.2, 0.3))
    parser.add_argument(
        "--patch-budgets",
        type=_parse_values,
        default=(0.1, 0.2, 0.3),
    )
    parser.add_argument(
        "--isolation-probabilities",
        type=_parse_values,
        default=(0.1, 0.3, 0.5),
    )
    parser.add_argument("--homogeneous", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    if args.seeds < 1:
        parser.error("--seeds must be at least 1.")
    seeds = tuple(range(args.base_seed, args.base_seed + args.seeds))
    runs = run_parameter_sweep(
        n=args.n,
        average_degree=args.average_degree,
        steps=args.steps,
        seeds=seeds,
        betas=args.betas,
        patch_budgets=args.patch_budgets,
        isolation_probabilities=args.isolation_probabilities,
        heterogeneous=not args.homogeneous,
    )
    write_experiment_outputs(runs, args.output_dir)
    print(
        f"Wrote {len(runs)} simulation results and the comparative analysis "
        f"to {args.output_dir}."
    )


if __name__ == "__main__":
    main()
