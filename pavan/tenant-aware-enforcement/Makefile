PY ?= python3
export PYTHONPATH := src:.

.PHONY: setup test pilot docker-up docker-down clean

setup:
	$(PY) -m pip install -r requirements.txt -q

test:
	$(PY) -m pytest -q

pilot:
	$(PY) -m sim.runner
	@echo "Wrote results/local_sim/pilot_results.json (LOCAL_SIM)"

docker-up:
	docker compose up -d

docker-down:
	docker compose down -v

clean:
	rm -rf .pytest_cache **/__pycache__
