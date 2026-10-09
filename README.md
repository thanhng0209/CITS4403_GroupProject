# CITS4403 Computational Modelling Research Project

## Project Topic

**Malware/Botnet Propagation in Heterogeneous IoT Networks**

## Research Question

**Under what network topologies and infection rates does decentralized local node isolation outperform centralized patching strategies in containing a fast-spreading worm?**

## Project Overview

This project investigates malware propagation and containment in IoT networks using computational network models.

Three network topologies are currently considered:

- Erdős–Rényi Random Network
- Watts–Strogatz Small-World Network
- Barabási–Albert Scale-Free Network

The baseline model simulates probabilistic malware transmission between connected devices.

Three containment strategies are currently implemented:

1. Random centralized patching
2. Degree-targeted centralized patching
3. Decentralized local node isolation

The project will compare these strategies across different network structures and model parameters using infection outcomes and network-level metrics.

## Project Structure

```text
CITS4403_GroupProject/
├── src/
│   ├── __init__.py
│   ├── states.py
│   ├── networks.py
│   ├── propagation.py
│   ├── containment.py
│   └── devices.py
├── experiments/
│   └── run_experiments.py
├── utils/
│   ├── __init__.py
│   ├── metrics.py
│   └── visualisation.py
├── tests/
├── data/
├── notebooks/
│   └── mal_sim.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```

### `src/`

Contains the main model implementation.

- `states.py` — node-state definitions
- `networks.py` — network topology generation
- `propagation.py` — baseline malware propagation model
- `containment.py` — containment strategies and containment simulations
- `devices.py` — illustrative heterogeneous IoT device profiles

### `experiments/`

- `run_experiments.py` — repeated simulations, parameter sweeps, summary
  statistics, and final comparative report generation

### `tests/`

Contains tests for device assignment, connectivity metrics, and deterministic
experiment output.

### `utils/`

Contains reusable helper functions.

- `metrics.py` — network and simulation metrics
- `visualisation.py` — network plots, degree distributions, and propagation animations

### `notebooks/`

Contains the main Jupyter Notebook used for:

- model explanation
- parameter configuration
- experiments
- visualisation
- preliminary analysis

## Setup

Python 3.x is required.

Create and activate a virtual environment if needed, then install the dependencies:

```bash
pip install -r requirements.txt
```

Start Jupyter Notebook from the project root:

```bash
jupyter notebook
```

Then open:

```text
notebooks/mal_sim.ipynb
```

## Current Model Parameters

The preliminary experiments currently use:

- Number of nodes: `1000`
- Target average degree: approximately `6`
- Infection probability (`beta`): `0.1`
- Simulation duration: `50` steps
- Patch budget: `20%`
- Local isolation probability: `0.1`
- Random seed: `42`

These values describe the preliminary notebook configuration. The separate
experiment runner below provides repeated seeds and systematic parameter sweeps.

## Repeated Experiments and Comparative Analysis

Run the complete default sweep from the project root:

```bash
python -m experiments.run_experiments
```

The default experiment uses 10 seeds (`42`–`51`), 1,000 nodes, 50 steps,
infection probabilities `0.05`, `0.1`, `0.2`, and `0.3`, patch budgets
`0.1`, `0.2`, and `0.3`, and local-isolation probabilities `0.1`, `0.3`,
and `0.5`. It runs the three network topologies against no containment,
random patching, degree-targeted patching, and local isolation. Intervention
parameters are swept only for the strategies that use them.

Example of a smaller exploratory run:

```bash
python -m experiments.run_experiments \
  --n 200 --steps 20 --seeds 3 --base-seed 100 \
  --betas 0.1,0.2 --patch-budgets 0.1,0.2 \
  --isolation-probabilities 0.2,0.4
```

The run writes these reproducible outputs to `data/` by default:

- `experiment_runs.csv` — one row per simulation, including its random seed,
  final and peak infection, online-device fraction, and post-containment
  connectivity
- `experiment_summary.csv` — means and approximate 95% confidence intervals
  for each topology, infection probability, strategy, and intervention setting
- `final_comparison.md` — a seed-aggregated comparison of the best observed
  intervention setting for each strategy, topology, and infection probability

Pass `--output-dir PATH` to write results elsewhere. Add `--homogeneous` to
disable device-profile effects for a homogeneous comparison.

### Heterogeneous device assumptions

The default model assigns an approximately even, seed-reproducible mix of
three illustrative device profiles: constrained devices have `1.5×`
susceptibility and `0.5×` isolation response; standard devices use `1.0×`
for both; hardened devices use `0.5×` susceptibility and `1.5×` isolation
response. Multipliers scale the configured transmission or isolation
probability, capped at 1. These are explicit scenario assumptions rather
than calibrated real-world measurements; adjust `DEVICE_PROFILES` in
`src/devices.py` when evidence supports different values.

Post-containment connectivity excludes isolated devices but includes patched
and infected devices. Results therefore report online fraction and the size
of the largest connected component both among online devices and relative to
the full network, so infection control is considered alongside availability.
The report's 95% intervals use the normal approximation and its "best observed"
setting is descriptive, not an out-of-sample optimum.

## Current Progress

- [x] Network topology generation
- [x] Network visualisation and degree-distribution analysis
- [x] Baseline malware propagation model
- [x] Random centralized patching
- [x] Degree-targeted centralized patching
- [x] Decentralized local isolation
- [x] Modular project structure
- [x] Repeated simulations across multiple random seeds
- [x] Parameter sweep experiments
- [x] Post-containment connectivity analysis
- [x] Heterogeneous IoT device modelling
- [x] Final comparative analysis report generation

## Team Members

- Wenkow Sun
- Ben Nguyen
