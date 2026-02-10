#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/santiago/archmic/Tp4/dijkstra"
GEM5="/home/santiago/archmic/gem5/build/RISCV/gem5.opt"
CFG="/home/santiago/archmic/Tp4/CortexA7L1.py"
INPUT_DAT="/home/santiago/archmic/Tp4/dijkstra/input.dat"

PROG_SMALL="/home/santiago/archmic/Tp4/dijkstra/dijkstra_small.riscv"
PROG_LARGE="/home/santiago/archmic/Tp4/dijkstra/dijkstra_large.riscv"

L1_SIZES=("1kB" "2kB" "4kB" "8kB" "16kB")

OUT_SIM_BASE="${BASE_DIR}/runs_L1_A7"
OUT_CSV_DIR="${BASE_DIR}/plots_L1_A7"

CSV_OUT="${OUT_CSV_DIR}/resultats_L1_A7_dijkstra.csv"

mkdir -p "$OUT_SIM_BASE" "$OUT_CSV_DIR"
cd "$BASE_DIR"

echo "jeu_donnees,L1_taille,cpi,numCycles,dossier_sortie" > "$CSV_OUT"

run_one() {
  local dataset="$1"
  local prog="$2"
  local l1="$3"

  local outdir="${OUT_SIM_BASE}/dijkstra_${dataset}_L1_${l1}"
  rm -rf "$outdir"
  mkdir -p "$outdir"

  echo "Running: dataset=${dataset}, L1=${l1}"
  "$GEM5" -d "$outdir" \
    "$CFG" \
    --cmd="$prog" \
    --l1-size="$l1" \
    --options "$INPUT_DAT" >/dev/null

  local stats="${outdir}/stats.txt"
  if [[ ! -f "$stats" ]]; then
    echo "ERROR: No stats.txt in $outdir"
    exit 1
  fi

  local cpi cycles
  cpi="$(awk '$1=="system.cpu.cpi"{print $2; exit}' "$stats")"
  cycles="$(awk '$1=="system.cpu.numCycles"{print $2; exit}' "$stats")"

  if [[ -z "${cpi}" || -z "${cycles}" ]]; then
    echo "ERROR: Missing system.cpu.cpi or system.cpu.numCycles in $stats"
    exit 1
  fi

  echo "${dataset},${l1},${cpi},${cycles},${outdir}" >> "$CSV_OUT"
  echo "CPI=${cpi} | numCycles=${cycles}"
}

for l1 in "${L1_SIZES[@]}"; do
  run_one "small" "$PROG_SMALL" "$l1"
done

for l1 in "${L1_SIZES[@]}"; do
  run_one "large" "$PROG_LARGE" "$l1"
done

echo "CSV guardado en: $CSV_OUT"
