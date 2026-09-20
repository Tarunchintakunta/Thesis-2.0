# Live processed metrics (CA2)

**data_mode:** `live`  
**stack:** `coldstart-study` (eu-west-1, arm64)  
**lite sample:** `reps=12` intended-cold measure calls per cell (disclose as lite).

## Inputs
- `data/raw/live/live_python_init/`
- `data/raw/live/live_nodejs_init/`
- `data/raw/live/live_python_memory/` (H4-lite)
- `data/raw/live_java/live_java_init/`
- CloudWatch `logs_collected/events.jsonl` (joined by request id)

## Outputs
- `metrics.csv` / `costs.csv` — from `parse_report_metrics.py` + `cost_model.py` (Init + H4)
- `init_summary_by_cell.csv` — Init Duration stats per runtime×variant @1024 MB
- `h4_python_memory_summary.csv` — Init vs memory for python optimised
- `h3_metrics.csv` / `h3_costs.csv` / `h3_warming_summary.csv` / `h3_summary.json` — H3-lite fold
- `roi_lite_by_variant.csv` — measured mean cost / cost-per-1k (all-cold)
- `adopt_lite_matrix.csv` — point-estimate bands vs `analysis_plan.yaml` practical thresholds (**not** Holm-confirmed ADOPT)
- `live_summary.json` — inventory + notes

## H3-lite
- Raw: `data/raw/live_h3/` (config: `configs/live_h3_warming.yaml`, matches `run_info.json`)
- Measure: n=10/arm; cold rate on=0.00, off=0.20

## Known exclusions
- `python-bytecode`: all 24 invocations `function_error=Unhandled`; excluded from Init summary.
