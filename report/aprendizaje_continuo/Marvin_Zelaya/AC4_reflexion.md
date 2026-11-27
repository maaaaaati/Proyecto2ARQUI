# AC4 — Reflexión crítica individual sobre el aprendizaje

**Estudiante:** Marvin Zelaya  
**Curso:** EL4314 — Arquitectura de Computadores  
**Proyecto:** Arquitecturas paralelas para la multiplicación de matrices en gem5  
**Fecha:** 26 de noviembre de 2026

## 1. Objetivo

Evaluar críticamente el proceso de aprendizaje desarrollado durante
el proyecto, comparando las competencias iniciales con las adquiridas,
analizando la eficacia de las estrategias utilizadas e identificando
oportunidades de mejora para futuros proyectos tecnológicos.

## 2. Comparación de competencias

Se utilizó la misma escala del diagnóstico inicial:

- **0:** Sin conocimientos previos.
- **1:** Conocimientos básicos o principalmente teóricos.
- **2:** Conocimientos intermedios.
- **3:** Capacidad para trabajar de forma autónoma.

| Competencia | Inicial | Final | Variación |
|---|---:|---:|---:|
| Uso y configuración de gem5 | 1 | 2 | +1 |
| Arquitectura ARMv8-A | 0 | 2 | +2 |
| Extensiones ARM SVE | 0 | 1 | +1 |
| Programación en C | 2 | 2 | 0 |
| Compilación cruzada | 2 | 3 | +1 |
| Jerarquía de memoria y coherencia | 2 | 2 | 0 |
| Paralelismo a nivel de instrucciones | 2 | 3 | +1 |
| Análisis de IPC, CPI y rendimiento | 2 | 3 | +1 |

**Nota:** Los niveles finales corresponden a una autoevaluación
provisional basada en las actividades desarrolladas hasta el
26 de noviembre de 2026.

## 3. Análisis de la evolución

### 3.1. Uso de gem5

Al comenzar el proyecto conocía gem5 principalmente desde
una perspectiva teórica, pero no tenía experiencia práctica
configurando ni ejecutando simulaciones.

Durante el desarrollo aprendí a preparar el entorno, trabajar
con distintos modelos de CPU y ejecutar experimentos para
obtener estadísticas de rendimiento.

El principal avance consistió en comprender el procedimiento
necesario para realizar experimentos reproducibles y verificar
sus resultados.

### 3.2. Arquitectura ARMv8-A y SVE

Inicialmente no contaba con conocimientos específicos de ARMv8-A
ni de sus extensiones vectoriales SVE.

La investigación y preparación del entorno permitieron
familiarizarme con esta arquitectura, su compilación cruzada
y su utilización en gem5.

En el caso de SVE, el aprendizaje fue principalmente conceptual,
ya que mis responsabilidades experimentales se concentraron
en E1 y E2.

Por esta razón, considero que todavía necesito profundizar
en la programación y evaluación de aplicaciones vectorizadas.

### 3.3. Paralelismo a nivel de instrucciones

Uno de los aprendizajes más importantes se relacionó con
el comportamiento de las arquitecturas superescalares.

En el experimento E2 evalué doce configuraciones del procesador
DerivO3CPU, modificando el ancho superescalar y la capacidad
del búfer de reordenamiento (ROB).

Los resultados permitieron observar que aumentar los recursos
microarquitectónicos no garantiza mejoras proporcionales
en el rendimiento.

Esto fortaleció mi comprensión de los cuellos de botella,
la saturación de recursos y las limitaciones del paralelismo
a nivel de instrucciones.

### 3.4. Análisis de rendimiento

Antes del proyecto conocía conceptos como IPC y CPI, pero
no tenía experiencia interpretando estas métricas a partir
de simulaciones realizadas con gem5.

El procesamiento de los resultados de E1 y E2 me permitió
relacionar las estadísticas con las características
microarquitectónicas de cada configuración.

También aprendí la importancia de verificar las estadísticas
originales antes de elaborar conclusiones.

## 4. Evaluación crítica de las estrategias de aprendizaje

| Estrategia | Evaluación | Evidencia |
|---|---|---|
| Investigación de documentación técnica | Eficaz | Permitió comprender los requisitos de gem5 y preparar el entorno de simulación. |
| Aprendizaje mediante experimentación | Muy eficaz | Se completaron las configuraciones de E1 y las doce de E2. |
| Análisis y verificación de estadísticas | Eficaz | Se obtuvieron archivos CSV y se integraron resultados en el informe. |
| Resolución progresiva de problemas técnicos | Eficaz, pero costosa en tiempo | Se superaron dificultades de memoria durante la compilación mediante ajustes al entorno y uso de swap adicional. |
| Planificación inicial del tiempo | Mejorable | La preparación del simulador requirió más esfuerzo del previsto debido a las limitaciones del equipo. |

