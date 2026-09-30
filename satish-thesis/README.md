# Physics-Informed HVAC Energy Prediction under Incomplete Sensor Data

MSc in Artificial Intelligence research project, National College of Ireland.
Sathish Kumar Konda (25190890).

The project tests whether a physics-informed, mask-aware recurrent network predicts hourly HVAC
energy of LBNL Building 59 more accurately than conventional models when building sensors fail.
The principal baseline is the Bayesian neural network of Mahajan et al. (2024,
*Sustainability* 16(22) 9943, doi:10.3390/su16229943), which uses the same building, target and
test window (July-December 2020) but assumes complete, forward-filled data.

## Headline results

Estimation task, test set July-December 2020, complete sensors (mean of five seeds):

| Model | RMSE (kWh) | MAE (kWh) | MAPE |
|---|---|---|---|
| BNN, published (Mahajan et al., 2024) | 9.65 | 7.06 | 0.350 |
| MC-LSTM, published | 11.86 | 8.21 | 0.450 |
| BNN, re-implemented with the paper's inputs | 12.11 | 9.51 | 0.405 |
| **PI-GRU (proposed)** | **9.01** | **5.70** | **0.216** |
| GRU-aux (PI-GRU without physics term) | 8.91 | 5.73 | 0.215 |
| XGBoost (same mask-aware features) | 7.97 | 6.03 | 0.291 |

- The PI-GRU beats the published baseline on every metric and is 20% more accurate than the
  re-implemented baseline when 40% of readings are lost to contiguous outages.
- Random (MCAR) loss barely matters; contiguous multi-sensor outages raise RMSE by 15-23%.
- Mask and time-since-last features are the most effective protection (10% lower RMSE at 40% outages).
- The physics term itself is neutral for accuracy and lowers the heat-balance residual by 10% on
  complete data; the envelope time constant is not identifiable from this building's data.

## Layout

| Path | Content |
|---|---|
| `src/prepare_data.py` | Raw Building 59 files to the hourly table |
| `src/masking.py` | MCAR and block sensor outages, causal imputers, mask features |
| `src/models.py` | PI-GRU, RC physics term, LSTM/GRU, Bayesian baseline, training loop |
| `src/experiment.py` | Tuning, five-seed training, sensor-loss grid, sensitivity runs |
| `src/analysis.py` | Statistics, tables and figures |
| `tests/` | Unit tests (leakage, masking, physics, metrics, split) |
| `notebooks/physics_informed_hvac.ipynb` | End-to-end notebook (Colab, Jupyter, macOS, Windows) |
| `data/bldg59_hourly.csv.gz` | Bundled hourly table (no Kaggle token needed) |
| `results/`, `figures/` | All outputs behind the report |
| `report/thesis.pdf` | Final report |
| `config_manual/config_manual.pdf` | Configuration manual |

## Reproduce

```bash
pip install -r requirements.txt
python -m pytest tests -q
python src/experiment.py
python src/analysis.py
cd report && latexmk -pdf thesis.tex
```

`python src/experiment.py --quick` is a two-minute smoke run. The device is chosen
automatically (CUDA, then Apple MPS, then CPU). To rebuild the hourly table from the raw files,
run `bash scripts/download_data.sh` (needs a Kaggle token) and `python src/prepare_data.py`.
See the configuration manual for details.
