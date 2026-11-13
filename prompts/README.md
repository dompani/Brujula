# Prompts

| Archivo | Versión | Estado | Referencia |
|---|---|---|---|
| `system_brujula_v1_5.txt` | 1.5 | Vigente | SPEC §9.1 |
| `tarea_explicacion_v1_6.txt` y `ejemplos_explicacion_v1_6.json` | 1.6 | Evaluada el 12-11-2026; no adoptada | SPEC §9.1, §9.6 y Anexo E |
| `tarea_explicacion_v1_7.txt` | 1.7 | Candidata; segunda comparación del golden set | SPEC §9.1 y §11.3 |

Las versiones candidatas cambian solo la línea «Explicación de la comparación» de la sección TAREAS del prompt de sistema. En la evaluación de la 1.6, la línea SALIDA también decía «Cada explicación: máximo 300 caracteres; en la explicación de la comparación, máximo 450», y los dos ejemplos se agregaron al final del prompt. La 1.7 no cambia la línea SALIDA ni usa ejemplos.

Cada cambio de prompt pasa por el golden set de §11.3 antes de reemplazar a la vigente.
