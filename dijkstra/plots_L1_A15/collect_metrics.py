from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

METRIC_KEYS = {
    "system.cpu.cpi": "cpi",
    "system.cpu.ipc": "ipc",
    "system.cpu.numCycles": "numCycles",
    "system.cpu.icache.overallMissRate::total": "icache_miss",
    "system.cpu.dcache.overallMissRate::total": "dcache_miss",
    "system.l2cache.overallMissRate::total": "l2_miss",
    "system.cpu.branchPred.BTBHitRatio": "btb_hit_ratio",
    "system.cpu.branchPred.condPredicted": "bp_cond_pred",
    "system.cpu.branchPred.condIncorrect": "bp_cond_incorrect",
    "system.cpu.branchPred.lookups": "bp_lookups",
    "system.cpu.commit.branchMispredicts": "bp_mispredicts",
}

LINE_RE = re.compile(r"^(\S+)\s+([0-9eE+\-\.]+)")


def pick_input_csv(dir_path: Path, csv_arg: str | None) -> Path:
    if csv_arg:
        return Path(csv_arg)
    csvs = sorted(dir_path.glob("resultats_*.csv"))
    if not csvs:
        raise SystemExit("No se encontro ningun resultats_*.csv en el directorio actual.")
    if len(csvs) > 1:
        print("Aviso: se encontraron varios CSV, se usara el primero:", csvs[0])
    return csvs[0]


def read_stats(stats_path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    with stats_path.open(encoding="utf-8") as f:
        for line in f:
            m = LINE_RE.match(line)
            if not m:
                continue
            key, val = m.group(1), m.group(2)
            if key in METRIC_KEYS:
                try:
                    values[key] = float(val)
                except ValueError:
                    pass
    return values


def fmt(val: float | None) -> str:
    if val is None:
        return ""
    return f"{val:.6f}".rstrip("0").rstrip(".")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraer métricas desde stats.txt por L1")
    parser.add_argument("--csv", help="Ruta al CSV de resultados (por defecto resultats_*.csv)")
    parser.add_argument("--out", help="Ruta de salida CSV (por defecto metrics_*.csv)")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    in_csv = pick_input_csv(here, args.csv)

    out_csv = Path(args.out) if args.out else in_csv.with_name(in_csv.name.replace("resultats_", "metrics_"))

    with in_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            raise SystemExit("El CSV de entrada esta vacio: " + str(in_csv))

    out_fields = [
        "jeu_donnees",
        "L1_taille",
        "cpi",
        "ipc",
        "numCycles",
        "icache_miss",
        "dcache_miss",
        "l2_miss",
        "bp_cond_mispredict_rate",
        "btb_hit_ratio",
        "bp_mispredict_rate",
    ]

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()

        for r in rows:
            outdir = Path(r.get("dossier_sortie", ""))
            stats_path = outdir / "stats.txt"
            if not stats_path.is_file():
                print("Aviso: no existe stats.txt en", stats_path)
                continue

            values = read_stats(stats_path)
            cond_pred = values.get("system.cpu.branchPred.condPredicted")
            cond_inc = values.get("system.cpu.branchPred.condIncorrect")
            bp_cond_rate = None
            if cond_pred and cond_pred > 0:
                bp_cond_rate = cond_inc / cond_pred if cond_inc is not None else None

            lookups = values.get("system.cpu.branchPred.lookups")
            mispred = values.get("system.cpu.commit.branchMispredicts")
            bp_rate = None
            if lookups and lookups > 0:
                bp_rate = mispred / lookups if mispred is not None else None

            row_out = {
                "jeu_donnees": r.get("jeu_donnees", ""),
                "L1_taille": r.get("L1_taille", ""),
                "cpi": fmt(values.get("system.cpu.cpi")),
                "ipc": fmt(values.get("system.cpu.ipc")),
                "numCycles": fmt(values.get("system.cpu.numCycles")),
                "icache_miss": fmt(values.get("system.cpu.icache.overallMissRate::total")),
                "dcache_miss": fmt(values.get("system.cpu.dcache.overallMissRate::total")),
                "l2_miss": fmt(values.get("system.l2cache.overallMissRate::total")),
                "bp_cond_mispredict_rate": fmt(bp_cond_rate),
                "btb_hit_ratio": fmt(values.get("system.cpu.branchPred.BTBHitRatio")),
                "bp_mispredict_rate": fmt(bp_rate),
            }
            writer.writerow(row_out)

    print("CSV generado:", out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
