# 0007. Regla de decisión con vía de robustez

- **Fecha:** 12-11-2026
- **Decide:** Grupo 2
- **SPEC:** §11.3; pregunta 16

## Contexto

La regla solo permitía adoptar una candidata que subiera la calidad 0,3 puntos, aunque mejorara mucho la robustez.

## Decisión

Se agrega una segunda vía: una candidata que no baje la calidad más de 0,1 puntos y suba la validez sin reparación al menos 10 puntos porcentuales o baje la tasa de plantilla al menos 5 puede reemplazar a la vigente. Las condiciones de seguridad, robustez y costo siguen iguales.

## Consecuencias

Rige desde la segunda comparación. No se aplica hacia atrás a la 1.6, porque se definió después de ver sus resultados.
