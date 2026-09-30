# Physics-Informed HVAC Energy Prediction under Incomplete Sensor Data

MSc in Artificial Intelligence research project, National College of Ireland.
Sathish Kumar Konda (25190890).

The project tests whether a physics-informed, mask-aware recurrent network predicts hourly HVAC
energy of LBNL Building 59 more accurately than conventional models when building sensors fail.
The principal baseline is the Bayesian neural network of Mahajan et al. (2024,
*Sustainability* 16(22) 9943, doi:10.3390/su16229943), which uses the same building, target and
test window (July-December 2020) but assumes complete, forward-filled data.

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
