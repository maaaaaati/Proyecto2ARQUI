#!/bin/bash
# run_e6.sh — E6, exploración de arquitecturas bajo el presupuesto de costo 32.
#   GEMM paralelo con SVE (gemm_omp_sve), N = 128, hilos = núcleos, O3.
#   Costo = núcleos * (ancho/2 + VL/128) <= 32
#
# Uso (desde la raíz del repo):
#   bash scripts/run_e6.sh                       # configuraciones por defecto (abajo)
#   CONFIGS="4:4:256 2:8:512" bash scripts/run_e6.sh
#   CONFIGS="8:2:128:mesi 8:2:128:moesi" bash scripts/run_e6.sh   # con Ruby
#
# Cada configuración es  núcleos:ancho:VL[:protocolo]
#   ancho      1, 2, 4 u 8 (fetch, decode, rename, issue y commit del O3)
#   VL         128 a 1024 bits (múltiplo de 128)
#   protocolo  classic (por defecto: caches clásicas, L1 privadas + L2 compartida),
#              mesi (Ruby, MESI_Two_Level) o moesi (Ruby, MOESI_CMP_directory)
# Las corridas se acumulan en results/e6/: agregar configuraciones nuevas no
# repite las que ya existen, y el CSV y los gráficos incluyen todas.
#
# Salida:
#   results/e6/<config>/stats.txt
#   results/e6/e6.csv               (+ costo, tiempo, GFLOP/s y GFLOP/s por costo)
#   results/e6/e6_time.png          tiempo de la ROI por configuración
#   results/e6/e6_perf_cost.png     rendimiento por unidad de costo

source "$(dirname "$0")/common.sh"

# Integrante 3: muchos núcleos simples (ancho 2, VL mínimo). El resto del grupo
# agrega aquí sus configuraciones, cada una justificada por un resultado de E2-E5.
CONFIGS="${CONFIGS:-8:2:128 16:2:128}"
N="${N:-128}"
CPU="${CPU:-ArmO3CPU}"
BIN="$REPO/bin/gem5/gemm_omp_sve"
OUT="${OUT:-$REPO/results/e6}"

[ -x "$BIN" ] || { echo "Falta $BIN. Compílalo con: make"; exit 1; }

echo "E6: N = $N · configuraciones: $CONFIGS · $JOBS en paralelo"
for cfg in $CONFIGS; do
    IFS=: read -r cores width vl prot <<<"$cfg"
    prot="${prot:-classic}"
    if (( vl % 128 != 0 || vl < 128 || vl > 1024 )); then
        echo "  VL inválido en $cfg (128..1024, múltiplo de 128)"; exit 1
    fi
    cost=$(python3 -c "print(f'{$cores * ($width / 2 + $vl / 128):g}')")
    if python3 -c "import sys; sys.exit(0 if $cost > 32 else 1)"; then
        echo "  AVISO: $cfg cuesta $cost (> 32), se corre igual pero no es válida para la propuesta"
    fi

    # El O3 trae todos los anchos en 8; se fijan los 5 del enunciado (no wbWidth,
    # ver run_e4.sh). La VL se fija en unidades de 128 bits.
    params=()
    for p in fetchWidth decodeWidth renameWidth issueWidth commitWidth; do
        params+=(--param "system.cpu[:].$p=$width")
    done
    params+=(--param "system.cpu[:].isa[:].sve_vl_se=$(( vl / 128 ))")

    case "$prot" in
        classic) VARIANT=ARM_MESI;  mem=(--caches --l2cache) ;;
        mesi)    VARIANT=ARM_MESI;  mem=(--ruby) ;;
        moesi)   VARIANT=ARM_MOESI; mem=(--ruby) ;;
        *) echo "  protocolo desconocido en $cfg (classic, mesi o moesi)"; exit 1 ;;
    esac
    GEM5_BIN="$GEM5/build/$VARIANT/gem5.opt"
    check_gem5

    run_sim "$OUT/c${cores}_w${width}_vl${vl}_${prot}" \
        "exp=e6 cpu=o3 cores=$cores threads=$cores width=$width vl=$vl protocol=$prot n=$N" \
        -n "$cores" --cpu-type="$CPU" "${mem[@]}" "${params[@]}" \
        -c "$BIN" -o "$N $cores"
done
wait_all

python3 "$REPO/scripts/parse_stats.py" "$OUT" -o "$OUT/e6.csv"
python3 "$REPO/scripts/e6_cost.py" "$OUT/e6.csv"
python3 "$REPO/scripts/plot.py" "$OUT/e6.csv" --x config --y time_ms --kind bar \
    --where roi_ok=1 --ylabel "Tiempo de la ROI [ms]" --xlabel "Configuración" \
    --title "E6 · Tiempo de GEMM (N = $N)" -o "$OUT/e6_time.png"
python3 "$REPO/scripts/plot.py" "$OUT/e6.csv" --x config --y gflops_per_cost --kind bar \
    --where roi_ok=1 --ylabel "GFLOP/s por unidad de costo" --xlabel "Configuración" \
    --title "E6 · Rendimiento por unidad de costo (N = $N)" -o "$OUT/e6_perf_cost.png"
