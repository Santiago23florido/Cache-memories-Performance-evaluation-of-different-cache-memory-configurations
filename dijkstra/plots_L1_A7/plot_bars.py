

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except Exception:
    print("ERROR: matplotlib no esta instalado. Instala python3-matplotlib para usar este script.")
    raise SystemExit(1)

SKIP_COLS = {"jeu_donnees", "L1_taille", "dossier_sortie"}


def parse_size(label: str) -> float:
    s = label.strip()
    lower = s.lower()
    for suffix, factor in (("kb", 1.0), ("mb", 1024.0), ("gb", 1024.0 * 1024.0)):
        if lower.endswith(suffix):
            try:
                return float(lower[: -len(suffix)]) * factor
            except ValueError:
                return float("inf")
    try:
        return float(lower)
    except ValueError:
        return float("inf")


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def format_value(value: float | None) -> str:
    if value is None:
        return ""
    if math.isnan(value):
        return ""
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    text = f"{value:.6f}"
    return text.rstrip("0").rstrip(".")



def pick_csv(dir_path: Path, csv_arg: str | None) -> Path:
    if csv_arg:
        return Path(csv_arg)
    csvs = sorted(dir_path.glob("*.csv"))
    if not csvs:
        raise SystemExit("No se encontro ningun .csv en el directorio actual.")
    if len(csvs) > 1:
        print("Aviso: se encontraron varios CSV, se usara el primero:", csvs[0])
    return csvs[0]



def main() -> int:
    parser = argparse.ArgumentParser(description="Grafico de barras por variable desde CSV")
    parser.add_argument("--csv", help="Ruta al CSV (por defecto el primero en el directorio)")
    parser.add_argument("--outdir", help="Directorio de salida para las imagenes (por defecto esta carpeta plots)")
    parser.add_argument("--show", action="store_true", help="Mostrar las figuras en pantalla")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    csv_path = pick_csv(here, args.csv)
    outdir = Path(args.outdir) if args.outdir else here
    outdir.mkdir(parents=True, exist_ok=True)

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            raise SystemExit("El CSV esta vacio: " + str(csv_path))
        fieldnames = reader.fieldnames or []

    metrics: list[str] = []
    for col in fieldnames:
        if col in SKIP_COLS:
            continue
        if any(parse_float(r.get(col)) is not None for r in rows):
            metrics.append(col)

    if not metrics:
        raise SystemExit("No se encontraron columnas numericas para graficar en el CSV.")

    datasets = sorted({r.get("jeu_donnees", "") for r in rows if r.get("jeu_donnees")})
    if not datasets:
        datasets = ["datos"]

    l1_sizes = sorted({r.get("L1_taille", "") for r in rows if r.get("L1_taille")}, key=parse_size)
    if not l1_sizes:
        raise SystemExit("No se encontraron valores de L1_taille para graficar.")

    values: dict[str, dict[str, dict[str, float | None]]] = {
        ds: {l1: {m: None for m in metrics} for l1 in l1_sizes} for ds in datasets
    }

    for r in rows:
        ds = r.get("jeu_donnees", "") or datasets[0]
        l1 = r.get("L1_taille", "")
        if ds not in values or l1 not in values[ds]:
            continue
        for m in metrics:
            val = parse_float(r.get(m))
            if val is not None:
                values[ds][l1][m] = val

    x = list(range(len(l1_sizes)))
    n_datasets = max(1, len(datasets))
    width = 0.8 / n_datasets

    for m in metrics:
        metric_values = []
        for ds in datasets:
            for l1 in l1_sizes:
                v = values[ds][l1][m]
                if v is not None and not math.isnan(v):
                    metric_values.append(v)
        if metric_values:
            min_v = min(metric_values)
            max_v = max(metric_values)
            if min_v == max_v:
                pad = max(abs(max_v) * 0.02, 1.0)
                y_min = min_v - pad
                y_max = max_v + pad
            else:
                range_v = max_v - min_v
                rel = range_v / max(abs(max_v), 1e-12)
                if rel < 0.1:
                    pad = max(range_v * 0.1, abs(max_v) * 0.01, 1e-6)
                    y_min = min_v - pad
                    y_max = max_v + pad
                else:
                    y_min = 0.0
                    y_max = max_v * 1.05
        else:
            y_min, y_max = 0.0, 1.0
        fig, ax = plt.subplots()
        ax.set_ylim(y_min, y_max)
        for j, ds in enumerate(datasets):
            offset = (j - (n_datasets - 1) / 2.0) * width
            xs = [i + offset for i in x]
            ys = []
            for l1 in l1_sizes:
                v = values[ds][l1][m]
                ys.append(v if v is not None else math.nan)
            label = ds if len(datasets) > 1 else None
            bars = ax.bar(xs, ys, width=width, label=label)
            ax.bar_label(
                bars,
                labels=[format_value(y) for y in ys],
                padding=3,
                fontsize=8,
                rotation=90,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(l1_sizes)
        ax.set_xlabel("L1_taille")
        ax.set_ylabel(m)
        ax.set_title(f"{m} por L1_taille")
        if len(datasets) > 1:
            ax.legend()
        fig.tight_layout()
        out_file = outdir / f"{m}_bar.png"
        fig.savefig(out_file, dpi=150)
        if args.show:
            plt.show()
        plt.close(fig)
        print("Grafico guardado en:", out_file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
