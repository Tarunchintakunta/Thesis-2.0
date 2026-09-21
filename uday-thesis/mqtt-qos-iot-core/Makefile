.PHONY: test dry-run analyse plan-ft live

test:
	cd $(CURDIR) && PYTHONPATH=src pytest -q

dry-run:
	PYTHONPATH=src python scripts/run_dry_run.py --plots

analyse:
	PYTHONPATH=src python scripts/analyse.py --plots

plan-ft:
	PYTHONPATH=src python scripts/plan_free_tier.py

live:
	PYTHONPATH=src python scripts/run_live.py
