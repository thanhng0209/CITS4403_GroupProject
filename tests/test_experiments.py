import tempfile
import unittest
from pathlib import Path

import networkx as nx
import pandas as pd

from experiments.run_experiments import (
    run_parameter_sweep,
    summarize_runs,
    write_experiment_outputs,
)
from src.containment import infection_isolation_step
from src.devices import assign_device_profiles
from utils.metrics import post_containment_connectivity


class FixedRandom:
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


class DeviceProfileTests(unittest.TestCase):
    def test_profile_assignment_is_balanced_and_reproducible(self):
        first = nx.path_graph(12)
        second = nx.path_graph(12)

        first_counts = assign_device_profiles(first, seed=17)
        second_counts = assign_device_profiles(second, seed=17)

        self.assertEqual(first_counts, {"constrained": 4, "standard": 4, "hardened": 4})
        self.assertEqual(first_counts, second_counts)
        self.assertEqual(
            nx.get_node_attributes(first, "device_type"),
            nx.get_node_attributes(second, "device_type"),
        )

    def test_susceptibility_multiplier_changes_transmission_probability(self):
        graph = nx.path_graph(2)
        graph.nodes[0]["state"] = "I"
        graph.nodes[1]["state"] = "S"
        graph.nodes[1]["susceptibility"] = 2.0

        from src.propagation import infection_step

        infection_step(graph, beta=0.5, rng=FixedRandom(0.75))

        self.assertEqual(graph.nodes[1]["state"], "I")

    def test_isolation_multiplier_changes_local_response_probability(self):
        graph = nx.path_graph(2)
        graph.nodes[0]["state"] = "I"
        graph.nodes[1]["state"] = "S"
        graph.nodes[1]["isolation_multiplier"] = 2.0

        infection_isolation_step(
            graph,
            beta=0.5,
            isolation_prob=0.5,
            rng=FixedRandom(0.75),
        )

        self.assertEqual(graph.nodes[1]["state"], "X")


class ConnectivityMetricTests(unittest.TestCase):
    def test_isolated_nodes_are_excluded_but_other_nodes_stay_available(self):
        graph = nx.path_graph(3)
        graph.nodes[1]["state"] = "X"
        graph.nodes[0]["state"] = "P"
        graph.nodes[2]["state"] = "I"

        metrics = post_containment_connectivity(graph)

        self.assertEqual(metrics["active_devices"], 2)
        self.assertEqual(metrics["component_count"], 2)
        self.assertEqual(metrics["largest_component_fraction_total"], 1 / 3)


class ExperimentTests(unittest.TestCase):
    def test_sweep_is_reproducible_and_writes_comparison_outputs(self):
        kwargs = {
            "n": 30,
            "average_degree": 4,
            "steps": 3,
            "seeds": (5, 9),
            "betas": (0.1,),
            "patch_budgets": (0.2,),
            "isolation_probabilities": (0.3,),
        }
        runs = run_parameter_sweep(**kwargs)
        repeated_runs = run_parameter_sweep(**kwargs)

        pd.testing.assert_frame_equal(runs, repeated_runs)
        self.assertEqual(len(runs), 3 * 2 * 4)

        summary = summarize_runs(runs)
        self.assertTrue((summary["final_infected_fraction_count"] == 2).all())
        with tempfile.TemporaryDirectory() as output_dir:
            write_experiment_outputs(runs, output_dir)
            self.assertTrue((Path(output_dir) / "experiment_runs.csv").is_file())
            self.assertTrue((Path(output_dir) / "experiment_summary.csv").is_file())
            report = (Path(output_dir) / "final_comparison.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("# Final comparative analysis", report)
            self.assertIn("95% CI", report)


if __name__ == "__main__":
    unittest.main()
