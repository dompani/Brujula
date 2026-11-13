# 0012. Proveedor de IA, presupuesto y publicación

- **Fecha:** 13-11-2026
- **Decide:** Grupo 2
- **SPEC:** §6.3, §6.7, §8.5, Anexo E.7 y §12 (pregunta 8)

## Contexto

La URL publicada debe tener la IA encendida con límite de gasto (requisito del Proyecto Final). §8.5 pide registrar aquí las condiciones antes de habilitar `LLM_MODE=real`.

## Decisión

| Condición de §8.5 | Estado |
|---|---|
| Proveedor | Anthropic (modelos Claude), el mismo con que se ejecutó el golden set |
| Modelo exacto | `claude-sonnet-5-5` (decisión 0013). El golden set se repite con él |
| Titular de las cuentas de IA y de nube | Daphne Loewenwarter (13-11-2026) |
| Presupuesto | `LLM_BUDGET_DAILY_USD=1`, `LLM_BUDGET_MONTHLY_USD=10`, `LLM_BUDGET_EVAL_USD=5`; alertas de facturación al 50, 80 y 100 % |
| Región de procesamiento de la IA | Fuera de Chile (transferencia internacional informada en el aviso de privacidad); región exacta según los términos vigentes [VERIFICAR] |
| Retención de peticiones y uso para entrenamiento | Según los términos vigentes del proveedor al abrir la cuenta [VERIFICAR] |
| Publicación | Aprobada en Cloud Run, región Santiago; reemplazada por plazo por Render, región de Oregón (decisión 0013) |

## Consecuencias

Los montos dejan de ser supuestos. Antes del hito 6 quedan pendientes el titular de las cuentas, el modelo exacto, los términos de datos y, si corresponde, el golden set con ese modelo; esta ficha se completa entonces.
