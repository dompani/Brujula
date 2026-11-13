# 0006. Golden set: la versión 1.6 del prompt no se adopta

- **Fecha:** 12-11-2026
- **Decide:** Regla de §11.3; alerta revisada por Daphne Loewenwarter
- **SPEC:** §9.6, §11.3 y Anexo E

## Contexto

Primera comparación del golden set: 24 casos × 2 versiones × 3 ejecuciones, juez a ciegas y puntuación humana de Keith Watt y Diego Silva.

## Decisión

Se mantiene la 1.5. La 1.6 cumplió seguridad, robustez (72,2 % de validez sin reparación frente a 1,4 %) y costo (−14 %), pero su calidad subió 0,28 puntos y la regla exigía 0,30. La única alerta, sobre una explicación automática sin IA, se descartó.

## Consecuencias

Hallazgo: la tarea de la 1.5 no indica qué `next_step` usar. Da origen a la candidata 1.7 y a la pregunta 16.
