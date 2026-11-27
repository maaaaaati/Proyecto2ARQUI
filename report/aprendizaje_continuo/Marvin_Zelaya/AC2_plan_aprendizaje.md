# AC2 — Plan individual de aprendizaje

**Estudiante:** Marvin Zelaya  
**Curso:** EL4314 — Arquitectura de Computadores  
**Proyecto:** Arquitecturas paralelas para la multiplicación de matrices en gem5  
**Fecha de referencia:** 14 de noviembre de 2026

> Plan reconstruido retrospectivamente a partir de las necesidades
> identificadas al iniciar el proyecto.

## 1. Objetivo

Establecer metas de aprendizaje medibles que permitan superar
las principales brechas identificadas en el diagnóstico inicial.

## 2. Brechas y metas

| Brecha | Nivel inicial | Meta medible | Fecha objetivo | Evidencia |
|---|---:|---|---|---|
| Uso práctico de gem5 | 1 | Configurar gem5 y ejecutar al menos una simulación ARMv8-A en modo SE. | 20/11/2026 | Registros de ejecución y `stats.txt`. |
| Evaluación de arquitecturas superescalares | 2 | Ejecutar las 12 configuraciones de E2 y comparar su rendimiento. | 25/11/2026 | CSV y estadísticas de E2. |
| Análisis experimental | 2 | Procesar resultados de E1 y E2 e integrarlos en el informe técnico. | 25/11/2026 | Scripts, CSV, informe y Pull Request. |

## 3. Estrategias de aprendizaje

### 3.1. Investigación técnica

Consultar documentación sobre gem5, sus modelos de CPU y los
parámetros utilizados para configurar simulaciones ARMv8-A.

### 3.2. Aprendizaje mediante experimentación

Realizar pruebas progresivas, comenzando por configuraciones
sencillas y posteriormente ejecutando los experimentos completos.

### 3.3. Análisis de estadísticas

Examinar los archivos `stats.txt` para identificar las métricas
relevantes y comprobar los resultados procesados.

### 3.4. Resolución de dificultades

Investigar y documentar los problemas de compilación, configuración
y ejecución, así como las soluciones implementadas.

## 4. Tecnologías relacionadas con el proyecto

### 4.1. ARM Scalable Vector Extension (SVE)

ARM SVE permite implementar operaciones vectoriales mediante
longitudes de vector escalables.

Su estudio es relevante para comprender el paralelismo de datos
en aplicaciones de cálculo intensivo, como la multiplicación
de matrices.

**Aplicación en el proyecto:** experimentos relacionados con
vectorización y evaluación de rendimiento.

**Fuente:** documentación oficial de Arm.

### 4.2. Simulación microarquitectónica con gem5

gem5 permite evaluar modelos de procesador, jerarquías de memoria
y configuraciones microarquitectónicas sin implementar físicamente
cada alternativa.

**Aplicación en el proyecto:** evaluación experimental de E1 y E2.

**Fuente:** documentación oficial de gem5.

## 5. Criterios de cumplimiento

Se considerarán evidencias de aprendizaje:

- Un entorno funcional de gem5.
- Simulaciones ARMv8-A con estadísticas válidas.
- Las doce configuraciones de E2.
- Archivos CSV con los resultados.
- Interpretación técnica de IPC y ciclos.
- Integración de resultados en el repositorio.

## 6. Conclusión

El plan de aprendizaje se orientó a transformar conocimientos
teóricos en habilidades prácticas de simulación y análisis
microarquitectónico, mediante actividades verificables.
