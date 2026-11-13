# Análisis

Scripts que produjeron los valores de referencia del SPEC. No son el código de la app: el agente implementa `scripts/procesar_historico.py` (§7.7) en el hito 2.

| Script | Qué hace | Uso, desde la raíz |
|---|---|---|
| `indicadores_historicos.py` | Calcula los indicadores del panel histórico y del Anexo D desde las fuentes | `python analisis/indicadores_historicos.py data/fuentes/valores_cuota_v2.csv data/fuentes/uf_fin_de_mes_v1.csv` |
| `cotejar_tabla_referencia.py` | Comprueba que la tabla de referencia de §7.7 coincida con lo calculado (tolerancia 0,05 puntos) | `python analisis/cotejar_tabla_referencia.py SPEC.md` |
| `cotejo_cmf.py` | Compara la base de valores cuota con un archivo de la CMF en una fecha (Anexo D.8) | `python analisis/cotejo_cmf.py data/fuentes/valores_cuota_v2.csv data/fuentes/cmf_cotejo/ffmm_todos_20221231_20221231.txt 20221231` |
| `verificar_reglas_catalogo_v3.py` | Ejecuta los ejemplos de selección (§7.4) y de simulación (§7.5) con el catálogo v3 | `python analisis/verificar_reglas_catalogo_v3.py` |

Requieren `pip install -r requirements-verificacion.txt`.
