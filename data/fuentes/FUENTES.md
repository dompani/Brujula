# Fuentes de datos

Archivos usados por el panel histórico (§7.7 del SPEC) y por el análisis del Anexo D. Se verifican con `sha256sum -c SHA256SUMS` desde esta carpeta y no se editan a mano.

| Archivo | Contenido | Procedencia | SHA-256 |
|---|---|---|---|
| `valores_cuota_v2.csv` | Valores cuota diarios de 9 fondos mutuos (3 administradoras × 3 perfiles propios), del 01-11-2019 al 31-10-2026: 23.013 filas; columnas `FECHA_INF`, `ADMINISTRADORA`, `PERFIL`, `RUN_FM`, `SERIE`, `NOMBRE`, `VALOR_CUOTA`; separador `;` | Información pública de la CMF (cartola diaria de fondos mutuos), preparada por Keith Watt; versión 2 recibida el 06-11-2026 (nombre original `Basedato_AGF_PR_VC_test.csv`). Cotejada con la CMF el 07-11-2026: 27 de 27 valores coinciden (SPEC, Anexo D.8) | `4214630e7de9ac6e0a2d4b80cb225d0ce89d7bbdab9075fbe39c11d68a768902` |
| `uf_fin_de_mes_v1.csv` | UF del último día de cada mes, de octubre de 2019 a octubre de 2026 (85 valores) | Tablas anuales de la UF del Servicio de Impuestos Internos, consultadas el 06-11-2026; verificada por muestreo (SPEC §7.7) | `c55524ffe9e239d1e2337d1723e275cd24b0c33651ea68a6c8484bcb39cb3fe1` |
| `cmf_cotejo/ffmm_todos_20191101_20191101.txt` | Cartola diaria de todos los fondos mutuos, 01-11-2019 | Herramienta pública «Cartola diaria por fondo» de la CMF, descargada el 07-11-2026 | `8be083fd5fd9a37ffcaa378f9fba1ac6f2b4cac8e56bd22c6c4ffc499db5b3bb` |
| `cmf_cotejo/ffmm_todos_20221231_20221231.txt` | Cartola diaria de todos los fondos mutuos, 31-12-2022 | Ídem | `8ec846fd4c02f41f90c38270ba5983847f0a8f72efe205365c23d5cc8326f2fb` |
| `cmf_cotejo/ffmm_todos_20261031_20261031.txt` | Cartola diaria de todos los fondos mutuos, 31-10-2026 | Ídem | `1ffb40c27fe6ab2b48b7721c26886e92576fc9ebc7e71b7c92f0f97dd6fd67d6` |

**Uso permitido en la app.** Solo agregados por categoría (conservador, moderado y agresivo, según la clasificación de cada administradora). Los nombres de administradoras y fondos y los RUN están aquí para reproducir el cálculo; la app no los muestra ni los envía al modelo (§7.7).

**Limitaciones.** El cotejo con la CMF es una muestra de 3 fechas; las series no son homogéneas (APV en dos administradoras, B y B1 en la tercera); el valor cuota no incluye impuestos ni beneficios tributarios (Anexo D.6).

**Publicación.** Decisión del grupo del 12-11-2026: `docs/decisiones/0009-repositorio-publico.md`.
