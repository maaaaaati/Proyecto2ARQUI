#!/usr/bin/env python3
"""
parse_stats.py — convierte los stats.txt de gem5 en un CSV (una fila por corrida).

Uso:
    python3 scripts/parse_stats.py results/e1                 > results/e1/e1.csv
    python3 scripts/parse_stats.py results/e1 -o results/e1/e1.csv
    python3 scripts/parse_stats.py results/e2 --extra 'rob\\.reads' --extra 'iq\\.'

Cómo funciona
-------------
* Busca recursivamente cada carpeta que tenga un stats.txt.
* Toma SOLO el bloque de la ROI. Con m5_reset_stats() al inicio y m5_dump_stats()
  al final de la región de interés, gem5 escribe:
      bloque 1  -> desde el reset hasta el dump  = la ROI   <- este usamos
      bloque 2  -> desde el dump hasta el fin del programa (verificación, etc.)
  Si un stats.txt tiene un solo bloque, el programa no marcó la ROI: se avisa
  por stderr y la fila queda con roi_ok = 0 (no la uses en el informe).
* Si la carpeta tiene un archivo run.meta (líneas clave=valor, lo escriben los
  scripts run_eX.sh), esas claves se agregan como columnas (cpu, n, threads, ...).
* Métricas multinúcleo: los contadores (fallos, accesos, instrucciones) se suman
  sobre todos los núcleos; los ciclos se toman del núcleo con más ciclos.

Sin dependencias externas (solo la biblioteca estándar de Python).
"""
import argparse
import csv
import os
import re
import sys

BEGIN = "---------- Begin Simulation Statistics ----------"
END = "---------- End Simulation Statistics   ----------"

# cpu, cpu0, cpu1, ... (se.py nombra system.cpu con 1 núcleo y system.cpuN con varios)
CPU = r"system\.cpu\d*"


def read_blocks(path):
    """Devuelve una lista de dicts {nombre_stat: valor} (uno por bloque)."""
    blocks, cur = [], None
    with open(path, errors="replace") as f:
        for line in f:
            if line.startswith("---------- Begin"):
                cur = {}
            elif line.startswith("---------- End"):
                if cur is not None:
                    blocks.append(cur)
                cur = None
            elif cur is not None:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        cur[parts[0]] = float(parts[1])
                    except ValueError:
                        pass  # valores como "nan" en formato raro, distribuciones, etc.
    return blocks


def read_meta(folder):
    meta = {}
    p = os.path.join(folder, "run.meta")
    if os.path.isfile(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    meta[k.strip()] = v.strip()
    return meta


def total(st, pattern):
    """Suma todas las stats cuyo nombre calza con el regex (anclado)."""
    rx = re.compile("^" + pattern + "$")
    vals = [v for k, v in st.items() if rx.match(k)]
    return sum(vals) if vals else None


def maximum(st, pattern):
    rx = re.compile("^" + pattern + "$")
    vals = [v for k, v in st.items() if rx.match(k)]
    return max(vals) if vals else None


def ratio(a, b):
    if a is None or b in (None, 0):
        return None
    return a / b


def metrics(st):
    m = {}
    m["sim_ticks"] = st.get("simTicks")
    m["sim_seconds"] = st.get("simSeconds")
    m["sim_insts"] = st.get("simInsts")
    m["sim_ops"] = st.get("simOps")
    m["cycles"] = maximum(st, CPU + r"\.numCycles")
    m["ipc"] = ratio(m["sim_insts"], m["cycles"])          # IPC agregado del sistema
    m["cpi"] = ratio(m["cycles"], m["sim_insts"])

    # Caches clásicas (se.py --caches --l2cache)
    for lvl, pat in (("l1d", CPU + r"\.dcache"), ("l1i", CPU + r"\.icache"),
                     ("l2", r"system\.l2")):
        miss = total(st, pat + r"\.overallMisses::total")
        acc = total(st, pat + r"\.overallAccesses::total")
        # gem5 no imprime stats que valen 0: si la cache tuvo accesos pero no
        # aparece la línea de fallos, es porque hubo 0 fallos.
        if acc is not None and miss is None:
            miss = 0.0
        m[lvl + "_misses"] = miss
        m[lvl + "_accesses"] = acc
        m[lvl + "_miss_rate"] = ratio(miss, acc)

    # O3 (quedan vacías con TimingSimple / Minor)
    m["branch_mispredicts"] = total(st, CPU + r"\.commit\.branchMispredicts")
    m["rob_full_events"] = total(st, CPU + r"\.rename\.ROBFullEvents")
    m["iq_full_events"] = total(st, CPU + r"\.rename\.IQFullEvents")
    return m


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else f"{v:.6g}"
    return str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="+", help="carpetas con corridas (se recorren recursivamente)")
    ap.add_argument("-o", "--output", help="archivo CSV de salida (por defecto, stdout)")
    ap.add_argument("--block", type=int, default=1,
                    help="bloque de stats a usar (1 = ROI, por defecto)")
    ap.add_argument("--extra", action="append", default=[], metavar="REGEX",
                    help="agrega como columnas todas las stats cuyo nombre contenga este regex "
                         "(repetible). Ej.: --extra 'ruby.*Invalidat'")
    args = ap.parse_args()

    rows = []
    for root in args.roots:
        for folder, _, files in sorted(os.walk(root)):
            if "stats.txt" not in files:
                continue
            path = os.path.join(folder, "stats.txt")
            blocks = read_blocks(path)
            if not blocks:
                print(f"[aviso] {path}: vacío (¿la simulación falló?)", file=sys.stderr)
                continue
            roi_ok = len(blocks) >= 2
            if not roi_ok:
                print(f"[aviso] {path}: un solo bloque, no se detectó la ROI", file=sys.stderr)
            idx = min(args.block, len(blocks)) - 1
            st = blocks[idx]

            row = {"run": os.path.relpath(folder, root), "roi_ok": int(roi_ok)}
            row.update(read_meta(folder))
            row.update(metrics(st))
            for rx in args.extra:
                r = re.compile(rx)
                for k, v in st.items():
                    if r.search(k):
                        row[k] = v
            rows.append(row)

    if not rows:
        sys.exit("No se encontró ningún stats.txt en: " + " ".join(args.roots))

    # columnas en orden de aparición
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    w = csv.writer(out)
    w.writerow(cols)
    for r in rows:
        w.writerow([fmt(r.get(c)) for c in cols])
    if args.output:
        out.close()
        print(f"{len(rows)} corridas -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
