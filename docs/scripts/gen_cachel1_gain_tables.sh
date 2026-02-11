#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUT_FILE="${ROOT_DIR}/docs/sections/CacheL1_gains_tables.tex"

python3 "${SCRIPT_DIR}/gen_cachel1_gain_tables.py" --out "${OUT_FILE}"
echo "Generado: ${OUT_FILE}"
