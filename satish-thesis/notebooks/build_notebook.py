"""Writes notebooks/physics_informed_hvac.ipynb (run: python notebooks/build_notebook.py)."""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
    md("""# Physics-Informed HVAC Energy Prediction under Incomplete Sensor Data

Sathish Kumar Konda (25190890), MSc in Artificial Intelligence, National College of Ireland.

This notebook reproduces the full study on the LBNL Building 59 dataset (Luo et al., 2022):

1. environment set-up (Google Colab, Jupyter, macOS or Windows; CUDA, Apple MPS or CPU),
2. data loading and profiling,
3. unit tests,
4. the experiment (baseline re-implementation, proposed physics-informed GRU, ablations, five seeds, controlled sensor loss),
5. statistics, tables and figures used in the report.

The principal baseline is Mahajan et al. (2024), *Sustainability* 16(22), 9943, which predicts hourly HVAC energy of the same building on the same test window (July-December 2020) from complete, forward-filled data.

`RUN_FULL = False` reuses the stored results in `results/` and only runs a short smoke experiment. Set it to `True` to re-run every experiment (about 40-60 minutes on a laptop GPU or 8 CPU cores)."""),
    code("""RUN_FULL = False"""),
    md("## 1. Environment"),
    code("""import importlib.util
import os
import pathlib
import subprocess
import sys

REPO = "https://github.com/Tarunchintakunta/Thesis-2.0.git"


def find_root():
    here = pathlib.Path.cwd().resolve()
    for cand in (here, here.parent, here / "satish-thesis", here / "Thesis-2.0" / "satish-thesis"):
        if (cand / "src" / "experiment.py").exists():
            return cand
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO, "Thesis-2.0"], check=True)
    subprocess.run(["git", "-C", "Thesis-2.0", "sparse-checkout", "set", "satish-thesis"], check=True)
    return (here / "Thesis-2.0" / "satish-thesis").resolve()


ROOT = find_root()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))

needed = {"xgboost": "xgboost", "torch": "torch", "sklearn": "scikit-learn", "scipy": "scipy",
          "matplotlib": "matplotlib", "pandas": "pandas", "pytest": "pytest"}
missing = [pkg for mod, pkg in needed.items() if importlib.util.find_spec(mod) is None]
if missing:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], check=True)
print("project root:", ROOT)
print("python:", sys.version.split()[0])"""),
    code("""def run(*args):
    \"\"\"Run a project script in a fresh interpreter and stream its output.\"\"\"
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONWARNINGS": "ignore",
           "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), os.environ.get("PYTHONPATH", "")])}
    proc = subprocess.Popen([sys.executable, *args], cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    for line in proc.stdout:
        print(line, end="")
    if proc.wait() != 0:
        raise RuntimeError(f"{' '.join(args)} failed with exit code {proc.returncode}")


run("-c", "import torch; from models import pick_device; print('torch', torch.__version__, '| device:', pick_device())")"""),
    md("""## 2. Data

`data/bldg59_hourly.csv.gz` is the hourly table built by `src/prepare_data.py` from the raw Building 59 files. To rebuild it from the raw data, run `scripts/download_data.sh` (needs a Kaggle token) and then `python src/prepare_data.py`."""),
    code("""import json

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import Image, display

from experiment import PERIODS, load_hourly

df = load_hourly()
print(df.shape, df.index.min(), "to", df.index.max())
print("splits:", PERIODS)
display(pd.read_csv("results/data_dictionary.csv"))
display(df.describe().T.round(2))"""),
    code("""profile = json.loads(pathlib.Path("results/data_profile.json").read_text(encoding="utf-8"))
pd.DataFrame({"natural gaps (%)": profile["raw_missing_pct"],
              "correlation with HVAC": profile["corr_with_hvac"]}).round(3)"""),
    md("## 3. Unit tests"),
    code("""run("-m", "pytest", "tests", "-q", "--color=no", "-p", "no:cacheprovider")"""),
    md("""## 4. Experiment

`src/experiment.py` runs two tasks. **estimate** is the primary task and follows the baseline: hourly HVAC energy is predicted from building and weather sensors without the HVAC meter history. **forecast** is supplementary: the next hour is predicted with the meter history as an extra input. The tree family (XGBoost and naive baselines) and the neural family run in separate processes."""),
    code("""run("src/experiment.py", "--quick")

have_results = all((ROOT / "results" / f"metrics_{t}_{f}.csv").exists()
                   for t in ("estimate", "forecast") for f in ("tree", "nn"))
if RUN_FULL or not have_results:
    run("src/experiment.py")
else:
    print("Stored full results found in results/. Set RUN_FULL = True to recompute them.")"""),
    md("## 5. Analysis"),
    code("""run("src/analysis.py")
TAB = ROOT / "results" / "tables"


def show(name):
    display(pd.read_csv(TAB / name))


def fig(name):
    display(Image(filename=str(ROOT / "figures" / name)))"""),
    md("### 5.1 Comparison with the baseline paper (complete data)"),
    code("""show("baseline_comparison.csv")
fig("baseline_comparison.png")"""),
    md("### 5.2 Robustness to sensor loss (estimation task)"),
    code("""show("robustness_estimate.csv")
fig("robustness_estimate.png")
fig("degradation_estimate.png")"""),
    md("### 5.3 Statistical tests: PI-GRU against the best conventional model and the matched ablation"),
    code("""show("significance_estimate.csv")"""),
    md("### 5.4 Physical consistency and learned thermal parameters"),
    code("""show("physics_consistency_estimate.csv")
show("physics_coefs_estimate.csv")
fig("physics_coefs_estimate.png")
fig("lambda_sensitivity_estimate.png")"""),
    md("### 5.5 Operating strata, imputation choice and cost"),
    code("""show("strata_estimate.csv")
show("imputation_sensitivity.csv")
show("cost_estimate.csv")"""),
    md("### 5.6 Example week"),
    code("""fig("trace_estimate.png")"""),
    md("### 5.7 Supplementary: one-hour-ahead forecasting with meter history"),
    code("""show("robustness_forecast.csv")
show("significance_forecast.csv")
fig("robustness_forecast.png")"""),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3"},
                                                 "language_info": {"name": "python"}})
out = Path(__file__).with_name("physics_informed_hvac.ipynb")
nbf.write(nb, out)
print("wrote", out)
