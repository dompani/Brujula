# 0008. Calibración humana reutilizada en la segunda comparación

- **Fecha:** 12-11-2026
- **Decide:** Grupo 2
- **SPEC:** §11.3

## Contexto

La segunda comparación (1.5 frente a 1.7) usa el mismo juez, rúbrica y modelo que la primera, en la que el juez coincidió con el promedio humano en 24 de 24 salidas; la 1.7 solo agrega una frase a la tarea.

## Decisión

No se hace puntuación humana nueva: se reutiliza la calibración de la primera comparación. Con calibración reutilizada decide el juez y solo vale la vía de robustez.

## Consecuencias

Si cambian el juez, la rúbrica o el modelo, o una candidata reescribe ampliamente la tarea o busca la vía de calidad, la puntuación humana vuelve.
