# Arquitecturas paralelas para la multiplicación de matrices en gem5

Proyecto de grupo · Arquitectura de Computadoras · GEMM (C = A × B, precisión simple) en gem5, modo SE, ARMv8 + SVE.

## Entorno

| Elemento | Versión |
|---|---|
| gem5 | 26.0.0.0 · rama `stable` · commit `9d368896ce119c17e1289dcbb18f33624724b843`, clonado en `~/gem5` |
| Variantes | `build/ARM_MESI` (MESI_Two_Level) y `build/ARM_MOESI` (MOESI_CMP_directory) |
| Compilador cruzado | `aarch64-linux-gnu-gcc` (Ubuntu 24.04), enlace estático |
| Host | WSL 2 · Ubuntu 24.04 |

### Compilar gem5

gem5 v26 usa Kconfig: el comando `scons ... --default=ARM PROTOCOL=...` del enunciado ya no funciona.

```bash
git clone --branch stable https://github.com/gem5/gem5.git ~/gem5
nohup bash scripts/build_gem5.sh 4 > ~/build_gem5.log 2>&1 &   # 4 = trabajos en paralelo
```

### Compilar los benchmarks

```bash
make          # bin/gem5/* (con ROI, requiere libm5.a) y bin/qemu/*
make test     # valida en QEMU
```

## Estructura

```
src/       gemm_scalar.c, gemm_sve.c, gemm_omp.c, false_sharing.c
configs/   scripts de configuración de gem5
scripts/   build_gem5.sh, run_e1.sh … run_e6.sh, parse_stats.py, plot.py
results/   una carpeta por corrida (stats.txt) + CSV
report/    informe IEEE y evidencias
minutas/   minutas de reuniones
```

## Reproducción

Un comando por experimento corre las simulaciones, genera el CSV (solo la ROI) y los gráficos.
Las corridas que ya tienen `stats.txt` se saltan (`FORCE=1` para repetirlas).

| Experimento | Comando | Salida |
|---|---|---|
| E1 | `bash scripts/run_e1.sh` | `results/e1/e1.csv`, `results/e1/e1_ipc.png` |
| E4 | `bash scripts/run_e4.sh` | `results/e4/e4.csv` (con speedup, eficiencia, fracción serial), `e4_speedup.png`, `e4_efficiency.png`, `e4_l2_misses.png` |

Variables opcionales para cualquier `run_eX.sh`: `JOBS=4` (simulaciones en paralelo),
`VARIANT=ARM_MESI` o `ARM_MOESI`, `GEM5=~/gem5`, `FORCE=1`.

### Scripts comunes

| Script | Para qué |
|---|---|
| `scripts/common.sh` | Funciones compartidas: `run_sim` lanza una corrida en su carpeta con `run.meta` (metadatos) y `cmd.txt`; controla el paralelismo |
| `scripts/parse_stats.py` | `stats.txt` → CSV. Usa solo el **bloque 1** (ROI); avisa y marca `roi_ok=0` si no hay ROI. `--extra REGEX` agrega stats específicas (p. ej. Ruby) |
| `scripts/plot.py` | Gráfico de barras o líneas desde el CSV (`--x --y --hue --where --ideal --order`) |
| `scripts/amdahl.py` | Agrega a un CSV speedup, eficiencia, fracción serial de Karp-Flatt y el ajuste de Amdahl (referencia: 1 núcleo, mismo N) |

`src/gemm_omp.c` usa **pthreads** (no OpenMP, que suele fallar en modo SE). Uso: `gemm_omp N T`;
en gem5 requiere `-n T` núcleos. La ROI excluye la creación de hilos (barreras antes y después).

Para un experimento nuevo, copiar `run_e1.sh` y cambiar el bucle y los parámetros de `run_sim`.

## Flujo de trabajo

- Nadie hace commit directo a `main`: cada integrante trabaja en su rama (`integranteN/tema`) y la aprueba el revisor cruzado por pull request.
- Todo resultado obtenido con ayuda de IA generativa se verifica con una simulación propia y se declara en la bitácora.
