# Dataset schema

Kondragunta Lakshmi Chaitanya - 25171216

## `data/processed/<mode>/metrics.csv` (and `costs.csv`)

One row per Lambda invocation. `<mode>` is `live` (measured) or `mock`
(synthetic, pipeline testing only). `costs.csv` is `metrics.csv` plus the two
cost columns at the end.

| column | meaning |
|---|---|
| seq | order inside the phase (client side) |
| phase | baseline, runtime_compare, package_size, memory, warming, burst, combined, pilot_cold, idle_probe, or `background` for REPORT lines with no client call (warmer pings) |
| data_mode | `live` or `mock` - never mixed in one analysis |
| function | logical name, e.g. `java-default`, `warm-target` (deployed as `<stack>-<name>`) |
| runtime / variant | python, nodejs, java / default, optimised |
| memory_mb | Memory Size from the REPORT line |
| role | `measure` (analysed), `follow_up` (warm call right after a cold one), `warmup` (thrown away), `prime` (idle probe set-up), `warmer_ping`, `unmatched` |
| pattern | idle, steady, sparse, burst |
| warming | on / off (warming phase arms; everything else is off) |
| intended_cold | the invoker tried to get a cold start |
| force_cold | update_env or idle - how the cold start was prepared |
| rep | block number of the interleaved randomised schedule |
| block | 20-minute block (warming phase) |
| burst_id | which burst a call belongs to |
| idle_gap_min | idle probe gap before the call |
| t_start / t_start_utc | client time the call started (epoch s / ISO) |
| request_id | Lambda request id - the join key with CloudWatch Logs |
| status / function_error / error | HTTP-style status, Lambda FunctionError, and error = either of them |
| rtt_ms | client round trip around `lambda.invoke()` |
| duration_ms / billed_ms / max_memory_used_mb | from the REPORT line |
| init_ms | `Init Duration` from the REPORT line, empty on warm calls |
| cold | True if and only if the REPORT line has an Init Duration |
| report_source | `logs` (CloudWatch), `tail` (invoke log tail) or `missing` |
| effective_billed_ms | billed time used for cost (Init added if the REPORT line does not include it, see ASSUMPTIONS M5) |
| cost_usd | cost of this call at the list price in `configs/pricing.yaml` |

`discarded_intended_colds.csv` counts intended-cold calls that came back warm
per phase / function / memory (published, never analysed as cold).

## `data/proxy/<machine>/runs.csv`

Local process-start benchmark. One row per fresh process.

| column | meaning |
|---|---|
| runtime / variant | as above |
| init_proxy_ms | process spawn -> handler loaded |
| handler_ms | one run of the fixed payload |
| process_wall_ms | whole child process seen from the parent |
| digest / items_total | output, must equal `payloads/expected_output.json` |
| ok / error | child exit status and stderr tail |
| rep / seq / warmup | block number, order, and warm-up rounds (never analysed) |

`run_info.json` next to it records the machine, tool versions, seed and the
package manifest (zip size, unzipped size, file count, sha256 per variant).
