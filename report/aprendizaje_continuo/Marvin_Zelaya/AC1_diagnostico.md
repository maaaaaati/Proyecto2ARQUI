# AC1 — Diagnóstico inicial de competencias

**Estudiante:** Marvin Zelaya  
**Curso:** EL4314 — Arquitectura de Computadores  
**Proyecto:** Arquitecturas paralelas para la multiplicación de matrices en gem5  
**Fecha de referencia:** 14 de noviembre de 2026

> Documento reconstruido retrospectivamente a partir del diagnóstico
> personal realizado al comenzar las actividades del proyecto.

## 1. Objetivo

Identificar los conocimientos y habilidades disponibles al iniciar el
proyecto, con el propósito de reconocer las principales necesidades de
aprendizaje y establecer metas de formación.

## 2. Escala de evaluación

| Nivel | Descripción |
|---|---|
| 0 | Sin conocimientos previos. |
| 1 | Conocimientos básicos o principalmente teóricos. |
| 2 | Conocimientos intermedios que permiten desarrollar actividades con apoyo de documentación. |
| 3 | Dominio suficiente para trabajar de forma autónoma. |

## 3. Matriz inicial de competencias

| Competencia | Nivel | Justificación |
|---|---:|---|
| Uso y configuración de gem5 | 1 | Conocía la finalidad general del simulador, pero no tenía experiencia utilizándolo. |
| Arquitectura ARMv8-A | 0 | No contaba con conocimientos específicos de esta arquitectura. |
| Extensiones ARM SVE | 0 | No había estudiado ni utilizado estas extensiones vectoriales. |
| Programación en C | 2 | Contaba con conocimientos intermedios de programación. |
| Compilación cruzada | 2 | Tenía conocimientos intermedios sobre compilación para distintas arquitecturas. |
| Jerarquía de memoria y coherencia | 2 | Conocía los fundamentos teóricos estudiados en Arquitectura de Computadores. |
| Paralelismo a nivel de instrucciones | 2 | Comprendía conceptos como segmentación, ejecución superescalar y fuera de orden. |
| Análisis de IPC, CPI y rendimiento | 2 | Conocía las métricas teóricas, pero no tenía experiencia práctica analizándolas mediante gem5. |

## 4. Análisis del diagnóstico

El diagnóstico inicial permitió identificar que las principales
necesidades de aprendizaje estaban relacionadas con el uso práctico
de gem5 y el conocimiento de la arquitectura ARMv8-A.

Aunque existía una base teórica de arquitectura de computadores,
era necesario trasladar estos conocimientos a un entorno de
simulación microarquitectónica.

La principal dificultad prevista consistía en configurar el simulador,
ejecutar experimentos reproducibles y relacionar las estadísticas
obtenidas con el comportamiento interno de los procesadores.

## 5. Brechas prioritarias

Se identificaron tres áreas principales:

1. Aprender a configurar, compilar y ejecutar gem5 en modo SE.
2. Comprender experimentalmente el efecto del ancho superescalar
   y la capacidad del ROB sobre el rendimiento.
3. Aprender a extraer, verificar e interpretar estadísticas de
   simulación para elaborar conclusiones técnicas justificadas.

## 6. Conclusión

El diagnóstico permitió establecer un punto de partida para el
aprendizaje individual. Se identificó la necesidad de complementar
los conocimientos teóricos con experiencia práctica en simulación
microarquitectónica y análisis experimental.
