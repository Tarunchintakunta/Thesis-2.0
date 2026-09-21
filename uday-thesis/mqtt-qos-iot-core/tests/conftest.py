import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
# Also allow importing lambda_ingest as a top-level package name used by tests.
sys.path.insert(0, str(ROOT / "src" / "lambda_ingest"))
