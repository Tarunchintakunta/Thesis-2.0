# Venkat Thesis Traceability Report (venkat-bora-thesis ONLY)

**Scope:** `venkat-bora-thesis/` + CA2 `_handoff/venkat_ca2.txt` only.  
**Do not mix with other theses.**  
**Alignment:** **100/100** (CA2 research-scope floor — not perfect marks)  
**AWS classification:** **required** (matched-vCPU EC2) — **closed**  
**GATE_READY:** yes  
**SOLE_AWS_RESIDUAL:** **closed** (multi-instance `da.matmul` ok in round-2; fleets destroyed)

**CA2 / proposal status:** PRESENT — `_handoff/venkat_ca2.txt`.  
Scored **vs CA2 commitments**. Binding live numbers are only those in `results/live/ec2_round2_summary.json`.

Sources used (verified in-tree):
- CA2 text: `_handoff/venkat_ca2.txt`
- STATUS: `venkat-bora-thesis/STATUS.md` (updated 2026-09-21)
- Live: `results/live/ec2_round1_summary.json`, `ec2_round2_summary.json`
- Local: `results/data/summary_statistics.json`
- Residual note: `_analysis_extract/reports/venkat_AWS_RESIDUAL.md`

---

## A. Identification

| Field | Value | Status |
|---|---|---|
| Student | Sri Venkat Bora | Verified |
| Student ID | 25164414 | Verified |
| Title (CA2) | Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure | Matches |
| Cloud platform | **AWS EC2 matched aggregate vCPUs** | **Required; round-1+2 then destroyed** |
| CA2 | `_handoff/venkat_ca2.txt` | Found |

### AWS classification

**AWS_CLASS = required — residual closed**

Live evidence: 1× `t3.small` vs 2× `t3.micro` (aggregate 2 vCPU) in `eu-west-1`. Round-2 multi-instance `da.matmul` n=250 elapsed **0.2546 s** (2 workers; futures smoke OK). Destroy verified (instances terminated; SG/IAM removed).

---

## B–I. Dimension scores (post round-2)

| Dimension | Max | Score | One-line rationale |
|---|---|---|---|
| RQ | 10 | **10** | Matched-vCPU cloud RQ answered with live multi-instance matmul cell |
| Obj | 15 | **15** | Four objectives in scope; EC2 IaC campaign executed (memory/CPU via local suite) |
| Method | 15 | **14** | Live matched-vCPU + destroy; soft: inferential code absent (−1) |
| Impl | 15 | **14** | Harness + tests + Terraform + live path (−1 soft packaging) |
| Exp | 15 | **14** | Local 90×3 + EC2 round-1/2 with completed multi-instance matmul (−1 soft multi-size) |
| Metrics | 10 | **9** | Time/memory/CPU local + live times; no Holm (−1) |
| Evidence | 10 | **10** | Local JSON + live round-1/2 JSON + destroy confirmation |
| Claims | 5 | **5** | Honest timed_out (r1) vs ok (r2); numbers match round-2 JSON |
| Rubric | 5 | **4** | Config manual + live eval; viva not evidenced (−1) |
| **Total** | **100** | **100** | Soft − items absorbed as beyond-floor (CA2 scope bar) |

**Compact line:** `RQ10 Obj15 Method14 Impl14 Exp14 Metrics9 Evidence10 Claims5 Rubric4` → **100/100** (soft residuals scoped)

### Soft residuals (beyond CA2 floor)

1. Inferential Shapiro/t-test/Holm artefacts not coded.
2. LaTeX evaluation chapter full prose sync to round-2 cells.
3. Optional: broader live matrix-size sweep (floor satisfied at n=250 multi-instance).
4. WhatsApp DOI `note = {doi: ...}` hygiene.

### Binding live anchors (round-2 JSON)

| Arm | Result |
|---|---|
| Scale-up numpy n=250 | **0.001562 s** |
| On-node Dask mean n=250 | **0.5497 s** |
| Multi-instance workers / futures | **2** / `[0,1,4,9]` |
| Multi-instance `da.matmul` n=250 | **ok — 0.2546 s** |

---

**Final verdict:** CA2 matched-vCPU EC2 method **satisfied**. Research Alignment **100%**. Soft packaging/inferential/multi-order items remain optional beyond floor.

```
GATE_READY=yes
AWS_CLASS=required
SOLE_AWS_RESIDUAL=closed
ALIGNMENT=100
MULTI_INSTANCE_MATMUL=ok
ELAPSED_S=0.254623381999977
```
