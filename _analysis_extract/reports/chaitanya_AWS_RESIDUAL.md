# Chaitanya alignment residual (AWS-goal)

**Updated:** 2026-09-20 (lite Holm family + bytecode drop)  
**Alignment:** **~97/100** (was ~95% after live Init+H3+H4 lite)  
**Status:** **NOT COMPLETE** (literal 100% still open)

## Compact
`RQ9 Obj12 Method13 Impl13 Exp11 Metrics12 Evidence12 Claims10 Rubric6` → **~97/100**

## Live AWS inventory (evidence-only)

Stack: `coldstart-study` (eu-west-1, arm64). **Still deployed** (shared ConcurrentExecutions=10; do not destroy while Vikas/others need headroom coordination).

| Artifact | Present |
|----------|---------|
| Raw Init | yes — `data/raw/live/live_{python,nodejs}_init/`, `data/raw/live_java/live_java_init/` |
| Raw H4 | yes — `data/raw/live/live_python_memory/` |
| Raw H3 | yes — `data/raw/live_h3/warming/` (`run_info` complete; 20 measure) |
| Processed | yes — `data/processed/live/{metrics,costs,init_summary_by_cell,h4_*,h3_*,roi_*,adopt_*,live_summary}.csv/json` |
| H3 config | yes — `configs/live_h3_warming.yaml` (recreated to match `run_info`: gap 180 s, block 0.5 h, block 10) |

### Measured Init @1024 MB (lite $n=12$ colds/cell)

| Runtime | Variant | n | mean | p50 | p95 |
|---------|---------|--:|-----:|----:|----:|
| python | default | 12 | 3177.9 | 3356.0 | 3527.1 |
| python | optimised | 12 | 88.9 | 88.3 | 121.9 |
| nodejs | default | 12 | 991.7 | 1000.8 | 1146.0 |
| nodejs | optimised | 12 | 135.1 | 140.5 | 146.4 |
| java | default | 12 | 688.6 | 687.3 | 771.9 |
| java | optimised | 12 | 360.9 | 333.4 | 427.8 |

Phase means (all colds in phase): python default+optimised n=24 mean≈**1633**; nodejs n=24 mean≈**563**; java n=24 mean≈**525**.  
H4-lite python optimised: n=60 colds, mean≈**81.5** ms across 128–3008 MB.

**Bytecode:** all 24 `python-bytecode` invocations `function_error=Unhandled` — excluded from Init tables.

### H3-lite (complete)

| Arm | n | colds | cold rate |
|-----|--:|------:|----------:|
| on (warm-target) | 10 | 0 | 0.00 |
| off (warm-control) | 10 | 2 | 0.20 |

Drop 0.20 (directional; $n$ small). Control cold Init median among 2 colds: 84.66 ms.

### ROI / ADOPT-lite (measured billed ms only)

Point estimates vs `analysis_plan.yaml` practical thresholds (**not** Holm-confirmed):

| Control | Scope | Init/freq Δ | Δ$/1k | band_lite |
|---------|-------|------------:|------:|-----------|
| Prune package | python def→opt | p50 −3267.6 ms | −0.041 | ADOPT_CANDIDATE_lite |
| Prune package | nodejs def→opt | p50 −860.3 ms | −0.012 | ADOPT_CANDIDATE_lite |
| Prune package | java def→opt | p50 −353.9 ms | −0.004 | ADOPT_CANDIDATE_lite |
| Raise memory | py opt 128→1024 | p50 −14.8 ms | +0.0008 | HOLD_lite |
| Warming | rate(5 min) | cold-rate −0.20 | ≈+4e-5 | ADOPT_CANDIDATE_lite |

Measured Init+campaign list-price cost (processed costs sum, Init rounds): ≈ **$0.0013** (+ H3 ≈$0.00002).

## Top blockers to 100%
1. **Soft:** confirmatory $n$ (power plan `min_n_per_cell: 30`). Lite Holm **ran** (H1/H2 reject; H3 fail to reject, 3 blocks).
2. **Closed:** `python-bytecode` formally dropped (Unhandled on live; ASSUMPTIONS W7)
3. **Soft:** longer H3 (pre-registered 4 h / gap 360) if depth required beyond lite
4. Destroy stack only after shared-account campaigns finish

**Hard AWS residual (first live Init Duration):** **closed** at lite depth. Remaining gaps are soft confirmatory / depth / bytecode hygiene.

```
GATE_READY=yes
LIVE_INIT_LITE=yes
LIVE_H3_LITE=yes
LIVE_H4_LITE=yes
ROI_LITE_MEASURED=yes
LIVE_CONFIRMATORY=lite_holm_underpowered
AWS_CLASS=required
SOLE_AWS_RESIDUAL=soft
DESTROY_AFTER_ROUND=deferred
```

Evidence: `STATUS.md`, `data/processed/live/live_summary.json`, `latex_report/text/evaluation.tex`, `configs/live_h3_warming.yaml`.
