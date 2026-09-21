.PHONY: test dry-run analyse plan-ft guard-lite guard-formal ready live live-lite live-dry destroy

test:
	cd $(CURDIR) && PYTHONPATH=src pytest -q

dry-run:
	PYTHONPATH=src python scripts/run_dry_run.py --plots

analyse:
	PYTHONPATH=src python scripts/analyse.py --plots

plan-ft:
	PYTHONPATH=src python scripts/plan_free_tier.py

guard-lite:
	PYTHONPATH=src python scripts/assert_free_tier_guard.py --mode lite

guard-formal:
	PYTHONPATH=src python scripts/assert_free_tier_guard.py --mode formal; test $$? -eq 1

ready:
	PYTHONPATH=src python scripts/check_ready_for_aws.py

live-dry:
	PYTHONPATH=src python scripts/run_live.py --scale smoke --dry-validate

live:
	PYTHONPATH=src python scripts/run_live.py --scale smoke

live-lite:
	PYTHONPATH=src python scripts/run_live.py --scale lite

destroy:
	bash scripts/destroy_stack.sh
