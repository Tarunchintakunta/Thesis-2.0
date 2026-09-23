#!/usr/bin/env bash
# Package src/lambda_handler for terraform apply.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
(cd "$ROOT/src/lambda_handler" && zip -qr "$BUILD/lambda_handler.zip" .)
ls -la "$BUILD/lambda_handler.zip"
