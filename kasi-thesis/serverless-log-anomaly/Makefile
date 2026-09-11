# Shortcuts - everything runs locally on the Lambda runtime emulator by default.
PY ?= .venv/bin/python
export PYTHONPATH := src

.PHONY: help setup fetch test lint validate smoke generate run report all bundle \
        localstack-up localstack-down deploy-local clean

help:
	@echo "setup | fetch | test | lint | validate | smoke | generate | run | report | all | bundle"
	@echo "localstack-up | deploy-local | localstack-down   (optional live path)"

setup:
	scripts/00_bootstrap.sh

fetch:
	scripts/fetch_loghub.sh

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests infra

validate:
	.venv/bin/cfn-lint infra/lambda_app/template.yaml

# seconds - checks the whole chain on a tiny config (not results)
smoke:
	$(PY) -m logad.pipeline --config configs/smoke.yaml --out results_smoke
	$(PY) -m logad.eval.report --results results_smoke

generate:
	scripts/02_generate_traffic.sh

run:
	scripts/04_train_eval.sh

report:
	scripts/05_stats_plots.sh

all: run report

bundle:
	scripts/06_bundle_results.sh

localstack-up:
	docker compose -f infra/localstack/docker-compose.yml up -d

localstack-down:
	docker compose -f infra/localstack/docker-compose.yml down

deploy-local:
	scripts/01_deploy_app.sh

clean:
	rm -rf results_smoke data/interim data/processed .pytest_cache dist
