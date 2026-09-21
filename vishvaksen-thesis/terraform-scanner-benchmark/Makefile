.PHONY: help generate test scan evaluate all pin

help:
	@echo "generate     - write 240 labelled Terraform modules"
	@echo "test         - pytest (corpus invariants + metrics + OPA check)"
	@echo "scan         - label-oracle checklist + checkov + tfsec + opa (no apply)"
	@echo "evaluate     - per-category P/R/F1/FN + time + LOC"
	@echo "all          - generate, test, scan, evaluate"
	@echo "pin          - record tool versions"

generate:
	python3 scripts/generate_corpus.py

test:
	python3 -m pytest tests/ -q --tb=short

scan:
	python3 scripts/run_checklist.py
	python3 scripts/run_checkov.py
	python3 scripts/run_tfsec.py
	python3 scripts/run_opa.py

evaluate:
	python3 scripts/evaluate.py

pin:
	python3 scripts/pin_tools.py

all:
	python3 scripts/run_all.py
