#!/usr/bin/env python3
"""
e3_speedup.py — agrega al CSV de E3 el speedup de SVE frente al código escalar.

Uso:
    python3 scripts/e3_speedup.py results/e3/e3.csv           # reescribe el CSV
    python3 scripts/e3_speedup.py results/e3/e3.csv -o otro.csv

Requiere columnas: kernel (scalar | sve), n, vl, lanes, cycles, sim_insts.
Para cada N, la referencia es la corrida kernel=scalar con el mismo N.

Columnas agregadas:
    speedup          = ciclos(escalar) / ciclos(SVE)
    ideal_speedup    = carriles = VL / 32 (floats por vector); el máximo teórico
                       si todo el trabajo fuera vectorial y sin cuellos de memoria
    vec_efficiency   = speedup / ideal_speedup (1 = escala perfecto con VL)
    inst_reduction   = instrucciones(escalar) / instrucciones(SVE)
También imprime una tabla por N en stderr, lista para el informe.
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

    base = {}
    for r in rows:
        if r.get("roi_ok", "1") == "1" and r.get("kernel") == "scalar":
            base[r["n"]] = r

    new = ["speedup", "ideal_speedup", "vec_efficiency", "inst_reduction"]
    for c in new:
        if c not in cols:
            cols.append(c)

    for r in rows:
        b = base.get(r.get("n"))
        cyc, ins, lanes = f(r.get("cycles")), f(r.get("sim_insts")), f(r.get("lanes"))
        if not b or r.get("roi_ok", "1") != "1" or not cyc or not ins:
            for c in new:
                r[c] = ""
            continue
        s = f(b["cycles"]) / cyc
        ideal = lanes if lanes else 1.0
        r["speedup"] = f"{s:.4f}"
        r["ideal_speedup"] = f"{ideal:g}"
        r["vec_efficiency"] = f"{s / ideal:.4f}"
        r["inst_reduction"] = f"{f(b['sim_insts']) / ins:.4f}"

    missing = sorted({r["n"] for r in rows} - set(base))
    if missing:
        print(f"AVISO: falta la corrida escalar para N = {', '.join(missing)}", file=sys.stderr)

    out = args.output or args.csv
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    def key(r):
        return (int(f(r["n"]) or 0), int(f(r.get("vl")) or 0))

    print(f"\n{'N':>4} {'kernel':>7} {'VL':>5} {'ciclos':>12} {'instr.':>11} {'IPC':>6} "
          f"{'speedup':>8} {'ideal':>6} {'efic.':>6} {'red.inst':>9}", file=sys.stderr)
    for r in sorted(rows, key=key):
        if r.get("roi_ok", "1") != "1":
            continue
        print(f"{r['n']:>4} {r.get('kernel',''):>7} {r.get('vl',''):>5} "
              f"{int(f(r['cycles'])):>12} {int(f(r['sim_insts'])):>11} {f(r['ipc']):>6.3f} "
              f"{r['speedup']:>8} {r['ideal_speedup']:>6} {r['vec_efficiency']:>6} "
              f"{r['inst_reduction']:>9}", file=sys.stderr)
    print(f"\nEscrito: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
