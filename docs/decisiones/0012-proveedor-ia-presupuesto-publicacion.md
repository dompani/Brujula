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
| Modelo exacto | Se registra al abrir la cuenta. Si no es el que usó la herramienta del golden set, el golden set se repite con él |
| Titular de las cuentas de IA y de nube | Un integrante que el grupo designa antes del hito 6 |
| Presupuesto | `LLM_BUDGET_DAILY_USD=1`, `LLM_BUDGET_MONTHLY_USD=10`, `LLM_BUDGET_EVAL_USD=5`; alertas de facturación al 50, 80 y 100 % |
| Región de procesamiento de la IA | Fuera de Chile (transferencia internacional informada en el aviso de privacidad); región exacta según los términos vigentes [VERIFICAR] |
| Retención de peticiones y uso para entrenamiento | Según los términos vigentes del proveedor al abrir la cuenta [VERIFICAR] |
| Publicación | Cloud Run con PostgreSQL gestionado, región `southamerica-west1` (Santiago) [VERIFICAR disponibilidad de los servicios] |

## Consecuencias

Los montos dejan de ser supuestos. Antes del hito 6 quedan pendientes el titular de las cuentas, el modelo exacto, los términos de datos y, si corresponde, el golden set con ese modelo; esta ficha se completa entonces.
