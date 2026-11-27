# Arquitecturas paralelas para la multiplicación de matrices en gem5

**Proyecto 2 — Arquitectura de Computadores**

Simulación y evaluación de arquitecturas de procesamiento para la multiplicación de matrices densas (*General Matrix Multiplication*, GEMM), utilizando gem5 en modo **System Emulation (SE)**, arquitectura **ARMv8-A** y extensiones vectoriales **SVE**.

La operación evaluada es:

$$
C = A \times B
$$

Las matrices utilizan elementos de precisión simple (`float`, 32 bits).

El proyecto estudia el impacto de diferentes características microarquitectónicas sobre el rendimiento, incluyendo modelos de CPU, paralelismo a nivel de instrucciones, vectorización, procesamiento multinúcleo, coherencia de caché y eficiencia computacional.

---

## 1. Entorno de desarrollo

| Elemento | Configuración |
|---|---|
| Simulador | gem5 26.0.0.0 |
| Rama de gem5 | `stable` |
| Commit de referencia | `9d368896ce119c17e1289dcbb18f33624724b843` |
| Directorio de instalación | `~/gem5` |
| Arquitectura simulada | ARMv8-A |
| Modo de simulación | SE |
| Extensión vectorial | ARM SVE |
| Variante MESI | `build/ARM_MESI` — `MESI_Two_Level` |
| Variante MOESI | `build/ARM_MOESI` — `MOESI_CMP_directory` |
| Compilador cruzado | `aarch64-linux-gnu-gcc` |
| Enlace de benchmarks | Estático |
| Entorno de referencia | WSL 2 con Ubuntu 24.04 |
| Entorno alternativo utilizado | Ubuntu 26.04 LTS nativo |

### 1.1. Compilación de gem5

El proyecto utiliza gem5 26.0.0.0, que incorpora un sistema de configuración basado en Kconfig.

Por esta razón, el comando tradicional:

```bash
scons ... --default=ARM PROTOCOL=...
```

no corresponde al procedimiento utilizado para esta versión.

Para obtener gem5:

```bash
git clone --branch stable https://github.com/gem5/gem5.git ~/gem5
```

Para compilar las variantes requeridas:

```bash
nohup bash scripts/build_gem5.sh 4 > ~/build_gem5.log 2>&1 &
```

El argumento `4` indica la cantidad de trabajos de compilación en paralelo.

### 1.2. Compilación de benchmarks

Desde la raíz del repositorio:

```bash
make
```

Se generan los ejecutables correspondientes a gem5 y QEMU.

Para ejecutar las pruebas funcionales:

```bash
make test
```

Los ejecutables de gem5 incorporan instrumentación de regiones de interés (*Region of Interest*, ROI), utilizando `libm5.a`.

---

## 2. Organización del repositorio

```text
Proyecto2ARQUI/
│
├── src/
│   ├── gemm_scalar.c
│   ├── gemm_sve.c
│   ├── gemm_omp.c
│   └── false_sharing.c
│
├── configs/
│   └── Configuraciones de simulación gem5
│
├── scripts/
│   ├── build_gem5.sh
│   ├── common.sh
│   ├── run_e1.sh
│   ├── run_e2.sh
│   ├── run_e3.sh
│   ├── run_e4.sh
│   ├── run_e5.sh
│   ├── run_e6.sh
│   ├── parse_stats.py
│   ├── plot.py
│   ├── amdahl.py
│   ├── e3_speedup.py
│   └── e6_cost.py
│
├── results/
│   ├── e1/
│   ├── e2/
│   ├── e3/
│   ├── e4/
│   ├── e5/
│   └── e6/
│
├── Informe/
│   ├── informe.tex
│   └── informe.pdf
│
├── report/
│   └── Evidencias del proyecto
│
└── minutas/
    └── Minutas de reuniones
```

Cada carpeta de resultados contiene las estadísticas y los archivos de salida correspondientes a las simulaciones ejecutadas.

