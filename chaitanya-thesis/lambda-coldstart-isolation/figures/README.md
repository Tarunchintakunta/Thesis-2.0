# figures/

| folder | source | status |
|---|---|---|
| `live/` | AWS campaign (`DATA_MODE=live`) | empty until the student runs the campaign |
| `mock/` | synthetic mock data | **SYNTHETIC** - every image carries a watermark; pipeline test only |
| `proxy/` | local process-start benchmark on a GitHub Actions runner | real proxy measurement, not Lambda Init Duration |
| `proxy_dev/` | same benchmark on the development laptop (Python, Node.js) | supplementary |

File names match the master prompt: `baseline_style_duration_cost.png`,
`init_by_runtime.png`, `package_size_effect.png`, `memory_effect.png`,
`warming_frequency.png`, `burst_latency.png`, `decision_matrix.png`.
