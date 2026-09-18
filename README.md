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
│   └── containment.py
├── utils/
│   ├── __init__.py
│   ├── metrics.py
│   └── visualisation.py
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

These values are currently used for preliminary model development and will later be extended into systematic parameter sweeps and repeated experiments.

## Current Progress

- [x] Network topology generation
- [x] Network visualisation and degree-distribution analysis
- [x] Baseline malware propagation model
- [x] Random centralized patching
- [x] Degree-targeted centralized patching
- [x] Decentralized local isolation
- [x] Modular project structure
- [ ] Repeated simulations across multiple random seeds
- [ ] Parameter sweep experiments
- [ ] Post-containment connectivity analysis
- [ ] Heterogeneous IoT device modelling
- [ ] Final comparative analysis

## Team Members

- Wenkow Sun
- Ben Nguyen
