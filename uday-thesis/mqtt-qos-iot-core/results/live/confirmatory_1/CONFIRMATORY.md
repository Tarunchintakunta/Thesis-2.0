# Uday confirmatory_1 (lite pooled Holm)

**Generated:** `2026-09-23T07:56:39.526510+00:00`  
**Sources:** `final_1` + `final_2` LIVE_EVIDENCE (destroy_confirmed each).  
**Not:** formal 5-rep / ~600k-msg design; **final_3 absent** on this branch.

## Same-metrics vs Shvaika gap

| Metric | Shvaika (2025) | Ours (live lite) |
|--------|----------------|------------------|
| Loss under disconnect | deferred / future work | QoS0 mean loss 0.415; QoS1 **0.0** |
| Broker | self-hosted TBMQ | **AWS IoT Core** managed |
| Latency / dup | steady-load framing | measured under disconnect |

## QoS0 loss by disconnect (pooled)

| disconnect_s | mean loss |
|-------------:|----------:|
| 0 | 0.0000 |
| 15 | 0.3000 |
| 60 | 0.6800 |
| 300 | 0.6800 |

## Soft N — Holm d300 > d60

**FAIL / retained null.** Under lite schedule, QoS0 d60 loss ≡ d300 loss (**0.68**).
Two-proportion tests cannot support d300>d60. Dated WONTFIX — not a silent park.

- `steady`: d60=0.68 d300=0.68 z=0.0 p=0.5 note=None
- `bursty`: d60=0.68 d300=0.68 z=0.0 p=0.5 note=None

## Holm family (pooled lite)

n_tests=17; adjustment=holm-bonferroni. See `holm_stats.json`.

Primary directional: QoS0 loss > QoS1 at disconnect cells where SE allows; d0 often degenerate.

