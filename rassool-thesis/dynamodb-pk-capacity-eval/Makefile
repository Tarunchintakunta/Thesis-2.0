# DynamoDB partition-key x capacity-mode study - common commands.
# The live steps need the student's AWS credentials; see RUNBOOK.md.
PY ?= .venv/bin/python
RESULTS ?= results
BUCKET ?= $(shell cd iac && terraform output -raw results_bucket 2>/dev/null)

.PHONY: test lint tf-check design tfvars build deploy seed pilot run-matrix collect analyse teardown smoke prices aws-verify

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check workloads tests analysis scripts

tf-check:
	cd iac && terraform fmt -check -recursive && terraform init -backend=false -input=false >/dev/null && terraform validate

design:
	$(PY) analysis/design_checks.py

tfvars:
	$(PY) scripts/render_tfvars.py

build:
	PY=$(PY) bash scripts/build_lambda.sh

deploy: tfvars build
	cd iac && terraform init -input=false && terraform apply -var seed_mode=true

seed:
	$(PY) -m workloads.seed.seed --all
	cd iac && terraform apply -var seed_mode=false

pilot:
	$(PY) scripts/run_matrix.py --pilot --results-bucket $(BUCKET) --out results_pilot

run-matrix:
	$(PY) scripts/run_matrix.py --results-bucket $(BUCKET) --out $(RESULTS)

collect:
	$(PY) scripts/collect_metrics.py --results $(RESULTS)

analyse:
	$(PY) analysis/analyse.py --results $(RESULTS) --out report/generated

teardown:
	cd iac && terraform destroy

# in-memory fake DynamoDB, 2 blocks of the W3 and W4 cells, compressed time (about 2 minutes)
smoke:
	$(PY) scripts/run_matrix.py --backend local --moto --blocks 2 --workloads W3,W4 \
	  --rate-scale 0.05 --time-scale 0.02 --orders 2000 --lambdas 2 --out results_smoke
	$(PY) analysis/analyse.py --results results_smoke --out results_smoke/analysis

prices:
	$(PY) analysis/fetch_prices.py --region eu-west-1

aws-verify:
	@bash ../../scripts/aws-verify/rassool-dynamodb.sh
