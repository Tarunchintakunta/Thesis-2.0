# Yashaswini Penumarthi (24262404) - serverless-fault-localisation
PY ?= .venv/bin/python
RC ?= .venv-rcaeval/bin/python
STACK ?= faultlab
RUN ?= data/runs/live

.PHONY: setup test lint cfn-lint check-bib sim budget rcaeval-data rcaeval-venv leg2-rules leg2-baselines leg2 \
	build deploy seed calibration steady peak collect rig destroy aws-verify

setup:
	python3.12 -m venv .venv
	$(PY) -m pip install -r requirements-dev.txt

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check detector eval baseline_runner injector workloads scripts src sim tests

cfn-lint:
	.venv/bin/cfn-lint template.yaml

check-bib:
	$(PY) scripts/check_bib.py --offline

# functional check of the rig pipeline on simulated telemetry (NOT AWS data)
sim:
	$(PY) -m eval.rig --source sim --out results/sim --figures figures/sim

budget:
	$(PY) scripts/budget_estimate.py

# ---- leg 2: RCAEval, offline ----
rcaeval-data:
	$(PY) -m baseline_runner.rcaeval_data --dataset RE2-OB --out data/rcaeval

rcaeval-venv:
	python3.12 -m venv .venv-rcaeval
	$(RC) -m pip install -r baseline_runner/requirements-rcaeval.txt

leg2-rules:
	$(PY) -m baseline_runner.rule_arm --data data/rcaeval --out results/rcaeval/raw/rules

leg2-baselines:
	$(RC) -m baseline_runner.run_baselines --data data/rcaeval --methods baro,circa,tracerca --out results/rcaeval/raw
	$(RC) -m baseline_runner.run_baselines --data data/rcaeval --methods causalrca --pattern 're2ob_*_1' --out results/rcaeval/raw

leg2: leg2-rules leg2-baselines
	$(PY) -m eval.leg2 --raw results/rcaeval/raw --out results/rcaeval --figures figures/rcaeval

# ---- live AWS (own account; see docs/CONFIGURATION_MANUAL.md) ----
build:
	sam build

deploy: build
	sam deploy --stack-name $(STACK) --capabilities CAPABILITY_IAM --resolve-s3

calibration steady peak:
	$(PY) scripts/campaign.py --phase $@ --url "$(API_URL)" --run $(RUN) --stack $(STACK)

collect:
	$(PY) scripts/collect_telemetry.py --run $(RUN) --stack $(STACK)

rig:
	$(PY) -m eval.rig --source live --run $(RUN) --out results/live --figures figures/live

destroy:
	sam delete --stack-name $(STACK)

aws-verify:
	@bash ../../scripts/aws-verify/yashaswini-serverless.sh
