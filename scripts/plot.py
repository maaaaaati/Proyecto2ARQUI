#!/usr/bin/env python3
"""
plot.py — gráfico común para todos los experimentos, a partir del CSV de parse_stats.py.

Ejemplos:
    # barras: IPC por CPU, una barra por tamaño N
    python3 scripts/plot.py results/e1/e1.csv --x cpu --y ipc --hue n --kind bar -o results/e1/e1_ipc.png

    # líneas: speedup vs. núcleos, con la recta ideal
    python3 scripts/plot.py results/e4/e4.csv --x cores --y speedup --hue n --kind line --ideal -o results/e4/e4_speedup.png

    # solo algunas filas (--where columna=valor, repetible)
    python3 scripts/plot.py results/e2/e2.csv --x width --y ipc --hue rob --where n=128 -o e2.png

Solo necesita matplotlib (sin pandas).
"""
import argparse
import csv
import sys

import matplotlib
matplotlib.use("Agg")  # sin ventana: escribe directo a archivo
import matplotlib.pyplot as plt

# Paleta categórica legible en informe y video (azul, naranja, verde, morado, rojo, gris)
COLORS = ["#2a6fdb", "#e8833a", "#2e9e5b", "#8a5cd1", "#d1495b", "#6c757d"]

LABELS = {
    "ipc": "IPC", "cpi": "CPI", "cycles": "Ciclos", "sim_seconds": "Tiempo simulado (s)",
    "sim_insts": "Instrucciones", "l1d_miss_rate": "Tasa de fallos L1D",
    "l2_miss_rate": "Tasa de fallos L2", "speedup": "Speedup", "efficiency": "Eficiencia",
    "cpu": "Modelo de CPU", "n": "N", "cores": "Núcleos", "width": "Ancho de emisión",
    "rob": "Entradas del ROB", "vl": "VL (bits)",
}


def num(s):
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return s


def sort_key(v):
    return (0, v) if isinstance(v, (int, float)) else (1, str(v))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--x", required=True, help="columna del eje X")
    ap.add_argument("--y", required=True, help="columna del eje Y")
    ap.add_argument("--hue", help="columna que separa series (colores)")
    ap.add_argument("--kind", choices=["bar", "line"], default="bar")
    ap.add_argument("--where", action="append", default=[], metavar="COL=VAL",
                    help="filtra filas (repetible)")
    ap.add_argument("--ideal", action="store_true",
                    help="dibuja y = x (útil para speedup vs. núcleos)")
    ap.add_argument("--order", help="orden de las categorías del eje X, separadas por coma "
                                    "(ej.: timingsimple,minor,o3)")
    ap.add_argument("--logx", action="store_true", help="eje X logarítmico base 2")
    ap.add_argument("--title", default="")
    ap.add_argument("--xlabel"), ap.add_argument("--ylabel")
    ap.add_argument("-o", "--output", required=True, help="archivo de salida (.png o .pdf)")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        rows = [{k: num(v) for k, v in r.items()} for r in csv.DictReader(f)]
    for cond in args.where:
        k, v = cond.split("=", 1)
        rows = [r for r in rows if str(r.get(k)) == v]
    rows = [r for r in rows if r.get(args.y) not in ("", None)]
    if not rows:
        sys.exit("No hay filas para graficar (revisa --y / --where).")
    for c in (args.x, args.y, args.hue):
        if c and c not in rows[0]:
            sys.exit(f"La columna '{c}' no existe. Columnas: {', '.join(rows[0])}")

    xs = sorted({r[args.x] for r in rows}, key=sort_key)
    if args.order:
        pref = [num(s) for s in args.order.split(",")]
        xs = [x for x in pref if x in xs] + [x for x in xs if x not in pref]
    hues = sorted({r[args.hue] for r in rows}, key=sort_key) if args.hue else [None]

    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=150)
    width = 0.8 / len(hues)
    for i, h in enumerate(hues):
        sub = [r for r in rows if h is None or r[args.hue] == h]
        pts = {r[args.x]: r[args.y] for r in sub}
        label = f"{LABELS.get(args.hue, args.hue)} = {h}" if h is not None else None
        color = COLORS[i % len(COLORS)]
        if args.kind == "bar":
            pos = [xs.index(x) + (i - (len(hues) - 1) / 2) * width for x in xs if x in pts]
            vals = [pts[x] for x in xs if x in pts]
            bars = ax.bar(pos, vals, width * 0.92, label=label, color=color)
            ax.bar_label(bars, fmt="%.3g", fontsize=7, padding=2)
        else:
            xv = [x for x in xs if x in pts]
            ax.plot(xv, [pts[x] for x in xv], marker="o", label=label, color=color, linewidth=2)

    if args.kind == "bar":
        ax.set_xticks(range(len(xs)), [str(x) for x in xs])
    if args.ideal:
        nx = [x for x in xs if isinstance(x, (int, float))]
        ax.plot(nx, nx, linestyle="--", color="#888888", label="Ideal")
    if args.logx:
        ax.set_xscale("log", base=2)
        ax.set_xticks(xs, [str(x) for x in xs])

    ax.set_xlabel(args.xlabel or LABELS.get(args.x, args.x))
    ax.set_ylabel(args.ylabel or LABELS.get(args.y, args.y))
    if args.title:
        ax.set_title(args.title)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    if args.hue or args.ideal:
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.output)
    print(f"gráfico -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