### 4.1. Estrategias que funcionaron

La experimentación fue la estrategia más útil porque permitió
comprobar directamente el efecto de los parámetros
microarquitectónicos sobre el rendimiento.

También resultó importante combinar la consulta de documentación
con la ejecución de comandos y la revisión de estadísticas.

Este procedimiento permitió transformar conceptos teóricos
en conocimientos aplicados.

### 4.2. Estrategias que deben mejorar

La principal dificultad estuvo relacionada con la planificación
del tiempo necesario para preparar y compilar gem5.

Mi computadora dispone de recursos limitados, por lo que
algunas compilaciones requirieron bastante tiempo y presentaron
problemas por consumo de memoria.

Aunque fue posible continuar mediante ajustes al entorno,
habría sido conveniente evaluar los requisitos de hardware
desde el inicio y reservar más tiempo para la instalación
y las pruebas preliminares.

## 5. Evaluación de las metas de aprendizaje

| Meta | Estado | Justificación |
|---|---|---|
| Configurar gem5 y ejecutar simulaciones ARMv8-A | Cumplida | Se preparó el entorno y se ejecutaron experimentos con estadísticas válidas. |
| Ejecutar las doce configuraciones de E2 | Cumplida | Se evaluaron las combinaciones de ancho superescalar y ROB previstas. |
| Procesar e integrar resultados de E1 y E2 | Cumplida | Se organizaron resultados y se incorporaron al informe técnico. |

Las metas técnicas correspondientes a mis experimentos
se cumplieron.

Sin embargo, el proceso de aprendizaje continúa, especialmente
en aspectos relacionados con ARM SVE y con la interpretación
de estadísticas microarquitectónicas más avanzadas.

## 6. ¿Qué haría diferente ante una nueva tecnología?

Si tuviera que comenzar otro proyecto utilizando una tecnología
desconocida, realizaría los siguientes cambios:

1. **Evaluar los requisitos de hardware desde el inicio.**
   Comprobaría la memoria, el almacenamiento y el tiempo
   aproximado necesario para compilar y ejecutar las herramientas.

2. **Preparar un ejemplo mínimo funcional.**
   Antes de desarrollar los experimentos completos, ejecutaría
   una prueba sencilla para verificar la instalación y la
   configuración del entorno.

3. **Definir hitos intermedios.**
   Separaría el trabajo en instalación, primera ejecución,
   automatización, experimentación y análisis.

4. **Documentar los problemas conforme aparecen.**
   Mantendría un registro de errores, soluciones y comandos
   utilizados para evitar repetir procedimientos.

5. **Reservar tiempo para verificar resultados.**
   Consideraría la revisión de estadísticas y la
   reproducibilidad como parte fundamental del experimento,
   no como una actividad secundaria.

## 7. Uso responsable de inteligencia artificial

Durante el proyecto utilicé herramientas de inteligencia
artificial generativa para apoyar la investigación,
la resolución de problemas técnicos y la documentación.

Esta asistencia resultó útil para identificar posibles
soluciones y comprender procedimientos desconocidos.

Sin embargo, aprendí que las recomendaciones deben
verificarse mediante pruebas reales y documentación técnica.

Los resultados experimentales utilizados en el informe
proceden de simulaciones ejecutadas con gem5 y no de
valores generados artificialmente.

## 8. Evidencias del aprendizaje

Las principales evidencias se encuentran en el repositorio:

- Scripts de ejecución de E1 y E2.
- Archivos CSV con resultados experimentales.
- Estadísticas generadas por gem5.
- Análisis técnico incorporado al informe.
- Commit `44cd67f`.
- Pull Request #2.
- Bitácora individual AC3.

## 9. Conclusión

El desarrollo del proyecto permitió fortalecer mis competencias
en simulación microarquitectónica, paralelismo a nivel de
instrucciones y análisis de rendimiento.

El aprendizaje más significativo fue comprender cómo las
decisiones de diseño de un procesador influyen en su
rendimiento y cómo evaluar estas decisiones mediante
experimentos reproducibles.

También adquirí experiencia enfrentando dificultades
técnicas relacionadas con la compilación y los recursos
de hardware disponibles.

Considero que el proyecto contribuyó a mejorar mi capacidad
para aprender herramientas desconocidas, resolver problemas
de manera sistemática y fundamentar conclusiones mediante
evidencia experimental.
