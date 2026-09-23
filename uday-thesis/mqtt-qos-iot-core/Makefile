.PHONY: test analyse ready live live-lite live-dry destroy

test:
	cd $(CURDIR) && PYTHONPATH=src pytest -q

analyse:
	PYTHONPATH=src python scripts/analyse.py --plots

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
