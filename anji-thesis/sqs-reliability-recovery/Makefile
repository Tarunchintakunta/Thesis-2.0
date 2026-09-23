# Live AWS experiment shortcuts (no local simulator).
PY     ?= .venv/bin/python
STACK  ?= sqs-rr-dev

.PHONY: help setup test lint validate build deploy destroy cost pilot baseline arms \
        campaigns burst experiments gates clean

help:
	@echo "setup | test | lint | validate | pilot | baseline | arms | campaigns | burst"
	@echo "experiments | gates"
	@echo "deploy | destroy | cost   (live AWS helpers; runners require --live)"

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

pilot:
	scripts/run_pilot.sh

baseline:
	scripts/run_baseline.sh

arms:
	$(PY) -m src.control.experiment_runner --live --config configs/arms.yaml --out results/arms

campaigns:
	scripts/run_fault_campaign.sh --all

burst:
	scripts/run_fault_campaign.sh --load burst --subset configs/key_cells.yaml

experiments: pilot baseline arms campaigns burst

gates: test validate
	@echo "gates passed"

clean:
	rm -rf .aws-sam .pytest_cache results/raw
