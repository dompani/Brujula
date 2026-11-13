# Instrucciones para agentes de código

1. **`SPEC.md` es la fuente de verdad.** Léelo completo antes de actuar. Ante un conflicto, aplica su sección «Jerarquía ante conflictos».
2. **Primera respuesta sin código.** Sigue «Instrucción de uso para el agente de código» del SPEC: resumen, contradicciones o vacíos, arquitectura y árbol de carpetas (§6.4), los seis hitos con sus criterios, decisiones técnicas y hasta cinco preguntas bloqueantes. Espera la aprobación del grupo.
3. **Trabaja por hitos.** Un hito no se aprueba sin la evidencia de su fila en el plan de ejecución.
4. **No modifiques una prueba ni una regla para que pase.** Informa el conflicto y propone una alternativa (SPEC, «Jerarquía ante conflictos»).
5. **Decisiones técnicas** en `docs/decisiones/`, con fecha, contexto, decisión y consecuencias.
6. **Sin secretos en el repositorio.** Variables en `.env.example`, sin valores (§6.4). Nunca subas `LLM_API_KEY`.
7. **Prompts versionados** en `prompts/`. Todo cambio de prompt pasa por el golden set (§11.3) y se registra en §9.6.
8. **Datos fuente inmutables.** Los archivos de `data/fuentes/` se verifican con `SHA256SUMS`; no se editan a mano.
9. **Cambios al SPEC** por pull request, con entrada en `CHANGELOG.md`; al cerrar una versión, etiqueta `spec-vX.Y`.
10. **Antes de proponer cambios**, corre las verificaciones del `README.md`.
