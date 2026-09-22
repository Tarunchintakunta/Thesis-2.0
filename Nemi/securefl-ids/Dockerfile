FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY scripts/run_docker_fl_worker.py ./scripts/run_docker_fl_worker.py
COPY data/UNSW_NB15_training-set.csv ./data/UNSW_NB15_training-set.csv

ENV PYTHONUNBUFFERED=1
CMD ["python", "scripts/run_docker_fl_worker.py"]