---

## 3. Experimentos

El proyecto contempla seis experimentos principales.

### E1. Comparación de modelos de CPU

Se evalúa el comportamiento de tres modelos de procesador:

- `TimingSimpleCPU`
- `MinorCPU`
- `DerivO3CPU`

Las simulaciones utilizan el benchmark escalar GEMM con tamaños de matriz:

$$
N \in \{64,128\}
$$

Las métricas analizadas incluyen:

- Ciclos de ejecución.
- Instrucciones por ciclo (IPC).
- Ciclos por instrucción (CPI).
- Fallos de caché L1D.

**Ejecución:**

```bash
bash scripts/run_e1.sh
```

**Resultados:**

```text
results/e1/e1.csv
results/e1/e1_ipc.png
```

### E2. Evaluación del ancho superescalar y del ROB

Se analiza el efecto del paralelismo a nivel de instrucciones utilizando el modelo `DerivO3CPU`.

Se consideran los siguientes parámetros:

**Ancho superescalar:**

$$
W \in \{1,2,4,8\}
$$

**Capacidad del Reorder Buffer (ROB):**

$$
ROB \in \{32,64,192\}
$$

Se utiliza GEMM escalar con:

$$
N=128
$$

Esto produce un total de:

$$
4 \times 3 = 12
$$

configuraciones experimentales.

Las métricas estudiadas incluyen:

- IPC.
- Ciclos de ejecución.
- Eventos de saturación del ROB.
- Eventos de saturación de la cola de instrucciones (IQ).
- Fallos de predicción de saltos.

**Ejecución:**

```bash
bash scripts/run_e2.sh
```

**Resultados:**

```text
results/e2/e2.csv
results/e2/e2_analysis.csv
results/e2/e2_counters_verified.csv
results/e2/e2_ipc.png
results/e2/e2_cycles.png
```

Los resultados permiten estudiar la relación entre el ancho del procesador, la capacidad de las estructuras internas y el rendimiento obtenido.

### E3. Vectorización mediante ARM SVE

Se evalúa el impacto de la vectorización sobre la multiplicación de matrices.

Se compara la implementación escalar con la implementación vectorial SVE.

Las métricas incluyen:

- Tiempo de ejecución.
- Speedup.
- Speedup ideal.
- Eficiencia vectorial.
- Reducción de instrucciones.
- IPC.

El speedup ideal se calcula a partir de la longitud vectorial:

$$
S_{\mathrm{ideal}}=\frac{VL}{32}
$$

donde `VL` corresponde a la longitud vectorial en bits.

**Ejecución:**

```bash
bash scripts/run_e3.sh
```

**Resultados:**

```text
results/e3/e3.csv
results/e3/e3_speedup.png
results/e3/e3_insts.png
results/e3/e3_ipc.png
```

### E4. Procesamiento multinúcleo

Se evalúa el rendimiento de GEMM utilizando múltiples núcleos de procesamiento.

El benchmark utiliza `pthreads` para distribuir el trabajo entre los núcleos.

Se estudian:

- Speedup.
- Eficiencia paralela.
- Fracción serial.
- Fallos de caché L2.

**Ejecución:**

```bash
bash scripts/run_e4.sh
```

**Resultados:**

```text
results/e4/e4.csv
results/e4/e4_speedup.png
results/e4/e4_efficiency.png
results/e4/e4_l2_misses.png
```

También se dispone de un modo que incluye la inicialización y la creación y espera de los hilos dentro de la ROI:

```bash
MODE=full bash scripts/run_e4.sh
```

Los resultados se almacenan en:

```text
results/e4_full/
```

### E5. Coherencia de caché

Se estudia el comportamiento de las arquitecturas multinúcleo bajo diferentes protocolos de coherencia.

Las variantes disponibles son:

- MESI: `MESI_Two_Level`.
- MOESI: `MOESI_CMP_directory`.

El experimento permite analizar el impacto del protocolo de coherencia y del tráfico asociado sobre el comportamiento de memoria.

