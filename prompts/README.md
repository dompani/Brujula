# Prompts

| Archivo | Versión | Estado | Referencia |
|---|---|---|---|
| `system_brujula_v1_7.txt` | 1.7 | **Vigente desde el 12-11-2026** (adoptada por la vía de robustez) | SPEC §9.1, §9.6 y Anexo E.8 |
| `system_brujula_v1_5.txt` | 1.5 | Reemplazada por la 1.7 | SPEC §9.6 |
| `tarea_explicacion_v1_7.txt` | 1.7 | Tarea de explicación de la 1.7; ya incluida en `system_brujula_v1_7.txt` | SPEC §9.1 |
| `tarea_explicacion_v1_6.txt` y `ejemplos_explicacion_v1_6.json` | 1.6 | Evaluada el 12-11-2026; no adoptada | SPEC §9.1, §9.6 y Anexo E |

La 1.7 es la 1.5 con una sola frase nueva en la tarea de explicación: «Usa tipo "personalizada" y next_step "ver_comparacion"». La 1.6 cambiaba la tarea completa, la línea SALIDA («Cada explicación: máximo 300 caracteres; en la explicación de la comparación, máximo 450») y agregaba dos ejemplos al final del prompt.

Cada cambio de prompt es una versión candidata y pasa por el golden set de §11.3 antes de reemplazar a la vigente.
