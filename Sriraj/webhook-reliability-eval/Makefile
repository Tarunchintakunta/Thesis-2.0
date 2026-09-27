# Sriraj Gannavaram — webhook-reliability-eval
PY ?= python3
export PYTHONPATH := src:.

.PHONY: setup test pilot lint tf-check clean

setup:
	$(PY) -m pip install -r requirements.txt -q

test:
	$(PY) -m pytest -q

pilot:
	$(PY) -m sim.runner
	@echo "Wrote results/local_sim/pilot_results.json (LOCAL_SIM — not live AWS)"

lint:
	$(PY) -m compileall -q src tests scripts

tf-check:
	cd terraform/envs/dev && terraform fmt -check -recursive || true
	cd terraform/modules/webhook && terraform fmt -check || true
	@echo "Terraform stubs present; validate/apply needs terraform + AWS creds (not required for floor)"

clean:
	rm -rf .pytest_cache **/__pycache__
