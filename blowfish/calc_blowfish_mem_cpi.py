import argparse
import os
import re
from dataclasses import dataclass
from typing import Dict, List

REQUIRED_KEYS = [
    "simTicks",
    "simFreq",
    "system.cpu.numCycles",
    "system.cpu.cpi",
    "system.cpu.ipc",
    "system.cpu.executeStats0.numInsts",
    "system.cpu.dcache.demandMisses::total",
    "system.cpu.dcache.demandMissLatency::total",
    "system.cpu.dcache.demandAvgMissLatency::total",
    "system.l2cache.demandMisses::total",
    "system.l2cache.demandMissLatency::total",
    "system.l2cache.demandAvgMissLatency::total",
]

LINE_RE = re.compile(r"^(?P<key>\S+)\s+(?P<val>[-+0-9.eE]+)\s*(#.*)?$")


@dataclass
class ResultRow:
    case: str
    cpi: float
    ipc: float
    numInsts: int
    numCycles: int
    simTicks: int
    simFreq: int
    ticks_per_cycle: float

    l1_misses: int
    l1_avg_miss_lat_ticks: float
    l1_miss_lat_ticks_total: int

    l2_misses: int
    l2_avg_miss_lat_ticks: float
    l2_miss_lat_ticks_total: int

    l1_avg_miss_lat_cycles: float
    l2_avg_miss_lat_cycles: float
    mpki_l1: float
    mpki_l2: float

    delta_cpi_mem_total: float
    delta_cpi_l2_miss: float
    delta_cpi_l1_only: float

    pct_cpi_mem_total: float
    pct_cpi_l2_miss: float
    pct_cpi_l1_only: float