Los detalles específicos de ejecución y los resultados deben consultarse en el script correspondiente:

```bash
bash scripts/run_e5.sh
```

### E6. Exploración del espacio de diseño

Se comparan configuraciones que combinan:

- Número de núcleos.
- Ancho superescalar.
- Longitud vectorial SVE.
- Protocolo de coherencia.

El objetivo es estudiar el compromiso entre rendimiento y costo arquitectónico.

**Ejecución:**

```bash
bash scripts/run_e6.sh
```

**Resultados:**

```text
results/e6/e6.csv
results/e6/e6_time.png
results/e6/e6_perf_cost.png
```

Las configuraciones se especifican mediante:

```text
núcleos:ancho:VL[:protocolo]
```

Los protocolos admitidos son:

- `classic`: sistema de memoria clásico.
- `mesi`: Ruby con MESI.
- `moesi`: Ruby con MOESI.

Ejemplo:

```bash
CONFIGS="4:4:256 2:8:512 8:2:128:moesi" \
bash scripts/run_e6.sh
```

Las corridas se acumulan en `results/e6/`, permitiendo incorporar nuevas configuraciones sin repetir las existentes.

---

## 4. Reproducción de resultados

Los experimentos utilizan scripts que automatizan la ejecución de gem5 y el procesamiento de resultados.

| Experimento | Script | Archivo principal |
|---|---|---|
| E1 | `run_e1.sh` | `results/e1/e1.csv` |
| E2 | `run_e2.sh` | `results/e2/e2.csv` |
| E3 | `run_e3.sh` | `results/e3/e3.csv` |
| E4 | `run_e4.sh` | `results/e4/e4.csv` |
| E5 | `run_e5.sh` | Según configuración del experimento |
| E6 | `run_e6.sh` | `results/e6/e6.csv` |

### 4.1. Variables de ejecución

Los scripts admiten las siguientes variables opcionales:

| Variable | Función |
|---|---|
| `JOBS=4` | Número de simulaciones paralelas |
| `VARIANT=ARM_MESI` | Seleccionar variante MESI |
| `VARIANT=ARM_MOESI` | Seleccionar variante MOESI |
| `GEM5=~/gem5` | Directorio de instalación de gem5 |
| `FORCE=1` | Repetir simulaciones existentes |

Por defecto, las corridas que ya contienen un archivo `stats.txt` se omiten.

### 4.2. Regiones de interés

Las métricas se obtienen exclusivamente de la región de interés (ROI).

El script `parse_stats.py` utiliza el primer bloque de estadísticas correspondiente a la ROI.

Cuando no se encuentra una ROI válida, el procesamiento genera una advertencia y establece:

```text
roi_ok=0
```

Esto permite identificar simulaciones cuyos resultados no deben utilizarse directamente en las comparaciones.

---

## 5. Scripts de procesamiento

| Script | Función |
|---|---|
| `common.sh` | Funciones compartidas para ejecutar simulaciones y controlar el paralelismo |
| `parse_stats.py` | Extracción de estadísticas de gem5 y generación de CSV |
| `plot.py` | Generación de gráficas a partir de archivos CSV |
| `amdahl.py` | Cálculo de speedup, eficiencia y métricas relacionadas con la ley de Amdahl |
| `e3_speedup.py` | Análisis de speedup y eficiencia de vectorización SVE |
| `e6_cost.py` | Evaluación de rendimiento y costo arquitectónico |

### 5.1. Archivos de evidencia

Cada simulación puede generar:

```text
stats.txt
cmd.txt
run.meta
config.ini
config.json
sim.log
```

Los archivos principales son:

- `stats.txt`: estadísticas producidas por gem5.
- `cmd.txt`: comando utilizado para ejecutar la simulación.
- `run.meta`: metadatos de ejecución.
- `config.ini` y `config.json`: configuración del sistema simulado.
- `sim.log`: registro de ejecución.

