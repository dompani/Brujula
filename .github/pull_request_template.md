## Qué cambia

<!-- Una o dos frases. -->

## Sección del SPEC

<!-- Por ejemplo: §9.3, §11.3, Anexo E. -->

## Hallazgo o decisión que lo motiva

<!-- Quién lo decidió y cuándo; enlaza el issue si existe. -->

## Registro

- [ ] Entrada en `CHANGELOG.md` con su número C (por ejemplo, C112)
- [ ] Si se cierra una versión: encabezado del SPEC actualizado y, al unir, etiqueta `spec-vX.Y`
- [ ] Si es una decisión del grupo: ficha en `docs/decisiones/`

## Verificaciones

- [ ] `python scripts/verificar_spec.py SPEC.md` sin errores
- [ ] Diagramas Mermaid sin errores
- [ ] Si cambia un prompt: golden set ejecutado y resultado en §9.6
- [ ] Si cambian archivos de `data/fuentes/`: `SHA256SUMS` y `FUENTES.md` actualizados
- [ ] Sin secretos, correos personales ni material del curso