def parse_stats(stats_path: str) -> Dict[str, float]:
    """Parse stats.txt and return only the needed key->value entries."""
    found: Dict[str, float] = {}
    with open(stats_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("----"):
                continue
            m = LINE_RE.match(line)
            if not m:
                continue
            key = m.group("key")
            if key in REQUIRED_KEYS:
                found[key] = float(m.group("val"))

    missing = [k for k in REQUIRED_KEYS if k not in found]
    if missing:
        raise ValueError(f"Missing required keys in {stats_path}: {missing}")
    return found


def compute_one(case: str, stats_path: str) -> ResultRow:
    """Compute all derived metrics for one run."""
    s = parse_stats(stats_path)

    simTicks = int(s["simTicks"])
    simFreq = int(s["simFreq"])
    numCycles = int(s["system.cpu.numCycles"])
    numInsts = int(s["system.cpu.executeStats0.numInsts"])
    cpi = float(s["system.cpu.cpi"])
    ipc = float(s["system.cpu.ipc"])

    ticks_per_cycle = simTicks / numCycles  # [ticks/cycle]

    # L1D (dcache)
    l1_misses = int(s["system.cpu.dcache.demandMisses::total"])
    l1_avg_miss_lat_ticks = float(s["system.cpu.dcache.demandAvgMissLatency::total"])  # [ticks/miss]
    l1_miss_lat_ticks_total = int(s["system.cpu.dcache.demandMissLatency::total"])     # [ticks]

    # L2
    l2_misses = int(s["system.l2cache.demandMisses::total"])
    l2_avg_miss_lat_ticks = float(s["system.l2cache.demandAvgMissLatency::total"])     # [ticks/miss]
    l2_miss_lat_ticks_total = int(s["system.l2cache.demandMissLatency::total"])        # [ticks]

    # Average miss latency in cycles
    l1_avg_miss_lat_cycles = l1_avg_miss_lat_ticks / ticks_per_cycle
    l2_avg_miss_lat_cycles = l2_avg_miss_lat_ticks / ticks_per_cycle

    # MPKI
    mpki_l1 = (l1_misses / numInsts) * 1000.0
    mpki_l2 = (l2_misses / numInsts) * 1000.0

    # Total miss-latency in cycles
    l1_miss_lat_cycles_total = l1_miss_lat_ticks_total / ticks_per_cycle
    l2_miss_lat_cycles_total = l2_miss_lat_ticks_total / ticks_per_cycle

    # Estimated delta CPI contributions
    delta_cpi_mem_total = l1_miss_lat_cycles_total / numInsts
    delta_cpi_l2_miss = l2_miss_lat_cycles_total / numInsts

    # Avoid double counting: split "mem total" into (L1-only) + (L2-miss)
    delta_cpi_l1_only = max(delta_cpi_mem_total - delta_cpi_l2_miss, 0.0)

    # Percent of measured CPI
    pct_cpi_mem_total = 100.0 * (delta_cpi_mem_total / cpi)
    pct_cpi_l2_miss = 100.0 * (delta_cpi_l2_miss / cpi)
    pct_cpi_l1_only = 100.0 * (delta_cpi_l1_only / cpi)

    return ResultRow(
        case=case,
        cpi=cpi,
        ipc=ipc,
        numInsts=numInsts,
        numCycles=numCycles,
        simTicks=simTicks,
        simFreq=simFreq,
        ticks_per_cycle=ticks_per_cycle,
        l1_misses=l1_misses,
        l1_avg_miss_lat_ticks=l1_avg_miss_lat_ticks,
        l1_miss_lat_ticks_total=l1_miss_lat_ticks_total,
        l2_misses=l2_misses,
        l2_avg_miss_lat_ticks=l2_avg_miss_lat_ticks,
        l2_miss_lat_ticks_total=l2_miss_lat_ticks_total,
        l1_avg_miss_lat_cycles=l1_avg_miss_lat_cycles,
        l2_avg_miss_lat_cycles=l2_avg_miss_lat_cycles,
        mpki_l1=mpki_l1,
        mpki_l2=mpki_l2,
        delta_cpi_mem_total=delta_cpi_mem_total,
        delta_cpi_l2_miss=delta_cpi_l2_miss,
        delta_cpi_l1_only=delta_cpi_l1_only,
        pct_cpi_mem_total=pct_cpi_mem_total,
        pct_cpi_l2_miss=pct_cpi_l2_miss,
        pct_cpi_l1_only=pct_cpi_l1_only,
    )


def to_csv(rows: List[ResultRow]) -> str:
    """CSV output for spreadsheets/plots."""
    header = [
        "case", "cpi", "ipc", "ticks_per_cycle",
        "mpki_l1", "avg_l1_miss_cycles",
        "mpki_l2", "avg_l2_miss_cycles",
        "deltaCPI_mem_total", "pctCPI_mem_total",
        "deltaCPI_l1_only", "pctCPI_l1_only",
        "deltaCPI_l2_miss", "pctCPI_l2_miss",
    ]
    lines = [",".join(header)]
    for r in rows:
        lines.append(",".join([
            r.case,
            f"{r.cpi:.6f}",
            f"{r.ipc:.6f}",
            f"{r.ticks_per_cycle:.6f}",
            f"{r.mpki_l1:.6f}",
            f"{r.l1_avg_miss_lat_cycles:.6f}",
            f"{r.mpki_l2:.6f}",
            f"{r.l2_avg_miss_lat_cycles:.6f}",
            f"{r.delta_cpi_mem_total:.8f}",
            f"{r.pct_cpi_mem_total:.4f}",
            f"{r.delta_cpi_l1_only:.8f}",
            f"{r.pct_cpi_l1_only:.4f}",
            f"{r.delta_cpi_l2_miss:.8f}",
            f"{r.pct_cpi_l2_miss:.4f}",
        ]))
    return "\n".join(lines)


def to_latex(rows: List[ResultRow]) -> str:
    """Compact LaTeX table focused on CPI impact in percent."""
    out = []
    out.append(r"\begin{table}[h]")
    out.append(r"\centering")
    out.append(r"\footnotesize")
    out.append(r"\setlength{\tabcolsep}{3pt}")
    out.append(r"\resizebox{\linewidth}{!}{%")
    out.append(r"\begin{tabular}{ll|c|c|c|c}")
    out.append(r"\hline")
    out.append(r"\textbf{Case} & \textbf{CPI} & \textbf{\%CPI mem total} & \textbf{\%CPI L1-only (approx)} & \textbf{\%CPI L2-miss} \\")
    out.append(r"\hline")
    for r in rows:
        out.append(
            rf"{r.case} & {r.cpi:.3f} & {r.pct_cpi_mem_total:.2f}\% & {r.pct_cpi_l1_only:.2f}\% & {r.pct_cpi_l2_miss:.2f}\% \\"
        )
    out.append(r"\hline")
    out.append(r"\end{tabular}")
    out.append(r"}")
    out.append(r"\caption{Estimated memory-penalty contribution to CPI for Blowfish runs (gem5 miss-latency accounting).}")
    out.append(r"\end{table}")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=".", help="Base directory containing the m5* run folders.")
    ap.add_argument("--out", default="blowfish_mem_cpi.csv", help="CSV output filename.")
    ap.add_argument("--latex", action="store_true", help="Print a LaTeX table to stdout.")
    ap.add_argument(
        "--dirs",
        nargs="*",
        default=[
            "m5bfA7_small",
            "m5bfA15_small",
            "m5bfA7_large",
            "m5bfA15_large",
        ],
        help="Run folders to process (each must contain stats.txt).",
    )
    args = ap.parse_args()

    rows: List[ResultRow] = []
    for d in args.dirs:
        stats_path = os.path.join(args.base, d, "stats.txt")
        case_name = d.replace("m5", "")
        rows.append(compute_one(case_name, stats_path))

    csv_text = to_csv(rows)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(csv_text + "\n")

    print(csv_text)
    if args.latex:
        print("\n" + to_latex(rows))


if __name__ == "__main__":
    main()