Algunos archivos generados automáticamente pueden estar excluidos del control de versiones mediante `.gitignore`.

---

## 6. Consideraciones de implementación

### 6.1. Configuración del procesador O3

Los scripts configuran los siguientes parámetros:

```text
fetchWidth
decodeWidth
renameWidth
issueWidth
commitWidth
```

No se recomienda fijar `wbWidth` en valores de 1 o 2, debido a un problema observado en gem5 v26 que provoca el error:

```text
TimeBuffer out-of-bounds
```

asociado a `IEW::instToCommit`.

### 6.2. Paralelismo con pthreads

El archivo `src/gemm_omp.c` utiliza `pthreads` en lugar de OpenMP.

Su sintaxis es:

```bash
gemm_omp N T [full]
```

donde:

- `N`: dimensión de las matrices.
- `T`: número de hilos.
- `full`: incluye inicialización y gestión de hilos en la ROI.

En gem5 se requieren `T` núcleos para ejecutar los hilos correspondientes.

### 6.3. GEMM multinúcleo con SVE

El ejecutable `gemm_omp_sve` combina el reparto de trabajo mediante hilos con el kernel vectorial SVE.

Se compila utilizando:

```text
-DUSE_SVE
```

La longitud vectorial se configura en gem5 en unidades de 128 bits.

Por ejemplo:

```bash
--param 'system.cpu[:].isa[:].sve_vl_se=2'
```

corresponde a:

$$
VL=256\text{ bits}
$$

---

## 7. Informe técnico

El informe se encuentra en:

```text
Informe/informe.tex
Informe/informe.pdf
```

Se utiliza el formato IEEE en LaTeX.

El informe presenta:

1. Metodología experimental.
2. Configuración del entorno de simulación.
3. Resultados de los experimentos.
4. Análisis comparativo.
5. Discusión de limitaciones.
6. Conclusiones.

Las figuras y tablas del documento se generan mediante herramientas de LaTeX, incluyendo TikZ y PGFPlots cuando corresponde.

La extensión máxima establecida es de **8 páginas**.

---

## 8. Flujo de trabajo colaborativo

El proyecto utiliza Git y GitHub para administrar las contribuciones de los integrantes.

### 8.1. Ramas de desarrollo

Cada integrante trabaja en una rama independiente:

```text
integrante1/experimentos-e1-e2
integrante2/benchmarks
integrante3/infra
```

Las modificaciones deben integrarse mediante Pull Requests.

### 8.2. Revisión cruzada

Antes de integrar los cambios en `main`, debe realizarse la revisión cruzada correspondiente.

La revisión contempla:

- Scripts de ejecución.
- Resultados experimentales.
- Archivos CSV.
- Interpretación de estadísticas.
- Conclusiones técnicas.
- Reproducibilidad.

No se deben realizar commits directamente sobre `main`.

### 8.3. Uso de inteligencia artificial

Todo resultado obtenido con apoyo de herramientas de inteligencia artificial generativa debe:

1. Verificarse mediante simulaciones propias.
2. Contrastarse con las estadísticas producidas por gem5.
3. Documentarse en la bitácora del proyecto.

---

## 9. Estado de integración

Los experimentos E1 y E2 fueron desarrollados en la rama:

```text
integrante1/experimentos-e1-e2
```

El commit de integración es:

```text
44cd67f
```

Incluye:

- Resultados experimentales.
- Estadísticas originales.
- Archivos CSV.
- Gráficas auxiliares.
- Script de ejecución de E2.
- Actualización del informe técnico.

La integración en `main` se gestiona mediante el **Pull Request #2**, pendiente de revisión y aprobación.

---

## 10. Repositorio

**Proyecto2ARQUI**

Repositorio colaborativo del Proyecto 2 de Arquitectura de Computadores.

La documentación, los scripts y los resultados experimentales se mantienen bajo control de versiones para facilitar la reproducibilidad y la revisión del trabajo.
