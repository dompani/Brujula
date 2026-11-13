# Brújula Inversiones

Especificación de una plataforma académica de orientación de inversiones según perfil: un cuestionario reproducible, una ficha de perfil y meta, una comparación determinista de tres alternativas simuladas, un simulador de escenarios y una explicación generativa con IA, con límite de gasto y control de salida.

Grupo 2 del curso Advanced Prompt Engineering (UAI, 2026): Diego Silva, Keith Watt y Daphne Loewenwarter.

> **Demostración académica.** No recibe dinero, no ejecuta inversiones y no es asesoría financiera. Las alternativas del catálogo son simuladas; el panel histórico usa datos públicos agregados por categoría.

## Estado

- **`SPEC.md` es la única fuente de verdad.** La app todavía no está implementada: el primer paso es el hito 1 del SPEC, en el que el agente de código entrega un plan sin escribir código (ver `AGENTS.md`).
- **Versiones.** Cada versión cerrada del SPEC tiene una etiqueta `spec-vX.Y`; el historial está en `CHANGELOG.md`. Las versiones v1.0 a v1.14 están en el historial de git, cada una con su etiqueta.
- **Prompt de la explicación.** Vigente: 1.7 (`prompts/system_brujula_v1_7.txt`), adoptada el 12-11-2026 tras el golden set. Resultados en §9.6 y Anexo E del SPEC y en `evals/informe_explicacion.md`.

## Contenido

| Carpeta o archivo | Qué contiene |
|---|---|
| `SPEC.md` | Especificación completa: alcance, reglas, arquitectura, prompts, criterios de aceptación A01–A64 y anexos |
| `CHANGELOG.md` | Registro de cambios del SPEC, con un número C por cambio |
| `AGENTS.md` · `CLAUDE.md` | Instrucciones para agentes de código |
| `prompts/` | Prompt de sistema vigente y tareas de explicación evaluadas |
| `data/catalogo_demo_v3.json` | Catálogo ficticio D01–D09 (§7.2) |
| `data/fuentes/` | Valores cuota, UF y archivos del cotejo con la CMF, con procedencia y SHA-256 (`FUENTES.md`) |
| `evals/` | Golden set de la explicación: 24 casos, rúbrica, informes, resultados y puntuación humana |
| `analisis/` | Scripts que produjeron los valores de referencia del SPEC (Anexo D, §7.4 y §7.5) |
| `tools/golden_set/` | Herramienta con la que se ejecutó el golden set, como páginas de claude.ai |
| `docs/decisiones/` | Una ficha por cada decisión del grupo |
| `docs/diagramas/` | Diagramas originales del grupo (flujo de usuario y componentes) |
| `scripts/` · `tests/` | Verificaciones del SPEC y pruebas de los validadores |

## Cómo se trabaja

1. Cada cambio va en una rama y se propone con un pull request; la plantilla pide sección, motivo y número C.
2. Otro integrante revisa antes de unir. `main` está protegida.
3. Las preguntas abiertas del SPEC son issues con la etiqueta `pregunta-abierta` (`scripts/crear_issues.sh` las crea).
4. Al cerrar una versión se actualiza el encabezado del SPEC y `CHANGELOG.md`, y se crea la etiqueta `spec-vX.Y`.

Detalle en `CONTRIBUTING.md`.

## Verificaciones

GitHub Actions (`.github/workflows/verificar.yml`) ejecuta en cada pull request:

- estructura del SPEC: secciones, tablas, criterios de la suite y su asignación a hitos, referencias;
- checksums de las fuentes;
- ejemplos de selección y simulación de §7.4 y §7.5;
- reproducción de la tabla de referencia del panel histórico (§7.7) desde las fuentes;
- diagramas Mermaid;
- validadores V-01 a V-07 del golden set y coherencia entre los prompts del repositorio y los evaluados.

Para correrlas localmente:

```bash
pip install -r requirements-verificacion.txt
python scripts/verificar_spec.py SPEC.md
(cd data/fuentes && sha256sum -c SHA256SUMS)
python analisis/verificar_reglas_catalogo_v3.py
python analisis/cotejar_tabla_referencia.py SPEC.md
(cd scripts && npm ci) && node scripts/verificar_mermaid.mjs SPEC.md
node --test tests/golden_set.test.mjs
```

## Datos

Los valores cuota son información pública de la Comisión para el Mercado Financiero (CMF) y la UF proviene del Servicio de Impuestos Internos (SII). Procedencia, fechas y checksums en `data/fuentes/FUENTES.md`. Los nombres de administradoras, fondos y RUN están en los archivos fuente solo para reproducir los cálculos: la app no los muestra (§7.7).

## Licencia

Este repositorio no tiene licencia, por decisión del grupo (12-11-2026). Es público para consulta, pero sus autores no otorgan permiso para copiar, modificar ni redistribuir su contenido. Los términos de servicio de GitHub permiten ver los repositorios públicos y hacer fork dentro de GitHub. Los datos de `data/fuentes/` son información pública de la CMF y del SII y conservan las condiciones de su origen.

## Uso de IA

El SPEC, los análisis y la herramienta del golden set se elaboraron con ayuda de Claude (Anthropic). Las decisiones son del grupo y están registradas en `docs/decisiones/` y `CHANGELOG.md`.
