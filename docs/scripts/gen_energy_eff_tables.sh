#!/usr/bin/env bash
set -euo pipefail

python3 "$(dirname "$0")/gen_energy_eff_tables.py"
