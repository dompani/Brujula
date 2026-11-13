# Herramienta del golden set

Páginas con las que el grupo ejecutó el golden set de la explicación (§11.3 del SPEC). Funcionan como artefactos publicados en claude.ai: usan las capacidades del entorno de claude.ai para llamar a Claude (`sample`), guardar los resultados (`db`) y descargar informes (`downloads`). Abiertas como archivo local solo muestran los casos, los prompts y la rúbrica.

| Archivo | Comparación |
|---|---|
| `paginas/golden_set_brujula_1_6.html` | 1.5 frente a 1.6 (primera comparación, 08 a 12-11-2026) |
| `paginas/golden_set_brujula_1_7.html` | 1.5 frente a 1.7 (segunda comparación, con la calibración humana reutilizada) |

## Qué hace

1. **Revisar y bloquear el protocolo:** 24 casos, los dos prompts y, en la 1.6, los dos ejemplos.
2. **Generar:** hasta 3 ejecuciones de 48 respuestas. Cada respuesta pasa por V-01 a V-07; si falla, se pide una reparación y, si vuelve a fallar, se usa la plantilla sin IA.
3. **Juez:** Claude puntúa a ciegas las dos respuestas de cada caso con la rúbrica.
4. **Puntuación humana:** externa y a ciegas (archivo generado con `src/comun/armar_paso4.js`), o reutilizada de una comparación anterior.
5. **Resultados:** métricas, calibración, alertas y la regla de decisión, con descarga del informe y de los datos.

## Código fuente

| Archivo | Uso |
|---|---|
| `src/comun/generar_casos.py` | Regenera `casos.json` con las reglas del SPEC: `python src/comun/generar_casos.py src/comun/casos.json` |
| `src/comparacion_1_X/logica.js` | Prompts, validadores, juez, métricas y regla de decisión de cada comparación |
| `src/comparacion_1_X/plantilla.html` | Interfaz de la página |
| `src/comparacion_1_X/build.py` | Arma la página: `python src/comparacion_1_7/build.py salida.html` |
| `src/comun/armar_paso4.js` | Arma el archivo de puntuación humana a ciegas desde los datos exportados |
| `src/comun/cargar_humano.py` | Valida y promedia los bloques de los evaluadores: `python src/comun/cargar_humano.py bloques.txt salida/ mapa_respuestas.json` |

Para publicar una página nueva en claude.ai se declaran las capacidades `sample`, `db` (lectura para quien vea la página y escritura para editores) y `downloads`.

## Limitaciones

El modelo lo elige la plataforma por nivel (se registra el nivel que respondió); la temperatura no se puede fijar; el prompt de sistema va al comienzo del mensaje; el costo es una estimación por largo de texto. Si la app usa otro modelo, el golden set se repite con él (§8.5).
