#!/usr/bin/env bash
# Builds build/lambda.zip: the lambda_fn package plus the pinned boto3/botocore
# from src/lambda_fn/requirements.txt, so the SDK version does not depend on
# whatever the managed runtime ships. All wheels are pure Python, so a build on
# macOS or Linux gives the same package; timestamps and pip's RECORD files are
# normalised so the zip hash is reproducible.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-python3}
export TZ=UTC  # zip stores local time - the same timestamps on every machine

rm -rf build/lambda build/lambda.zip
mkdir -p build/lambda
"$PY" -m pip install --quiet --no-compile --disable-pip-version-check \
  --only-binary=:all: --platform manylinux2014_aarch64 --python-version 3.12 --implementation cp \
  --target build/lambda -r src/lambda_fn/requirements.txt
cp -R src/lambda_fn build/lambda/
find build/lambda -name "__pycache__" -type d -prune -exec rm -rf {} +
find build/lambda -path "*.dist-info/RECORD" -delete
rm -rf build/lambda/bin
find build/lambda -exec touch -h -t 202601010000 {} +
(cd build/lambda && find . -type f | LC_ALL=C sort | TZ=UTC zip -q -X -D ../lambda.zip -@)
echo "build/lambda.zip $(shasum -a 256 build/lambda.zip | cut -c1-16)"
