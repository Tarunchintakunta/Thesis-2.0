# data/external/

## loghub/BGL_2k.log (labelled source corpus for D2)

* What: the 2,000 line sample of the Blue Gene/L supercomputer log from Loghub.
  The first field of every line is `-` for normal lines and an alert tag
  (e.g. `KERNDTLB`, `APPSEV`) for anomalous ones, so the labels come with it.
  1,857 normal / 142 alert lines (7.1 %).
* Where: https://github.com/logpai/loghub (file `BGL/BGL_2k.log`)
* Terms: Loghub states that its datasets "are freely available for research or
  academic work". Ethics scenario 2A - cite the source and link to it.
* Citation: Zhu, J., He, S., He, P., Liu, J. and Lyu, M.R. (2023) 'Loghub: a
  large collection of system log datasets for AI-driven log analytics', ISSRE
  2023. https://doi.org/10.1109/ISSRE59848.2023.00071
* Integrity: SHA-256 `2a819ea540909db682005c9cf948387a40729b5c2e9f19d430e29ce704825496`
  (checked by `scripts/fetch_loghub.sh`).

The file itself is **not committed** (gitignored) - it is not ours to
redistribute. `scripts/fetch_loghub.sh` downloads and verifies it; CI does the
same.
