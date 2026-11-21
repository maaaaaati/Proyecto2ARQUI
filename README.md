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

_(Se completa a medida que existan los scripts: un comando por experimento regenera CSV y gráficos.)_

| Experimento | Comando |
|---|---|
| E1 | `bash scripts/run_e1.sh` |

## Flujo de trabajo

- Nadie hace commit directo a `main`: cada integrante trabaja en su rama (`integranteN/tema`) y la aprueba el revisor cruzado por pull request.
- Todo resultado obtenido con ayuda de IA generativa se verifica con una simulación propia y se declara en la bitácora.
