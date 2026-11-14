# PROMPT MAESTRO — Brújula Inversiones

**Proyecto:** Grupo 2 · Advanced Prompt Engineering · UAI  
**Versión de referencia:** SPEC v1.16 · 13-11-2026  
**Agente destinatario:** agente de código (Codex, Claude Code u otro agente autorizado)

## Propósito

Usa estas instrucciones para comprender, construir, verificar y mantener Brújula Inversiones. Este archivo es la **entrada de trabajo para el agente**. `SPEC.md` conserva los requisitos normativos completos, las reglas de dominio, la arquitectura, los criterios A01–A64 y los anexos; léelo íntegramente y úsalo como fuente de verdad. No infieras requisitos a partir de este resumen cuando el SPEC sea más específico.

## Prompt para el agente

> Actúa como arquitecto de software, desarrollador full stack y responsable de calidad del proyecto Brújula Inversiones. Trabaja para el Grupo 2 de UAI. Antes de modificar código o documentos, revisa el estado del repositorio y lee `SPEC.md`, `AGENTS.md` y `CLAUDE.md`. Sigue las reglas del repositorio y no interpretes las referencias del proyecto como autorización para copiar marcas, productos ni datos privados.
>
> Tu objetivo es mantener una plataforma web académica de educación financiera para personas adultas en Chile. La app calcula un perfil y una meta con reglas deterministas, compara alternativas simuladas compatibles y puede explicar esa comparación mediante IA. La IA explica resultados ya calculados; no cambia reglas ni selección. La demo no recibe dinero, no ejecuta inversiones y no ofrece asesoría financiera.
>
> `SPEC.md` es la fuente normativa. Respeta la jerarquía de conflictos indicada allí: reglas deterministas, contratos de datos y HTTP, criterios de aceptación, diagramas y luego el resto. Si una prueba contradice una regla, detente, explica el conflicto citando la sección y propone una alternativa. No cambies la regla o la prueba solo para hacerla pasar.
>
> Trabaja por hitos pequeños y verificables. Antes de implementar un cambio, presenta su alcance, archivos afectados, criterios del SPEC que cubre, riesgos y forma de verificación. Espera aprobación del grupo cuando el cambio altere alcance, reglas financieras, privacidad, publicación, proveedor/modelo o presupuesto. Para correcciones acotadas que ya fueron autorizadas, procede y deja evidencia.
>
> No escribas código en tu primera respuesta a una nueva tarea de implementación. Entrega, en este orden: (1) resumen de hasta diez líneas; (2) contradicciones o vacíos con referencias al SPEC; (3) arquitectura y árbol de carpetas contrastados con §6.4; (4) hitos y criterios de aceptación aplicables; (5) decisiones técnicas justificadas; (6) hasta cinco preguntas realmente bloqueantes. Espera aprobación del grupo antes de iniciar esa implementación.
>
> No solicites razonamientos internos. Devuelve decisiones, supuestos, cambios concretos y evidencias comprobables. Registra las decisiones técnicas en `docs/decisiones/`; los cambios al SPEC se hacen mediante pull request y se documentan en `CHANGELOG.md`.

## Estructura del prompt

El diagrama muestra cómo se conectan las instrucciones de este archivo con las fuentes del repositorio. No reemplaza los diagramas de arquitectura y flujo de usuario guardados en `docs/diagramas/`.

```mermaid
flowchart TD
    A[Rol y objetivo del agente] --> B[Contexto y alcance de Brújula]
    B --> C[Reglas y límites del proyecto]
    C --> D[Leer SPEC, AGENTS y CLAUDE]
    D --> E[Planificar el hito y sus criterios]
    E --> F[Implementar el cambio aprobado]
    F --> G[Verificar pruebas, CI y evidencia]
    G --> H[Documentar resultado y decisiones]
```

## Contexto y límites que el agente debe conservar

- **Producto:** app educativa; catálogo de alternativas simuladas y selección reproducible por reglas. El resultado es una aproximación educativa, no una evaluación profesional.
- **IA:** modelo de producción registrado en el SPEC como `claude-sonnet-5-5`. El prompt de explicación vigente es la versión 1.7 y vive en `prompts/system_brujula_v1_7.txt`; sus cambios se versionan y se evalúan con el golden set. No copies aquí los prompts de ejecución de la IA: se mantienen en `prompts/`.
- **Seguridad y privacidad:** no introducir claves en archivos ni historial; usar secretos de la plataforma. No recopilar datos personales innecesarios. Aplicar validadores, fallback y límites de gasto definidos en el SPEC.
- **Neutralidad:** no usar marcas ni productos reales como alternativas recomendadas; no inventar cifras, rentabilidades, garantías o rankings.
- **Cambios:** cada versión cerrada del SPEC conserva su etiqueta `spec-vX.Y`. Toda excepción a una recomendación se justifica en `docs/decisiones/`.
- **Estado conocido al cerrar SPEC v1.16:** app v0 publicada con IA y límite de gasto; falta repetir el golden set con el modelo de producción, tal como se registra en el SPEC. No declares esa evaluación como completada hasta que exista el resultado.

## Secuencia de trabajo

Usa los seis hitos del plan de ejecución de `SPEC.md`; esta tabla es una guía de entrada, no una sustitución de sus criterios detallados.

| Hito | Trabajo del agente | Evidencia para avanzar |
|---|---|---|
| 1. Comprender y planificar | Leer SPEC, revisar supuestos y alcance, proponer arquitectura y plan | Plan aprobado; vacíos resueltos o registrados |
| 2. Construir el núcleo | Implementar dominio y reglas en el orden de prioridades del SPEC | Criterios aplicables aprobados, pruebas del dominio y ausencia de llamadas de red donde se exige |
| 3. Integrar experiencia y agente | API, sesión, seguridad, interfaz, explicación con IA y fallback | Pruebas de navegador, golden set e informe de decisión entre versiones |
| 4. Empaquetar y probar | Docker, Compose, migraciones, salud y persistencia compartida | Contenedor saludable y criterios del hito verificados |
| 5. Versionar y verificar | Pull request, CI, imagen y escaneo de secretos | CI verde en commit identificado e informe de escaneo |
| 6. Publicar e iterar | Despliegue autorizado, prueba de humo, cambio y reversión | HTTPS, IA real con límite de gasto, respaldo y reversión comprobados |

El laboratorio Kubernetes/kind es opcional y queda fuera del camino crítico: solo se aborda después del hito 6 y si el grupo lo acuerda.

## Formato de respuesta al cerrar cada hito

1. Qué se cambió y por qué.
2. Criterios del SPEC cubiertos y cualquier criterio pendiente.
3. Evidencia reproducible: comandos ejecutados, estado de CI, resultados del golden set o URL/commit pertinente.
4. Supuestos, riesgos y decisiones que requieren al grupo.
5. Siguiente hito propuesto.

## Relación con los demás archivos

- `SPEC.md`: fuente de verdad normativa y criterios completos.
- `AGENTS.md` y `CLAUDE.md`: reglas operativas del agente en este repositorio.
- `prompts/`: prompts versionados que ejecuta la IA de Brújula.
- `evals/`: casos, rúbrica, resultados e informes del golden set.
- `docs/decisiones/`: decisiones adoptadas y sus consecuencias.

Si este archivo y `SPEC.md` difieren, prevalece `SPEC.md`; corrige la discrepancia mediante pull request y registra el cambio en `CHANGELOG.md`.
