# Decision matrix - template

Kondragunta Lakshmi Chaitanya - 25171216

Blank version of the table `scripts/analyse.py` fills in
(`reports/paper/tables/<mode>/decision_matrix.md` and `figures/<mode>/decision_matrix.png`).
Only measured (live) or clearly labelled simulated numbers go in.

| Control | Typical Init delta (ms) | Cold-frequency delta | Delta cost / 1k (USD) | p (Holm) | Band | When to use |
|---|---|---|---|---|---|---|
| Switch runtime | | | | | | |
| Prune package | | | | | | |
| Raise memory | | | | | | |
| Low-freq warming | ~0 on Init magnitude | | warming invoke cost | | | |
| Combined free controls | | | | | | |
| *(Future)* Provisioned concurrency | - | - | paid | - | not tested | out of primary scope |

## How each column is computed

* **Typical Init delta** - median Init Duration before minus after (cold samples only).
  Switch runtime: slowest minus fastest runtime at 1024 MB (optimised packages).
  Prune package: default minus optimised per runtime. Raise memory: 128 MB minus 1024 MB.
  Combined: default package at 128 MB minus optimised at 1024 MB.
* **Cold-frequency delta** - cold fraction with the control minus without it. Only
  warming changes it; the other controls change how long a cold start takes, not how often.
* **Delta cost / 1k** - `1000 x (f x dc + (1 - f) x dw)` with `dc`/`dw` the change in mean
  cost of a cold / warm call and `f` the cold fraction of the warm-control arm. For warming:
  cost of the pings per 1,000 real calls minus the billed init time it saves.
* **p (Holm)** - adjusted p-value of the matching pre-registered test (H1, H2_x, H3; H4_x and
  combined_x are exploratory and corrected inside their own family).
* **Band** - adopt / situational / avoid with the thresholds in `docs/ANALYSIS_PLAN.md`
  section 6 (50 ms, 0.10 cold-fraction drop, $0.001 per 1k).
