#!/bin/bash
# run_e4.sh — E4, multiprocesador de memoria compartida.
#   GEMM paralelo por filas (gemm_omp, pthreads) con 1, 2, 4 y 8 núcleos O3 de
#   ancho 2, hilos = núcleos, N = 64 y 128. Caches clásicas: L1 privadas + L2 compartida.
#
# Uso (desde la raíz del repo):
#   bash scripts/run_e4.sh
#   CORES="1 2" SIZES=64 bash scripts/run_e4.sh      # prueba rápida
#
# Salida:
#   results/e4/c<núcleos>_n<N>/stats.txt
#   results/e4/e4.csv                (+ speedup, eficiencia, fracción serial)
#   results/e4/e4_speedup.png        (speedup vs. núcleos, con la ideal)
#   results/e4/e4_efficiency.png
#   results/e4/e4_l2_misses.png

source "$(dirname "$0")/common.sh"
check_gem5

CORES="${CORES:-1 2 4 8}"
SIZES="${SIZES:-64 128}"
CPU="${CPU:-ArmO3CPU}"
WIDTH="${WIDTH:-2}"
BIN="$REPO/bin/gem5/gemm_omp"
OUT="$REPO/results/e4"

[ -x "$BIN" ] || { echo "Falta $BIN. Compílalo con: make"; exit 1; }

# El O3 de gem5 trae todos los anchos en 8. Se fijan los 5 que lista el enunciado
# (fetch, decode, rename, issue, commit), igual que en E2.
# NO se toca wbWidth: con wbWidth=2 y 8 núcleos, gem5 v26 aborta con
# "TimeBuffer out-of-bounds" (IEW::instToCommit empuja a ciclos futuros las
# instrucciones que no caben en el writeback sin revisar el límite de la cola).
WIDTH_PARAMS=()
for p in fetchWidth decodeWidth renameWidth issueWidth commitWidth; do
    WIDTH_PARAMS+=(--param "system.cpu[:].$p=$WIDTH")
done

echo "E4: núcleos = $CORES · N = $SIZES · $CPU ancho $WIDTH · $JOBS en paralelo"
for n in $SIZES; do
    for c in $CORES; do
        run_sim "$OUT/c${c}_n${n}" "exp=e4 cpu=o3 width=$WIDTH cores=$c threads=$c n=$n" \
            -n "$c" --cpu-type="$CPU" --caches --l2cache \
            "${WIDTH_PARAMS[@]}" \
            -c "$BIN" -o "$n $c"
    done
done
wait_all

python3 "$REPO/scripts/parse_stats.py" "$OUT" -o "$OUT/e4.csv"
python3 "$REPO/scripts/amdahl.py" "$OUT/e4.csv"
python3 "$REPO/scripts/plot.py" "$OUT/e4.csv" --x cores --y speedup --hue n \
    --kind line --ideal --where roi_ok=1 \
    --title "E4 · Speedup de GEMM paralelo (O3 ancho $WIDTH)" -o "$OUT/e4_speedup.png"
python3 "$REPO/scripts/plot.py" "$OUT/e4.csv" --x cores --y efficiency --hue n \
    --kind line --where roi_ok=1 \
    --title "E4 · Eficiencia paralela" -o "$OUT/e4_efficiency.png"
python3 "$REPO/scripts/plot.py" "$OUT/e4.csv" --x cores --y l2_misses --hue n \
    --kind bar --where roi_ok=1 --ylabel "Fallos de L2" \
    --title "E4 · Fallos de L2 por número de núcleos" -o "$OUT/e4_l2_misses.png"
