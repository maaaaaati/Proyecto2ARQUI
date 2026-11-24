#!/usr/bin/env python3
"""
e6_cost.py — agrega costo y rendimiento/costo a un CSV de parse_stats.py (E6).

Uso:
    python3 scripts/e6_cost.py results/e6/e6.csv          # reescribe el CSV
    python3 scripts/e6_cost.py results/e6/e6.csv -o otro.csv

Requiere columnas: cores, width, vl (bits), n y sim_ticks (tiempo de la ROI en ps).

Columnas agregadas:
    cost           = cores * (width/2 + vl/128)        modelo de costo del enunciado
    time_ms        = tiempo simulado de la ROI en milisegundos
    gflops         = 2*N^3 / tiempo / 1e9               (GEMM hace N^3 multiplicaciones
                                                         y N^3 sumas)
    gflops_per_cost = gflops / cost                     rendimiento por unidad de costo
    config         = etiqueta corta "8n·w2·vl128" para los gráficos
Imprime en stderr la tabla ordenada por tiempo y avisa si alguna supera 32.
"""
import argparse
import csv
import sys

PRESUPUESTO = 32


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

    for r in rows:
        c, w, vl, n = (f(r.get(k)) for k in ("cores", "width", "vl", "n"))
        # simSeconds sale con solo 6 decimales (0.000138); simTicks es exacto (1 tick = 1 ps)
        ticks = f(r.get("sim_ticks"))
        t = ticks / 1e12 if ticks else f(r.get("sim_seconds"))
        if None in (c, w, vl, n):
            continue
        cost = c * (w / 2 + vl / 128)
        r["cost"] = f"{cost:g}"
        prot = r.get("protocol", "")
        r["config"] = f"{int(c)}n·w{int(w)}·vl{int(vl)}" + (f"·{prot}" if prot not in ("", "classic") else "")
        if t and r.get("roi_ok", "1") == "1":
            gflops = 2 * n ** 3 / t / 1e9
            r["time_ms"] = f"{t * 1e3:.6g}"
            r["gflops"] = f"{gflops:.6g}"
            r["gflops_per_cost"] = f"{gflops / cost:.6g}"

    ok = [r for r in rows if "time_ms" in r]
    ok.sort(key=lambda r: f(r["time_ms"]))
    print(f"{'configuración':<22} {'costo':>5} {'tiempo [ms]':>12} {'GFLOP/s':>9} {'GFLOP/s/costo':>14}",
          file=sys.stderr)
    for r in ok:
        aviso = "  <-- EXCEDE EL PRESUPUESTO" if f(r["cost"]) > PRESUPUESTO else ""
        print(f"{r['config']:<22} {r['cost']:>5} {r['time_ms']:>12} {r['gflops']:>9} "
              f"{r['gflops_per_cost']:>14}{aviso}", file=sys.stderr)
    if ok:
        mejor_t = ok[0]
        mejor_rc = max(ok, key=lambda r: f(r["gflops_per_cost"]))
        print(f"Mejor por tiempo: {mejor_t['config']}  ·  "
              f"mejor por rendimiento/costo: {mejor_rc['config']}", file=sys.stderr)

    for c in ("config", "cost", "time_ms", "gflops", "gflops_per_cost"):
        if c not in cols:
            cols.append(c)
    with open(args.output or args.csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
