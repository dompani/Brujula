# 0010. Golden set: la versión 1.7 del prompt reemplaza a la 1.5

- **Fecha:** 12-11-2026
- **Decide:** Regla de §11.3 (vía de robustez, calibración reutilizada); cierre del grupo
- **SPEC:** §9.1, §9.6, §11.3 y Anexo E.8

## Contexto

La primera comparación mostró que la tarea de explicación de la 1.5 no indica qué `next_step` usar, por lo que casi siempre necesita reparación. La 1.7 agrega una sola frase que lo fija. Se comparó con la 1.5 en los mismos 24 casos, con 3 ejecuciones, el mismo juez y la calibración humana de la primera comparación.

## Decisión

La 1.7 reemplaza a la 1.5 por la vía de robustez: validez sin reparación 95,8 % frente a 2,8 %, plantilla 0 % frente a 4,2 %, calidad +0,03 (mínimo −0,10), costo estimado −50 % y ninguna alerta. `prompt_version=1.7` es la vigente.

## Consecuencias

`prompts/system_brujula_v1_7.txt` es el prompt que usa la app. Si la app usa un modelo distinto del que usó la herramienta, el golden set se repite con él (§8.5). La lista de V-04 podría distinguir «el mayor riesgo de las tres» de «el mayor riesgo» como declaración de un riesgo principal; queda como mejora posible.
