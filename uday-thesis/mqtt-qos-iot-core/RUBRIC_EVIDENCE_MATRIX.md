# Rubric evidence matrix — Uday (mqtt-qos-iot-core)

**Driver:** `/RUBRIC_70_TO_100_STRATEGY.md`  
**Artefact:** `uday-thesis/mqtt-qos-iot-core/`  
**CA2:** 100% | **INITIAL_EVAL_PASS:** yes | **Final-3:** in flight (final_1 done; final_2/3 running)  
**Rubric:** partial → fold after final-3  

| Rubric requirement | Where evidence exists | Concrete evidence | Gap to 80+/90+ |
|--------------------|----------------------|-------------------|----------------|
| Objectives fully achieved | STATUS; LIVE_EVIDENCE | 16-cell lite QoS×disconnect×rate | Map each Obj → cell metric after final-3 |
| Critical literature review | baseline_papers; STATUS | vs Shvaika / managed IoT gap | Critique matrix in report |
| Alternatives considered | DESIGN_RATIONALE; configs | lite vs formal 600k; smoke vs lite | Decision table: self-host broker vs IoT Core |
| Methodology justified | experiment.yaml; STATUS | Factorial 2×4×2; Free-Tier guard | Justify interval_s=1.0 vs formal 5s |
| Rigorous implementation | terraform; run_live; destroy_stack | apply→16 cells→destroy 43 resources | Complete final-3 packs |
| Rigorous evaluation | LIVE_EVIDENCE; STATUS neg | QoS1 loss≈0; QoS0 loss rises with disconnect | Stats across final-3; latency for QoS1 cost |
| Synthesis of data | cells loss_rate | d60≡d300 under lite wall-clock (**neg**) | Explain cut/schedule interaction |
| Relevant theory | STATUS vs Shvaika | Managed + disconnect gap | Agree/disagree paragraphs |
| Insightful conclusions | STATUS limitations | Reliability paid in latency/backlog | “So what” for IoT practitioners |
| Academic implications | DESIGN_RATIONALE | Lite factorial closes method floor | Contribution vs TBMQ-style work |
| Practitioner implications | STATUS | Prefer QoS1 when disconnects matter | Config Manual takeaway |
| Validity | STATUS; honesty fields | Live IoT Core path | Single region; synthetic schedule |
| Generalisability | DESIGN_RATIONALE | Formal 600k beyond floor | Multi-month staging note |
| Limitations | STATUS | d60≡d300; n=1; lite wall-clock | Keep after final-3 |
| Reproducibility | README; destroy_stack; make live-lite | enable_apply + device_count=5 | Exact final script `run_final_lite.sh` |
| Viva evidence | STATUS neg + gates | Why not formal 600k; why d60≡d300 | Defend Free-Tier envelope |

## Objective → test → result (update after final-3)

| Objective | Test / metric | Result location | Achieved? |
|-----------|---------------|-----------------|-----------|
| QoS0 vs QoS1 under disconnect | loss_rate by qos×disconnect_s | `results/live/final_*/LIVE_EVIDENCE.json` | pending final-3 |
| Rate mode steady vs bursty | loss / latency by rate_mode | same | pending |
| Free-Tier-safe live method | destroy_confirmed + 16 cells | final_1 done | **yes** (f1) |

## Design decisions (Artefact)

| Decision | Alt 1 | Alt 2 | Selected | Reason |
|----------|-------|-------|----------|--------|
| Broker | Self-host MQTT | AWS IoT Core | IoT Core | CA2 cloud-managed scope |
| Scale | Formal 600k msgs | Lite ~6k | Lite | Free-Tier; formal beyond-CA2 |
| Factors | QoS only | QoS×disconnect×rate | Full factorial lite | Matches commitments |

## Eval checklist

- [x] Descriptive cells (f1)  
- [ ] Factor + interaction across final-3  
- [ ] Stats / stability across 3 packs  
- [x] Negative: d60≡d300; QoS1 cost  
- [ ] Lit comparison paragraphs in report  
- [ ] Practitioner implications box  
- [x] Limitations disclosed  
- [ ] RQ answered with final-3 baseline  

**Scoreboard Rubric70:** partial (until final-3 + fold)  
**Last updated:** 2026-09-22
