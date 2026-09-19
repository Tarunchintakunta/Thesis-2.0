# Cold-start study - common commands. MODE=mock (default) or MODE=live.
#   make test            unit + integration tests
#   make package gate    build the six packages, check every digest is the same
#   make mock-all        whole pipeline on synthetic data (regenerates the committed mock outputs)
#   make MODE=live campaign pipeline   the real thing (student's own AWS account, see reports/configuration_manual.md)
PY ?= .venv/bin/python
MODE ?= mock
RUNTIMES ?= python nodejs java
RAW = data/raw/$(MODE)
PROC = data/processed/$(MODE)
FIG = figures/$(MODE)
TAB = reports/paper/tables/$(MODE)
PILOT = data/pilot/$(MODE)

.PHONY: test lint package gate bench campaign pipeline pilot mock-all proxy-analysis aws-verify

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests scripts

package:
	PY=$(PY) bash scripts/package_all.sh $(RUNTIMES)

gate:
	$(PY) scripts/check_digests.py

bench:
	$(PY) scripts/local_init_bench.py --reps 30 --out data/proxy/local

proxy-analysis:
	$(PY) scripts/analyse_proxy.py --in data/proxy/github --out figures/proxy reports/paper/tables/proxy

campaign:
	DATA_MODE=$(MODE) $(PY) scripts/invoke_steady.py --out $(RAW)
	DATA_MODE=$(MODE) $(PY) scripts/invoke_idle.py --out $(RAW)
	DATA_MODE=$(MODE) $(PY) scripts/invoke_burst.py --out $(RAW)

pipeline:
	DATA_MODE=$(MODE) $(PY) scripts/collect_logs.py --runs $(RAW)
	$(PY) scripts/parse_report_metrics.py --in $(RAW) --out $(PROC)/metrics.csv
	$(PY) scripts/cost_model.py --in $(PROC)/metrics.csv --out $(PROC)/costs.csv
	$(PY) scripts/analyse.py --in $(PROC) --out $(FIG) $(TAB)

pilot:
	DATA_MODE=$(MODE) $(PY) scripts/invoke_idle.py --config configs/pilot.yaml --out $(PILOT)/raw
	DATA_MODE=$(MODE) $(PY) scripts/collect_logs.py --runs $(PILOT)/raw
	$(PY) scripts/parse_report_metrics.py --in $(PILOT)/raw --out $(PILOT)/metrics.csv
	$(PY) scripts/pilot_power.py --in $(PILOT) --out $(PILOT)/pilot_power.md

mock-all:
	rm -rf data/raw/mock data/pilot/mock/raw
	$(MAKE) MODE=mock campaign pipeline pilot

aws-verify:
	@bash ../../scripts/aws-verify/chaitanya-lambda.sh
