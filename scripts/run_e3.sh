#!/bin/bash
# run_e3.sh — E3, extensión vectorial SVE.
#   GEMM escalar vs. GEMM SVE con VL = 128, 256, 512 y 1024 bits, N = 64 y 128.
#   1 núcleo ArmO3CPU con sus parámetros por defecto (el mismo núcleo que E1-O3),
#   caches clásicas L1 + L2. Total: 2 escalares + 8 SVE = 10 corridas.
#
#   gemm_sve.c es agnóstico a la longitud vectorial: se usa el MISMO binario
#   para todas las VL; solo cambia el parámetro sve_vl_se de gem5
#   (en unidades de 128 bits: 1 = 128, 2 = 256, 4 = 512, 8 = 1024).
#
# Uso (desde la raíz del repo):
#   bash scripts/run_e3.sh                      # las 10 corridas + CSV + gráficos
#   VLS="256" SIZES="64" bash scripts/run_e3.sh # solo algunas
#   JOBS=2 bash scripts/run_e3.sh               # menos simulaciones a la vez (poca RAM)
#
# Salida:
#   results/e3/scalar_n<N>/ y results/e3/sve_vl<VL>_n<N>/   (stats.txt de cada corrida)
#   results/e3/e3.csv              (solo la ROI, con speedup y reducción de instrucciones)
#   results/e3/e3_speedup.png      (speedup vs. VL, con la recta ideal = carriles)
#   results/e3/e3_insts.png        (instrucciones ejecutadas en la ROI)
#   results/e3/e3_ipc.png          (IPC escalar vs. SVE)

source "$(dirname "$0")/common.sh"
check_gem5

CPU="${CPU:-ArmO3CPU}"
VLS="${VLS:-128 256 512 1024}"
SIZES="${SIZES:-64 128}"
SCALAR="$REPO/bin/gem5/gemm_scalar"
SVE="$REPO/bin/gem5/gemm_sve"
OUT="$REPO/results/e3"

for b in "$SCALAR" "$SVE"; do
    [ -x "$b" ] || { echo "Falta $b. Compílalo con: make"; exit 1; }
done

echo "E3: CPU = $CPU · VL = $VLS · N = $SIZES · $JOBS en paralelo"
for n in $SIZES; do
    # Línea base escalar (vl=0 marca "sin vector" en el CSV)
    run_sim "$OUT/scalar_n${n}" "exp=e3 cpu=o3 kernel=scalar vl=0 lanes=1 n=$n cores=1" \
        --cpu-type="$CPU" --caches --l2cache \
        -c "$SCALAR" -o "$n"

    for vl in $VLS; do
        run_sim "$OUT/sve_vl${vl}_n${n}" \
            "exp=e3 cpu=o3 kernel=sve vl=$vl lanes=$(( vl / 32 )) n=$n cores=1" \
            --cpu-type="$CPU" --caches --l2cache \
            --param "system.cpu[:].isa[:].sve_vl_se=$(( vl / 128 ))" \
            -c "$SVE" -o "$n"
    done
done
wait_all

# Comprobar que cada corrida verificó bien el resultado (gemm_* imprime OK/FALLO)
bad=0
for d in "$OUT"/*/; do
    [ -f "$d/sim.log" ] || continue
    if ! grep -q "checksum=.* OK" "$d/sim.log"; then
        echo "  ATENCIÓN: $d no imprimió OK (ver sim.log)"; bad=1
    fi
done
[ "$bad" = 0 ] && echo "  Todas las corridas verificaron el resultado (OK)."

python3 "$REPO/scripts/parse_stats.py" "$OUT" -o "$OUT/e3.csv"
python3 "$REPO/scripts/e3_speedup.py" "$OUT/e3.csv"

python3 "$REPO/scripts/plot.py" "$OUT/e3.csv" --x vl --y speedup --hue n \
    --kind line --where kernel=sve --where roi_ok=1 \
    --title "E3 · Speedup de SVE frente al código escalar" \
    --xlabel "VL (bits)" --ylabel "Speedup (ciclos escalar / ciclos SVE)" \
    -o "$OUT/e3_speedup.png"
python3 "$REPO/scripts/plot.py" "$OUT/e3.csv" --x vl --y sim_insts --hue n \
    --kind bar --where roi_ok=1 \
    --title "E3 · Instrucciones en la ROI (VL 0 = escalar)" \
    --xlabel "VL (bits)" -o "$OUT/e3_insts.png"
python3 "$REPO/scripts/plot.py" "$OUT/e3.csv" --x vl --y ipc --hue n \
    --kind bar --where roi_ok=1 \
    --title "E3 · IPC (VL 0 = escalar)" \
    --xlabel "VL (bits)" -o "$OUT/e3_ipc.png"
