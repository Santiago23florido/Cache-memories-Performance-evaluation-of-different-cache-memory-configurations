#!/usr/bin/env bash
# run_blowfish_mem_cpi.sh
# Run the Python script on the 4 Blowfish folders and print CSV + LaTeX.
set -euo pipefail

# Execute from the directory that contains:
#   m5bfA7_small/, m5bfA15_small/, m5bfA7_large/, m5bfA15_large/
python3 calc_blowfish_mem_cpi.py --out blowfish_mem_cpi.csv --latex
