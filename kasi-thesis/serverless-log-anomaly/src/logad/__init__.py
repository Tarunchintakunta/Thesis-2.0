"""logad - source-free vs transfer log anomaly detection on serverless logs.

Sub packages follow the pipeline order:
collect -> inject -> parse -> features -> detectors -> eval  (pipeline.py glues them)
"""

__version__ = "0.1.0"
