#!/usr/bin/env bash
# Build the six deployment packages into build/ and write build/package_manifest.json.
#
#   bash scripts/package_all.sh                 # python nodejs java
#   bash scripts/package_all.sh python nodejs   # skip java (no JDK on this machine)
#
# PY_PLATFORM defaults to the Lambda target (arm64 manylinux wheels). Every
# dependency in the default variant is pure python, so the same folder also runs
# locally for the init benchmark.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-python3}
PY_PLATFORM=${PY_PLATFORM:-manylinux2014_aarch64}
OUT=build
RUNTIMES=${*:-python nodejs java}
mkdir -p "$OUT"

pkg_python() {
  for v in default optimised bytecode; do
    d="$OUT/python-$v"
    rm -rf "$d" "$OUT/python-$v.zip"
    mkdir -p "$d"
    cp "functions/python/$v/handler.py" "$d/"
    if [ -f "functions/python/$v/requirements.txt" ]; then
      "$PY" -m pip install --quiet --no-compile --target "$d" \
        --platform "$PY_PLATFORM" --implementation cp --python-version 3.12 --only-binary=:all: \
        -r "functions/python/$v/requirements.txt"
      # console-script wrappers in bin/ carry the build machine's interpreter path in
      # their shebang, and RECORD lists their hashes - both make the zip differ from
      # machine to machine. Lambda never runs either, so they are dropped. The rest
      # of the pip metadata stays (it is part of a normal "default" upload).
      rm -rf "$d/bin"
      find "$d" -path "*.dist-info/RECORD" -delete
    fi
    if [ "$v" = "bytecode" ]; then
      "$PY" -m compileall -b "$d" >/dev/null
      find "$d" -name "*.py" -delete
      find "$d" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    fi
    echo "python-$v done"
  done
}

pkg_nodejs() {
  for v in default optimised; do
    d="$OUT/nodejs-$v"
    rm -rf "$d" "$OUT/nodejs-$v.zip"
    mkdir -p "$d"
    cp "functions/nodejs/$v/index.mjs" "functions/nodejs/$v/package.json" "$d/"
    if grep -q '"dependencies"' "$d/package.json"; then
      (cd "$d" && npm install --omit=dev --no-audit --no-fund --no-package-lock --silent)
    fi
    echo "nodejs-$v done"
  done
}

pkg_java() {
  for v in default optimised; do
    (cd "functions/java/$v" && mvn -q -B package -DskipTests)
    d="$OUT/java-$v"
    rm -rf "$d"
    mkdir -p "$d"
    cp "functions/java/$v/target/function.jar" "$d/function.jar"
    echo "java-$v done"
  done
}

for r in $RUNTIMES; do
  case "$r" in
    python) pkg_python ;;
    nodejs) pkg_nodejs ;;
    java) pkg_java ;;
    *) echo "unknown runtime $r" >&2; exit 2 ;;
  esac
done

PYTHONPATH=src "$PY" -m coldstart.packaging "$OUT"
