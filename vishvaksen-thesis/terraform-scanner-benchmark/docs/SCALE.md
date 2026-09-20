# Corpus scale

Formal CA2: **60 modules per category**, four AWS categories, **~60% defective**
(36 insecure + 24 secure), **N = 240**, matching the Rahman et al. (2023)
240-manifest oracle order of magnitude.

This generator **emits the full formal N**, not a subset.

| Category | Secure | Insecure | Defective fraction | Patterns |
|----------|-------:|---------:|-------------------:|---------:|
| public_storage | 24 | 36 | 0.60 | 12 × (s01,s02,i01,i02,i03) |
| overpermissive_access | 24 | 36 | 0.60 | 12 × (s01,s02,i01,i02,i03) |
| encryption_at_rest | 24 | 36 | 0.60 | 12 × (s01,s02,i01,i02,i03) |
| weak_logging | 24 | 36 | 0.60 | 12 × (s01,s02,i01,i02,i03) |
| **Total** | **96** | **144** | **0.60** | 48 pattern families |

Variants:

- `s01` / `s02` — secure (second copy changes region / identifiers)
- `i01` — insecure literal on the defective attribute
- `i02` — insecure via **variable default** (indirection; intended residual FN for literal gates)
- `i03` — insecure alternate literal (e.g. `public-read-write` vs `public-read`)

Each insecure module names a secure sibling (`s01` of the same pattern) for
remediation LOC (unified-diff line count). Pairs differ on the defect
attribute, or on the smallest change-set that realises the misconfiguration
(e.g. public ACL plus public-access-block disabled). Documented in labels.

Labels are written **before** scanners run (`scripts/generate_corpus.py`).
The second-reviewer 20% subsample is specified in
`docs/SECOND_REVIEW_PROTOCOL.md` and is **not executed** in this pass.
