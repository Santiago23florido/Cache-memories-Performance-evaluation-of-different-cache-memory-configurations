#!/usr/bin/env bash
# run_dijkstra_mem_cpi.sh
# Run the Python script on the 4 Dijkstra folders and print CSV + LaTeX.
set -euo pipefail

# Execute from the directory that contains:
#   m5smalldijkstraA7/, m5smalldijkstraA15/, m5largedijkstraA7/, m5largedijkstraA15/
python3 calc_dijkstra_mem_cpi.py --out dijkstra_mem_cpi.csv --latex
