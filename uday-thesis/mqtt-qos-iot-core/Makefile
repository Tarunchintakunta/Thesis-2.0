.PHONY: test dry-run analyse terraform-validate cost guard live

test:
	python3 -m pytest tests -q

dry-run:
	python3 scripts/dry_run.py --out results/mock --scale dry_run

analyse:
	python3 scripts/analyse.py --in results/mock --out results/mock/summary

terraform-validate:
	cd terraform && terraform init -backend=false -input=false && terraform validate

cost:
	python3 scripts/estimate_cost.py --mode dry_run
	python3 scripts/estimate_cost.py --mode formal

guard:
	python3 scripts/assert_free_tier_guard.py --mode dry_run
	python3 scripts/assert_free_tier_guard.py --mode live_lite

live:
	python3 scripts/run_live.py
