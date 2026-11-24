#!/bin/bash
# run_e1.sh — E1, línea base de un núcleo.
#   3 modelos de CPU (TimingSimple, Minor, O3) × N = 64, 128 = 6 corridas.
#   GEMM escalar, 1 núcleo, caches clásicas L1 + L2.
#
# Uso (desde la raíz del repo):
#   bash scripts/run_e1.sh                 # las 6 corridas + CSV + gráfico
#   CPUS="ArmTimingSimpleCPU" bash scripts/run_e1.sh   # solo un modelo
#
# Salida:
#   results/e1/<cpu>_n<N>/stats.txt   (una carpeta por corrida)
#   results/e1/e1.csv                 (una fila por corrida, solo la ROI)
#   results/e1/e1_ipc.png             (IPC por CPU y tamaño)

source "$(dirname "$0")/common.sh"
check_gem5

CPUS="${CPUS:-ArmTimingSimpleCPU ArmMinorCPU ArmO3CPU}"
SIZES="${SIZES:-64 128}"
BIN="$REPO/bin/gem5/gemm_scalar"
OUT="$REPO/results/e1"

[ -x "$BIN" ] || { echo "Falta $BIN. Compílalo con: make"; exit 1; }

echo "E1: CPUs = $CPUS · N = $SIZES · $JOBS en paralelo"
for cpu in $CPUS; do
    for n in $SIZES; do
        short="${cpu#Arm}"; short="${short%CPU}"; short="${short,,}"   # ArmO3CPU -> o3
        run_sim "$OUT/${short}_n${n}" "exp=e1 cpu=$short n=$n cores=1" \
            --cpu-type="$cpu" --caches --l2cache \
            -c "$BIN" -o "$n"
    done
done
wait_all

python3 "$REPO/scripts/parse_stats.py" "$OUT" -o "$OUT/e1.csv"
python3 "$REPO/scripts/plot.py" "$OUT/e1.csv" --x cpu --y ipc --hue n \
    --kind bar --where roi_ok=1 --order timingsimple,minor,o3 \
    --title "E1 · IPC por modelo de CPU" -o "$OUT/e1_ipc.png"
