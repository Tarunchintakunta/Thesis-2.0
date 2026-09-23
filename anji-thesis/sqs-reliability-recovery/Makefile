# Shortcuts. Everything defaults to DRY_RUN=1 (local simulator, free).
PY     ?= .venv/bin/python
STACK  ?= sqs-rr-dev
export DRY_RUN ?= 1

.PHONY: help setup test lint validate build deploy destroy cost guard pilot baseline arms \
        campaigns burst experiments gates clean aws-verify localsim-extra

help:
	@echo "setup | test | lint | validate | pilot | baseline | arms | campaigns | burst"
	@echo "experiments | gates | localsim-extra"
	@echo "deploy | destroy | cost | guard   (live AWS helpers)"

setup:
	scripts/scaffold.sh

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests scripts

validate:
	.venv/bin/cfn-lint template.yaml

build:
	sam build

deploy:
	scripts/deploy.sh

destroy:
	scripts/destroy.sh $(STACK)

cost:
	$(PY) scripts/estimate_cost.py --config configs/fault_campaigns.yaml

guard:
	$(PY) scripts/assert_free_tier_guard.py --config configs/pilot.yaml

pilot:
	scripts/run_pilot.sh

baseline:
	scripts/run_baseline.sh

arms:
	$(PY) -m src.control.experiment_runner --config configs/arms.yaml --out results/arms

campaigns:
	scripts/run_fault_campaign.sh --all

burst:
	scripts/run_fault_campaign.sh --load burst --subset configs/key_cells.yaml

experiments: pilot baseline arms campaigns burst

localsim-extra:
	$(PY) -m src.control.experiment_runner --config configs/live_key_cells_n3.yaml --out results/localsim/key_cells_n3
	$(PY) -m src.control.experiment_runner --config configs/live_key_cells_concurrency_sensitivity.yaml --out results/localsim/key_cells_concurrency
	$(PY) scripts/summarize_key_cells.py \
		--in results/localsim/key_cells_n3 \
		--in results/localsim/key_cells_concurrency \
		--out results/localsim/localsim_key_cells_summary.json \
		--csv results/localsim/localsim_key_cells_summary.csv \
		--note "localsim only; not live AWS" \
		--note "n=3 confirmatory on the same 4 lite cells as configs/live_key_cells.yaml"

gates: test validate
	@echo "gates passed"

clean:
	rm -rf .aws-sam .pytest_cache results/raw
