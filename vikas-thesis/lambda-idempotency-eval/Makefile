# Vikas Reddy Amanagantti - lambda-idempotency-eval
PY ?= .venv/bin/python
export PYTHONPATH := src:.

LIVE := data/runs/live
MOTO := data/runs/moto
WORKERS ?= 16
# campaign N from the pilot rule (results/live/pilot_choice.json)
N ?= $(shell $(PY) -c "import json;print(json.load(open('results/live/pilot_choice.json'))['N'])" 2>/dev/null)

.PHONY: setup test lint check-bib tf-check budget build deploy pilot pilot-size campaign sensitivity cloudwatch \
	analyse destroy functional clean

setup:
	python3.12 -m venv .venv
	$(PY) -m pip install -r requirements-dev.txt

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check src tests scripts analysis

check-bib:
	$(PY) scripts/check_bib.py --offline

tf-check:
	cd infra && terraform fmt -check -recursive && terraform init -backend=false -input=false && terraform validate

budget:
	$(PY) scripts/budget_estimate.py $(if $(N),--n $(N))

build:
	PY=$(PY) scripts/build_lambda.sh

# ---- live AWS (needs credentials; spend is bounded by config/experiment.yaml) ----
deploy: build
	cd infra && terraform init -input=false && terraform apply

pilot:
	$(PY) -m driver.run --phase pilot --out $(LIVE)/pilot
	$(PY) -m driver.streams --out $(LIVE)/pilot

pilot-size:
	$(PY) analysis/pilot_size.py --run $(LIVE)/pilot --out results/live

campaign:
	@test -n "$(N)" || (echo "run make pilot-size first (or pass N=...)"; exit 1)
	$(PY) -m driver.run --phase campaign --n $(N) --workers $(WORKERS) --out $(LIVE)/campaign
	$(PY) -m driver.streams --out $(LIVE)/campaign

sensitivity:
	$(PY) -m driver.run --phase sensitivity --workers $(WORKERS) --out $(LIVE)/sensitivity
	$(PY) -m driver.streams --out $(LIVE)/sensitivity

cloudwatch:
	$(PY) scripts/collect_cloudwatch.py --run $(LIVE)/campaign

analyse:
	$(PY) analysis/analyse.py --campaign $(LIVE)/campaign --sensitivity $(LIVE)/sensitivity \
		--out results/live --figures figures/live

destroy:
	cd infra && terraform destroy

# ---- functional check on moto: no AWS, NOT a measurement ----
functional:
	rm -rf $(MOTO)
	$(PY) -m driver.run --backend local --moto --phase pilot --out $(MOTO)/pilot
	$(PY) analysis/pilot_size.py --run $(MOTO)/pilot --out results/moto
	$(PY) -m driver.run --backend local --moto --phase campaign --n 30 --out $(MOTO)/campaign
	$(PY) -m driver.run --backend local --moto --phase sensitivity --n 20 --out $(MOTO)/sensitivity
	$(PY) analysis/analyse.py --campaign $(MOTO)/campaign --sensitivity $(MOTO)/sensitivity \
		--out results/moto --figures figures/moto

clean:
	rm -rf build $(MOTO) data/runs/local
