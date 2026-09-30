#!/usr/bin/env bash
# Download the LBNL Building 59 files used by this project into data/raw/.
# Primary source: Dryad, doi:10.7941/D1N33Q (Luo et al., 2022). Dryad blocks scripted
# downloads, so this script uses the Kaggle mirror of the same "Bldg59_clean data" folder.
# Needs a Kaggle API token in ~/.kaggle/kaggle.json.
set -euo pipefail
cd "$(dirname "$0")/../data/raw" 2>/dev/null || { mkdir -p "$(dirname "$0")/../data/raw"; cd "$(dirname "$0")/../data/raw"; }
D=gideonkipkorir/building-operational-performance
P="Building_59/Bldg59_clean data"
kaggle datasets download "$D" -f README_Dryad_Bldg59.txt -p .
for f in ele site_weather zone_temp_interior wifi rtu_sa_t rtu_ra_t rtu_fan_spd; do
  kaggle datasets download "$D" -f "$P/$f.csv" -p .
  [ -f "$f.csv.zip" ] && unzip -oq "$f.csv.zip" && rm "$f.csv.zip"
done
ls -la
