#!/usr/bin/env bash
# Build iac/build/driver.zip for the load-generator Lambda (python3.12, arm64).
# The zip holds workloads/generator + workloads/lambda_handler and numpy for
# manylinux aarch64. boto3 comes with the Lambda runtime, so it is not bundled.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-python3}
OUT=iac/build
PKG=$OUT/pkg
rm -rf "$PKG" "$OUT/driver.zip"
mkdir -p "$PKG/workloads"

cp workloads/__init__.py "$PKG/workloads/"
cp -r workloads/generator workloads/lambda_handler "$PKG/workloads/"
find "$PKG" -name "__pycache__" -type d -prune -exec rm -rf {} +

"$PY" -m pip install --quiet --no-compile --target "$PKG" \
  --platform manylinux2014_aarch64 --implementation cp --python-version 3.12 --only-binary=:all: \
  "numpy>=1.26,<3"
rm -rf "$PKG/bin"

(cd "$PKG" && zip -q -r -X ../driver.zip .)
echo "built $OUT/driver.zip ($(du -h "$OUT/driver.zip" | cut -f1))"
