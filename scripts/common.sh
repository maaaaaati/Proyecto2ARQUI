#!/bin/bash
# common.sh — funciones compartidas por los scripts run_eX.sh.
# Se usa con:  source "$(dirname "$0")/common.sh"
#
# Variables que se pueden cambiar al llamar a cualquier run_eX.sh:
#   GEM5=~/gem5          copia de gem5
#   VARIANT=ARM_MESI     build a usar (ARM_MESI o ARM_MOESI)
#   JOBS=4               simulaciones en paralelo
#   FORCE=1              repite corridas que ya tienen stats.txt
# Ejemplo:  JOBS=6 bash scripts/run_e1.sh

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEM5="${GEM5:-$HOME/gem5}"
VARIANT="${VARIANT:-ARM_MESI}"
GEM5_BIN="$GEM5/build/$VARIANT/gem5.opt"
SE_PY="$GEM5/configs/deprecated/example/se.py"
JOBS="${JOBS:-4}"
FORCE="${FORCE:-0}"

check_gem5() {
    [ -x "$GEM5_BIN" ] || { echo "No existe $GEM5_BIN (¿terminó de compilar gem5?)"; exit 1; }
    [ -f "$SE_PY" ]    || { echo "No existe $SE_PY"; exit 1; }
}

# Espera hasta que haya menos de $JOBS simulaciones corriendo.
throttle() {
    while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n || true; done
}

# run_sim OUTDIR "clave=valor clave=valor ..." [argumentos de se.py...]
#   Lanza una simulación en segundo plano en OUTDIR, guarda la línea de comando
#   (cmd.txt), la salida (sim.log) y los metadatos (run.meta) para parse_stats.py.
run_sim() {
    local out="$1" meta="$2"; shift 2
    if [ "$FORCE" != "1" ] && [ -s "$out/stats.txt" ]; then
        echo "  ya existe: $out (FORCE=1 para repetir)"
        return
    fi
    mkdir -p "$out"
    {
        echo "# generado por $(basename "$0") el $(date -Iseconds)"
        echo "variant=$VARIANT"
        for kv in $meta; do echo "$kv"; done
    } > "$out/run.meta"
    echo "$GEM5_BIN -d $out $SE_PY $*" > "$out/cmd.txt"
    throttle
    echo "  corriendo: $out"
    (
        if "$GEM5_BIN" -d "$out" "$SE_PY" "$@" > "$out/sim.log" 2>&1; then
            echo "  listo:     $out"
        else
            echo "  FALLÓ:     $out (ver $out/sim.log)"
        fi
    ) &
}

wait_all() { wait; }
