# Live AWS experiment shortcuts (Terraform only).
PY     ?= .venv/bin/python
STAGE  ?= dev

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
	cd terraform && terraform init -input=false && terraform validate

build:
	bash scripts/build_lambda_zips.sh

deploy:
	scripts/deploy.sh $(STAGE)

destroy:
	scripts/destroy.sh $(STAGE)

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
	rm -rf .pytest_cache results/raw
