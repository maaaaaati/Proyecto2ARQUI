#!/bin/bash
# E2 — Ancho superescalar y tamaño del ROB.
# GEMM escalar, ArmO3CPU, un núcleo, cachés L1 + L2.
#
# Uso:
#   bash scripts/run_e2.sh
#   WIDTHS="1" ROBS="32" bash scripts/run_e2.sh
#
# Variables:
#   WIDTHS: anchos a evaluar (1 2 4 8)
#   ROBS: tamaños del ROB (32 64 192)
#   N: tamaño de matriz (128 por defecto)
#   JOBS: simulaciones simultáneas

source "$(dirname "$0")/common.sh"
check_gem5

WIDTHS="${WIDTHS:-1 2 4 8}"
ROBS="${ROBS:-32 64 192}"
N="${N:-128}"

BIN="$REPO/bin/gem5/gemm_scalar"
OUT="$REPO/results/e2"

[ -x "$BIN" ] || {
    echo "ERROR: falta $BIN"
    exit 1
}

echo "======================================"
echo " EXPERIMENTO E2"
echo "======================================"
echo "CPU: ArmO3CPU"
echo "Matriz: N=$N"
echo "Anchos: $WIDTHS"
echo "ROB: $ROBS"
echo "Paralelismo: $JOBS"
echo "======================================"

for width in $WIDTHS; do
    for rob in $ROBS; do

        params=()

        for p in fetchWidth decodeWidth renameWidth issueWidth commitWidth; do
            params+=(--param "system.cpu[:].$p=$width")
        done

        params+=(--param "system.cpu[:].numROBEntries=$rob")

        run_sim "$OUT/w${width}_rob${rob}_n${N}" \
            "exp=e2 cpu=o3 width=$width rob=$rob n=$N cores=1" \
            --cpu-type=ArmO3CPU \
            --caches --l2cache \
            "${params[@]}" \
            -c "$BIN" -o "$N"

    done
done

wait_all

python3 "$REPO/scripts/parse_stats.py" "$OUT" -o "$OUT/e2.csv"

echo "======================================"
echo " E2 FINALIZADO"
echo " Resultados: $OUT/e2.csv"
echo "======================================"
