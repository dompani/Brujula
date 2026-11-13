# Cómo contribuir

## Flujo de trabajo

1. Actualiza `main` y crea una rama con un nombre que diga qué cambia: `spec/regla-decision`, `datos/uf-2027`, `app/hito-2-dominio`.
2. Haz el cambio. Si toca el SPEC, agrega su entrada en `CHANGELOG.md`, en la versión en curso, con el siguiente número C libre.
3. Corre las verificaciones del `README.md`.
4. Abre un pull request; la plantilla pide sección, motivo, registro y verificaciones.
5. Otro integrante revisa y aprueba. Se une con «Squash and merge» para que cada cambio sea un commit en `main`.

## Mensajes de commit

Una línea en presente que diga qué cambia y por qué, por ejemplo: `SPEC §11.3: regla de reutilización de la calibración (C109)`.

## Cerrar una versión del SPEC

1. Actualiza el encabezado de `SPEC.md` (versión, fecha y resumen) y la evolución de la suite en §11.2 si cambiaron criterios.
2. Cierra la sección de la versión en `CHANGELOG.md`.
3. Une el pull request y crea la etiqueta: `git tag -a spec-vX.Y -m "SPEC vX.Y" && git push origin spec-vX.Y`.

## Decisiones del grupo

Toda decisión que cambie el alcance, los datos o la evaluación se registra en `docs/decisiones/` con el formato de las fichas existentes, y se enlaza desde el pull request que la aplica.

## Preguntas abiertas

Las preguntas de §12 que siguen abiertas son issues con la etiqueta `pregunta-abierta`. Al resolverse, el pull request que actualiza el SPEC cierra el issue.

## Prompts y golden set

Un cambio de prompt es una versión candidata: se compara con la vigente según §11.3 (24 casos, validadores, juez a ciegas y calibración humana o reutilizada) y el resultado se registra en §9.6 y en `evals/informe_explicacion.md`, aunque la candidata pierda. La herramienta está en `tools/golden_set/`.

## Datos

Los archivos de `data/fuentes/` no se editan. Una fuente nueva o actualizada entra como archivo nuevo, con su procedencia en `FUENTES.md` y su línea en `SHA256SUMS`.

## Lo que no se sube

Secretos y claves, correos o datos personales que no sean los nombres de los integrantes, y material del curso (presentaciones y PDF de la UAI).
