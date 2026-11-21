#!/usr/bin/env python3
"""
amdahl.py — agrega speedup, eficiencia y fracción serial a un CSV de parse_stats.py.

Uso:
    python3 scripts/amdahl.py results/e4/e4.csv            # reescribe el CSV con columnas nuevas
    python3 scripts/amdahl.py results/e4/e4.csv -o otro.csv

Requiere columnas: n (tamaño), cores (núcleos = hilos) y cycles (ciclos de la ROI).
Para cada N, la referencia es la corrida con cores = 1 (mismo programa, 1 hilo).

Columnas agregadas:
    speedup     = ciclos(1 núcleo) / ciclos(p núcleos)
    efficiency  = speedup / p
    serial_kf   = fracción serial de Karp-Flatt para ese p:
                  e = (1/S - 1/p) / (1 - 1/p)
                  (si crece con p, la pérdida viene de sobrecosto paralelo -
                   sincronización, memoria, coherencia - y no de código serial fijo)
    amdahl_f    = fracción serial f que mejor ajusta S(p) = 1 / (f + (1-f)/p)
                  con todos los p > 1 de ese N (mínimos cuadrados sobre 1/S)
También imprime un resumen por N en stderr.
"""
import argparse
import csv
import sys


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("-o", "--output", help="por defecto reescribe el mismo archivo")
    args = ap.parse_args()

    with open(args.csv, newline="") as fh:
        reader = csv.DictReader(fh)
        cols = list(reader.fieldnames)
        rows = list(reader)

    by_n = {}
    for r in rows:
        if r.get("roi_ok", "1") != "1":
            continue
        by_n.setdefault(r["n"], []).append(r)

    for n, group in sorted(by_n.items(), key=lambda kv: f(kv[0]) or 0):
        base = [r for r in group if f(r["cores"]) == 1]
        if not base or not f(base[0]["cycles"]):
            print(f"[aviso] N={n}: falta la corrida con 1 núcleo, no se calcula speedup",
                  file=sys.stderr)
            continue
        c1 = f(base[0]["cycles"])
        sx = sy = 0.0
        for r in group:
            p, c = f(r["cores"]), f(r["cycles"])
            if not p or not c:
                continue
            s = c1 / c
            r["speedup"] = f"{s:.4f}"
            r["efficiency"] = f"{s / p:.4f}"
            if p > 1:
                x, y = 1 - 1 / p, 1 / s - 1 / p
                r["serial_kf"] = f"{y / x:.4f}"
                sx += x * x
                sy += x * y
        fit = sy / sx if sx else None
        for r in group:
            if fit is not None:
                r["amdahl_f"] = f"{fit:.4f}"

        print(f"N={n}:", file=sys.stderr)
        for r in sorted(group, key=lambda r: f(r["cores"])):
            print(f"  {r['cores']:>2} núcleos  speedup={r.get('speedup', '-'):>7}  "
                  f"eficiencia={r.get('efficiency', '-'):>7}  "
                  f"Karp-Flatt={r.get('serial_kf', '-'):>7}", file=sys.stderr)
        if fit is not None:
            print(f"  Amdahl (ajuste): fracción serial f = {fit:.4f}  "
                  f"-> speedup máximo teórico 1/f = {1 / fit if fit > 0 else float('inf'):.1f}",
                  file=sys.stderr)

    for c in ("speedup", "efficiency", "serial_kf", "amdahl_f"):
        if c not in cols:
            cols.append(c)
    with open(args.output or args.csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
