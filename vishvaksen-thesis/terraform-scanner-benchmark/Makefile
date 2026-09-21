.PHONY: help generate test scan evaluate dual-review all pin

help:
	@echo "generate     - write 240 labelled Terraform modules"
	@echo "test         - pytest (corpus invariants + metrics + OPA check)"
	@echo "scan         - checklist + checkov + tfsec + opa (no apply)"
	@echo "evaluate     - per-category P/R/F1/FN + time + LOC"
	@echo "dual-review  - provisional 20% same-author subsample JSON"
	@echo "all          - generate, test, scan, evaluate, dual-review"
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

dual-review:
	python3 scripts/run_second_review.py

pin:
	python3 scripts/pin_tools.py

all:
	python3 scripts/run_all.py
	python3 scripts/run_second_review.py
