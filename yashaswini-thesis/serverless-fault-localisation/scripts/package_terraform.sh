#!/usr/bin/env bash
# Build Lambda zip packages for terraform/ (SAM not required).
# Output: build/{faultlab-layer,orders-api,inventory,payments,notifications}.zip
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
LAYER_STAGE="$BUILD/layer-stage"
PY="${PYTHON:-python3.12}"

rm -rf "$BUILD"
mkdir -p "$BUILD" "$LAYER_STAGE/python"

# Shared layer: faultlab package + aws-xray-sdk under python/
cp -R "$ROOT/src/layer/faultlab" "$LAYER_STAGE/python/faultlab"
"$PY" -m pip install -q -r "$ROOT/src/layer/requirements.txt" -t "$LAYER_STAGE/python" \
  --platform manylinux2014_aarch64 --only-binary=:all: --python-version 3.12 --implementation cp \
  2>/dev/null || "$PY" -m pip install -q -r "$ROOT/src/layer/requirements.txt" -t "$LAYER_STAGE/python"
(cd "$LAYER_STAGE" && zip -qr "$BUILD/faultlab-layer.zip" python)

for svc in orders_api inventory payments notifications; do
  zip_name="${svc//_/-}.zip"
  (cd "$ROOT/src/$svc" && zip -qr "$BUILD/$zip_name" app.py)
done

echo "packages:"
ls -la "$BUILD"/*.zip
