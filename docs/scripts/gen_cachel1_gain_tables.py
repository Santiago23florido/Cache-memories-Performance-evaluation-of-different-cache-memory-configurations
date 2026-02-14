from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


PREFERRED_DATASETS = ["small", "large"]


def parse_size(label: str) -> float:
    s = label.strip().lower()
    for suffix, factor in (("kb", 1.0), ("mb", 1024.0), ("gb", 1024.0 * 1024.0)):
        if s.endswith(suffix):
            try:
                return float(s[: -len(suffix)]) * factor
            except ValueError:
                return float("inf")
    try:
        return float(s)
    except ValueError:
        return float("inf")


def fmt_l1(label: str) -> str:
    text = label.strip()
    lower = text.lower()
    if lower.endswith("kb"):
        num = text[:-2].strip()
        return f"{num}\\,kB"
    return text


def fmt_pct(value: float) -> str:
    rounded = round(value + 1e-12, 2)
    if abs(rounded) < 0.005:
        rounded = 0.0
    return f"{rounded:.2f}".replace(".", ",")


def order_datasets(datasets: list[str]) -> list[str]:
    ordered = [d for d in PREFERRED_DATASETS if d in datasets]
    rest = [d for d in datasets if d not in ordered]
    return ordered + sorted(rest)


def read_metrics(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise SystemExit(f"CSV vacio: {csv_path}")
    return rows


def gains_for_dataset(rows: list[dict[str, str]], base_l1: str) -> list[tuple[str, float, float, float]]:
    by_l1 = {r["L1_taille"]: r for r in rows}
    if base_l1 not in by_l1:
        base_l1 = min(by_l1.keys(), key=parse_size)
    base = by_l1[base_l1]

    base_ipc = float(base["ipc"])
    base_i = float(base["icache_miss"])
    base_d = float(base["dcache_miss"])

    out: list[tuple[str, float, float, float]] = []
    for l1 in sorted(by_l1.keys(), key=parse_size):
        r = by_l1[l1]
        ipc = float(r["ipc"])
        i = float(r["icache_miss"])
        d = float(r["dcache_miss"])
        gain_ipc = (ipc / base_ipc - 1.0) * 100.0
        gain_i = (1.0 - i / base_i) * 100.0
        gain_d = (1.0 - d / base_d) * 100.0
        out.append((l1, gain_ipc, gain_i, gain_d))
    return out


def render_table(program: str, dataset: str, cpu: str, base_l1: str,
                 rows: list[tuple[str, float, float, float]]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\resizebox{\linewidth}{!}{%",
        r"\begin{tabular}{l|c|c|c}",
        r"\hline",
        r"\textbf{L1} & \textbf{Gain IPC (\%)} & \textbf{Baisse miss I-Cache (\%)} & \textbf{Baisse miss D-Cache (\%)} \\",
        r"\hline",
    ]
    for l1, g_ipc, g_i, g_d in rows:
        lines.append(
            f"{fmt_l1(l1)}  & {fmt_pct(g_ipc)} & {fmt_pct(g_i)} & {fmt_pct(g_d)} \\\\"
        )
    lines += [
        r"\hline",
        r"\end{tabular}",
        r"}",
        rf"\caption{{{program} {dataset} ({cpu}) : gains relatifs par rapport à {fmt_l1(base_l1)}.}}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)




def generate_all() -> str:
    root = Path(__file__).resolve().parents[2]
    configs = [
        ("Dijkstra", "Cortex-A7", root / "dijkstra/plots_L1_A7/metrics_L1_A7_dijkstra.csv", "1kB"),
        ("Dijkstra", "Cortex-A15", root / "dijkstra/plots_L1_A15/metrics_L1_A15_dijkstra.csv", "2kB"),
        ("Blowfish", "Cortex-A7", root / "blowfish/plots_L1_A7/metrics_L1_A7_blowfish.csv", "1kB"),
        ("Blowfish", "Cortex-A15", root / "blowfish/plots_L1_A15/metrics_L1_A15_blowfish.csv", "2kB"),
    ]

    blocks: list[str] = [
        f"% Auto-généré : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "% Source : metrics_*.csv",
        "",
    ]

    for program, cpu, csv_path, base_l1 in configs:
        rows = read_metrics(csv_path)
        datasets = order_datasets(sorted({r["jeu_donnees"] for r in rows if r.get("jeu_donnees")}))
        for dataset in datasets:
            ds_rows = [r for r in rows if r.get("jeu_donnees") == dataset]
            if not ds_rows:
                continue
            gains = gains_for_dataset(ds_rows, base_l1)
            blocks.append(render_table(program, dataset, cpu, base_l1, gains))
    return "\n".join(blocks).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generar tablas LaTeX de gains L1")
    parser.add_argument("--out", help="Archivo de salida (por defecto stdout)")
    args = parser.parse_args()

    content = generate_all()
    if args.out:
        Path(args.out).write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
