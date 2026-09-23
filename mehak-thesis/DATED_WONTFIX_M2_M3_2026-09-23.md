# DATED WONTFIX — Mehak M2 / M3 (2026-09-23)

**Thesis:** mehak-thesis / `mhsa-tdl-framework`  
**IDs:** M2 (true net-bytes), M3 (full 2011 dump / 2019 Borg cells)  
**Disposition:** **DATED_WONTFIX** — schema / beyond disclosed floor; not remediable on 2011 parts in-repo.

## M2 — true network-byte channel
ClusterData **2011** `task_usage` has **no** network-byte / bandwidth column (`data/gct/CHANNEL_HONESTY.md`).  
MHSA 4th channel = **sampled CPU**; `net_channel_is_network_bytes=false` in load meta.  
Inventing a byte series would break evidence rules. Optional 2019 Borg cells (which expose assigned network) remain **beyond-CA2**.

## M3 — full dump / 2019 cells
Formal floor is answered on the disclosed **4 event + 2 usage** 2011 parts (`results/gct/final_*`, `hard_verify_*`).  
Remaining 2011 parts and 2019 eight-cell Borg dumps are scoped-out optionals (`DESIGN_RATIONALE_BEYOND_CA2.md`) — not open remediable gaps.

## Audit gate
`mhsa-tdl-framework/scripts/audit_mhsa_negative_root_causes.py` treats M2/M3 as closed when this amendment + CHANNEL_HONESTY + net flag exist.  
Negative MHSA result (Acc < Aldomi/RF) stays **evidenced**, not WONTFIX.
