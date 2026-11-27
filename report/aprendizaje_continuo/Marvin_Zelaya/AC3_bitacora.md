# AC3 — Bitácora individual de aprendizaje

**Estudiante:** Marvin Zelaya  
**Curso:** EL4314 — Arquitectura de Computadores  
**Proyecto:** Arquitecturas paralelas para la multiplicación de matrices en gem5  
**Periodo:** 5 al 29 de noviembre de 2026

## 1. Objetivo

Documentar las actividades realizadas, las dificultades encontradas,
las estrategias utilizadas y los aprendizajes adquiridos durante
el desarrollo del proyecto.

## 2. Registro cronológico

| Fecha | Actividad | Descripción |
|---|---|---|
| 05/11/2026 | Repartición de labores | Se distribuyeron las responsabilidades. Me correspondieron la preparación de gem5, actividades de E1 y el liderazgo del experimento E2. |
| 14–19/11/2026 | Investigación inicial | Investigué el funcionamiento de gem5, sus modelos de CPU y los requisitos para desarrollar los experimentos asignados. |
| 20–23/11/2026 | Compilación y configuración | Trabajé en la preparación del entorno de simulación. Se presentaron dificultades por las limitaciones de memoria y procesamiento de mi computadora. |
| 24/11/2026 | Simulaciones | Continué con las ejecuciones de E1 y E2 y la recopilación de estadísticas. |
| 25/11/2026 | Análisis e integración | Analicé los resultados obtenidos, integré mi parte del informe y publiqué los cambios en el repositorio. |
| 27/11/2026 | Grabación del video (programada) | Se realizará la grabación del video de exposición del proyecto, en el cual los integrantes explicarán la metodología, los experimentos desarrollados, los resultados obtenidos y el aprendizaje adquirido durante el proceso. |
| 29/11/2026 | Revisión y entrega final (programadas) | Se realizará una revisión integral del proyecto, verificando el funcionamiento de los scripts, la organización de los resultados, la documentación, el informe técnico y el video. Posteriormente, se efectuará la entrega final. |

## 3. Registro de horas

| Actividad | Horas |
|---|---:|
| Investigación y preparación | 4 |
| Compilación y configuración | 6 |
| Ejecución de simulaciones | 3 |
| Análisis de resultados | 3 |
| **Total registrado** | **16** |

Las horas son aproximadas y corresponden al tiempo dedicado
a las actividades indicadas. No incluyen necesariamente
reuniones o tareas adicionales de coordinación.

## 4. Dificultades y soluciones

### 4.1. Limitaciones del equipo

La computadora utilizada dispone de recursos limitados para
compilar y ejecutar herramientas como gem5.

Durante la compilación se presentaron problemas de consumo
de memoria. Para continuar fue necesario ajustar el entorno
y habilitar espacio de intercambio adicional.

**Aprendizaje:** la planificación de experimentos debe considerar
las limitaciones de hardware disponibles.

### 4.2. Falta de experiencia práctica con gem5

Antes del proyecto conocía gem5 de forma teórica, pero no
había ejecutado simulaciones con esta herramienta.

Fue necesario investigar su configuración, compilación y
procedimiento de ejecución.

**Aprendizaje:** adquirí experiencia en la preparación de
entornos de simulación microarquitectónica.

### 4.3. Interpretación de estadísticas

Los resultados generados por gem5 contienen numerosas métricas.
Fue necesario identificar las estadísticas relevantes para
comparar las configuraciones de los experimentos.

**Aprendizaje:** fortalecí la capacidad de relacionar IPC,
ciclos y parámetros microarquitectónicos.

## 5. Resultados obtenidos

### 5.1. Experimento E1

Se ejecutaron configuraciones correspondientes a:

- `TimingSimpleCPU`.
- `MinorCPU`.
- `DerivO3CPU`.

Para tamaños de matriz:

- `N = 64`.
- `N = 128`.

### 5.2. Experimento E2

Se evaluaron doce configuraciones de `DerivO3CPU`.

Anchos superescalares:

- 1, 2, 4 y 8.

Capacidades del ROB:

- 32, 64 y 192 entradas.

Los resultados permitieron analizar cómo el aumento de
recursos microarquitectónicos influye en el rendimiento
y por qué pueden presentarse efectos de saturación.

### 5.3. Integración

Los resultados se organizaron en archivos CSV y se
incorporaron al informe técnico.

Se publicaron los cambios mediante el commit `44cd67f`
y el Pull Request #2 del repositorio del proyecto.

## 6. Uso de inteligencia artificial

Durante el proyecto utilicé herramientas de inteligencia
artificial generativa como apoyo para:

- Comprender la configuración y ejecución de gem5.
- Investigar errores de compilación.
- Revisar comandos y scripts.
- Organizar resultados experimentales.
- Apoyar el análisis y la redacción técnica.

Las respuestas de estas herramientas se contrastaron con
las ejecuciones realizadas y las estadísticas obtenidas
directamente mediante gem5.

## 7. Reflexión

El proyecto permitió pasar de conocimientos principalmente
teóricos sobre gem5 a la ejecución práctica de simulaciones
microarquitectónicas.

También permitió comprender que aumentar el ancho superescalar
o la capacidad del ROB no garantiza mejoras proporcionales
en el rendimiento.

Las dificultades de compilación fortalecieron mi capacidad
para investigar problemas técnicos y adaptar las estrategias
de trabajo a los recursos disponibles.

## 8. Conclusión

Las actividades desarrolladas permitieron completar las
simulaciones y el análisis de E1 y E2, además de adquirir
experiencia práctica en gem5, interpretación de estadísticas
y documentación de resultados experimentales.
