#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

P_MAX_MW = {
    "A7": 100.0,
    "A15": 500.0,
}


def parse_metrics(path: Path) -> dict[str, dict[int, float]]:
    by_ds: dict[str, dict[int, float]] = {}
    if not path.is_file():
        return by_ds
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ds = (row.get("jeu_donnees") or "").strip()
            l1 = (row.get("L1_taille") or "").strip().lower()
            if not ds or not l1.endswith("kb"):
                continue
            try:
                kb = int(float(l1[:-2]))
            except ValueError:
                continue
            try:
                ipc = float(row.get("ipc", ""))
            except ValueError:
                continue
            by_ds.setdefault(ds, {})[kb] = ipc
    return by_ds


def fmt(val: float | None) -> str:
    if val is None:
        return "--"
    return f"{val:.5f}".replace(".", ",")


def build_table(core: str, metrics: dict[str, dict[int, float]]) -> list[str]:
    pmax = P_MAX_MW[core]
    sizes = set()
    for d in metrics.values():
        sizes.update(d.keys())
    sizes = sorted(sizes)

    title = f"Cortex-{core}"
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\footnotesize",
        r"\resizebox{\linewidth}{!}{%",
        r"\begin{tabular}{c|c|c|c|c}",
        r"\hline",
        r"\textbf{L1 (kB)} & \textbf{Dijkstra small} & \textbf{Dijkstra large} & \textbf{Blowfish small} & \textbf{Blowfish large} \\",
        r"\hline",
    ]
    for kb in sizes:
        row_vals = []
        for algo in ("dijkstra", "blowfish"):
            for ds in ("small", "large"):
                ipc = metrics.get(f"{algo}_{ds}", {}).get(kb)
                val = None if ipc is None else ipc / pmax
                row_vals.append(fmt(val))
        lines.append(f"{kb}  & {row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} \\\\")
    lines += [
        r"\hline",
        r"\end{tabular}",
        r"}",
        rf"\caption{{Efficacite energetique (IPC/mW) pour {title} ($P_{{\max}}$ = \mbox{{{int(pmax)}\,mW}}).}}",
        rf"\label{{tab:eff-energetique-{core.lower()}}}",
        r"\end{table}",
        "",
    ]
    return lines


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out_path = root / "docs" / "sections" / "EfficaciteEnergetique_tables.tex"

    blocks: list[str] = []
    for core in ("A7", "A15"):
        dj_path = root / f"dijkstra/plots_L1_{core}/metrics_L1_{core}_dijkstra.csv"
        bf_path = root / f"blowfish/plots_L1_{core}/metrics_L1_{core}_blowfish.csv"

        metrics: dict[str, dict[int, float]] = {}
        dj = parse_metrics(dj_path)
        bf = parse_metrics(bf_path)
        metrics["dijkstra_small"] = dj.get("small", {})
        metrics["dijkstra_large"] = dj.get("large", {})
        metrics["blowfish_small"] = bf.get("small", {})
        metrics["blowfish_large"] = bf.get("large", {})

        blocks.extend(build_table(core, metrics))

    out_path.write_text("\n".join(blocks).rstrip() + "\n", encoding="utf-8")
    print(f"Listo: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
