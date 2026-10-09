# Final comparative analysis

- Device model: **heterogeneous**.
- Independent random seeds: **3** (100, 101, 102).
- Infection probabilities: **0.1, 0.2**.
- Infection outcomes are the final infected fraction after the configured number of synchronous steps.
- Connectivity excludes isolated devices; patched and infected devices remain online. The reported giant-component fraction is relative to all devices, including isolated devices.
- 95% intervals use the normal approximation (mean ± 1.96 × standard error).

Each strategy is represented by its lowest-mean-infection setting for that topology and beta. This is a descriptive comparison of the swept settings, not an out-of-sample optimum.

| Topology | beta | Strategy | Setting | Final infected | 95% CI | Online | Largest component |
|---|---:|---|---|---:|---:|---:|---:|
| Random | 0.1 | no_containment | none | 0.798 | ±0.196 | 1.000 | 0.998 |
| Random | 0.1 | random_patching | patch budget 0.2 | 0.492 | ±0.131 | 1.000 | 0.998 |
| Random | 0.1 | targeted_patching | patch budget 0.2 | 0.345 | ±0.142 | 1.000 | 0.998 |
| Random | 0.1 | local_isolation | isolation probability 0.4 | 0.033 | ±0.056 | 0.887 | 0.877 |
| Random | 0.2 | no_containment | none | 0.987 | ±0.007 | 1.000 | 0.998 |
| Random | 0.2 | random_patching | patch budget 0.2 | 0.777 | ±0.003 | 1.000 | 0.998 |
| Random | 0.2 | targeted_patching | patch budget 0.2 | 0.708 | ±0.014 | 1.000 | 0.998 |
| Random | 0.2 | local_isolation | isolation probability 0.4 | 0.192 | ±0.199 | 0.683 | 0.607 |
| Small-World | 0.1 | no_containment | none | 0.355 | ±0.099 | 1.000 | 1.000 |
| Small-World | 0.1 | random_patching | patch budget 0.2 | 0.183 | ±0.218 | 1.000 | 1.000 |
| Small-World | 0.1 | targeted_patching | patch budget 0.2 | 0.107 | ±0.083 | 1.000 | 1.000 |
| Small-World | 0.1 | local_isolation | isolation probability 0.4 | 0.022 | ±0.012 | 0.940 | 0.927 |
| Small-World | 0.2 | no_containment | none | 0.948 | ±0.054 | 1.000 | 1.000 |
| Small-World | 0.2 | random_patching | patch budget 0.2 | 0.695 | ±0.029 | 1.000 | 1.000 |
| Small-World | 0.2 | targeted_patching | patch budget 0.2 | 0.132 | ±0.120 | 1.000 | 1.000 |
| Small-World | 0.2 | local_isolation | isolation probability 0.4 | 0.023 | ±0.018 | 0.937 | 0.913 |
| Scale-Free | 0.1 | no_containment | none | 0.922 | ±0.064 | 1.000 | 1.000 |
| Scale-Free | 0.1 | random_patching | patch budget 0.2 | 0.580 | ±0.089 | 1.000 | 1.000 |
| Scale-Free | 0.1 | targeted_patching | patch budget 0.2 | 0.027 | ±0.033 | 1.000 | 1.000 |
| Scale-Free | 0.1 | local_isolation | isolation probability 0.4 | 0.043 | ±0.070 | 0.857 | 0.830 |
| Scale-Free | 0.2 | no_containment | none | 1.000 | ±0.000 | 1.000 | 1.000 |
| Scale-Free | 0.2 | random_patching | patch budget 0.2 | 0.772 | ±0.027 | 1.000 | 1.000 |
| Scale-Free | 0.2 | targeted_patching | patch budget 0.2 | 0.093 | ±0.094 | 1.000 | 1.000 |
| Scale-Free | 0.2 | local_isolation | isolation probability 0.4 | 0.097 | ±0.093 | 0.732 | 0.590 |

## Interpretation notes

- Compare infection control alongside online fraction and largest-component fraction: isolation can reduce infections by taking devices offline.
- Device profiles are deliberately illustrative and should be calibrated against evidence before making real-world claims.
- Use `experiment_summary.csv` for every swept intervention setting and `experiment_runs.csv` for seed-level observations.
