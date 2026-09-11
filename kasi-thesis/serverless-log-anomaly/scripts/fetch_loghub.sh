#!/usr/bin/env bash
# Download the Loghub BGL 2k sample (labelled source corpus for D2) and check it.
# Loghub: "freely available for research or academic work" - https://github.com/logpai/loghub
# Cite: Zhu et al. (2023) Loghub, ISSRE, doi:10.1109/ISSRE59848.2023.00071
set -euo pipefail
cd "$(dirname "$0")/.."

URL=https://raw.githubusercontent.com/logpai/loghub/master/BGL/BGL_2k.log
DEST=data/external/loghub/BGL_2k.log
EXPECTED=2a819ea540909db682005c9cf948387a40729b5c2e9f19d430e29ce704825496

mkdir -p "$(dirname "$DEST")"
if [ ! -f "$DEST" ]; then
  curl -sSfL -o "$DEST" "$URL"
fi

if command -v sha256sum >/dev/null; then
  GOT=$(sha256sum "$DEST" | cut -d' ' -f1)
else
  GOT=$(shasum -a 256 "$DEST" | cut -d' ' -f1)
fi
if [ "$GOT" != "$EXPECTED" ]; then
  echo "checksum mismatch for $DEST (got $GOT) - the upstream file changed, check before using it"
  exit 1
fi
echo "ok: $DEST ($(wc -l < "$DEST") lines, sha256 verified)"
