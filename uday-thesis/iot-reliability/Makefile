# Shortcuts. Everything defaults to DRY_RUN=1 (local simulator, free).
PY     ?= .venv/bin/python
STACK  ?= sqs-rr-dev
export DRY_RUN ?= 1

.PHONY: help setup test lint validate build deploy destroy cost guard pilot baseline arms \
        campaigns burst experiments stats figures self-check gates clean

help:
	@echo "setup | test | lint | validate | pilot | baseline | arms | campaigns | burst"
	@echo "experiments (all of the above runs) | stats | figures | gates"
	@echo "deploy | destroy | cost | guard   (live AWS helpers)"

setup:
	scripts/scaffold.sh

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests analysis scripts

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

stats:
	$(PY) analysis/stats_tests.py --in results --hypotheses H1,H2,H3 --alpha 0.05 --holm

figures:
	$(PY) analysis/plot_results.py --in results --out results/figures

self-check:
	$(PY) analysis/stats_tests.py --self-check

# Phase 8 quality gates from the master prompt
gates: test validate self-check
	test -f docs/CONFIGURATION_MANUAL.md
	test -f results/figures/loss_vs_visibility.png
	@echo "all quality gates passed"

clean:
	rm -rf .aws-sam .pytest_cache results/raw
