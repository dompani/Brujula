# Registro de cambios del SPEC

Cada versión cerrada tiene una etiqueta `spec-vX.Y` en git. Los números C identifican cada cambio y no se reutilizan.

## v1.12 → v1.13, cerrada (12-11-2026, reutilización de la calibración humana)

| N.º | Sección | Decisión | Cambio en v1.13 |
|---|---|---|---|
| C109 | §11.3 | El grupo decidió no repetir la puntuación humana en la segunda comparación | Regla de reutilización de la calibración: juez, rúbrica y modelo sin cambios, candidata sin reescritura amplia y acuerdo previo de al menos 70 %; con calibración reutilizada decide el juez y solo vale la vía de robustez |
| C110 | §11.3, §11.2 | La segunda comparación (1.5 frente a 1.7) cumple las tres condiciones | Segunda comparación sin puntuación humana nueva, en una página propia de la herramienta, con la 1.5 generada de nuevo |
| C111 | Encabezado, plan | Cierre de la versión 1.13 | Encabezado y pendientes externos actualizados |

## v1.11 → v1.12, cerrada (12-11-2026, pregunta 16 y candidata 1.7)

| N.º | Sección | Decisión | Cambio en v1.12 |
|---|---|---|---|
| C104 | §11.3, preguntas | El grupo aceptó que una versión que no baje la calidad más de 0,1 puntos y mejore claramente la robustez pueda reemplazar a la vigente | Regla de decisión con dos vías, calidad (3a) y robustez (3b), con umbrales de 10 puntos porcentuales en validez sin reparación o 5 en tasa de plantilla [SUPUESTO]; pregunta 16 resuelta; rige desde la segunda comparación |
| C105 | §9.1, §9.6 | Candidata 1.7: la tarea de la 1.5 con tipo y `next_step` fijados | Texto de la tarea 1.7 y fila en el registro de versiones |
| C106 | §11.3, A63, §11.2 | Segunda comparación: 1.5 frente a 1.7 | Protocolo de la segunda comparación; A63 la incluye |
| C107 | Anexo E | Con la vía de robustez la 1.6 habría cumplido, pero la vía se definió después de ver sus resultados | Nota que deja la decisión de la 1.6 sin cambios |
| C108 | Encabezado, plan | Cierre de la versión 1.12 | Encabezado, pendientes externos e hito 3 actualizados |

## v1.10 → v1.11, cerrada (12-11-2026, resultado del golden set de la explicación)

| N.º | Sección | Hallazgo o decisión | Cambio en v1.11 |
|---|---|---|---|
| C96 | §9.6, §11.3, Anexo E | Primera ejecución del golden set de la explicación (08 a 12-11-2026): 24 casos × 2 versiones × 3 ejecuciones, con juez y puntuación humana | Se mantiene la 1.5: la 1.6 cumple seguridad, robustez y costo, pero su calidad sube 0,28 y la regla exige 0,30. Resultado registrado en §9.6 y en el nuevo Anexo E |
| C97 | §11.3, preguntas | La calibración humana la hicieron Keith Watt y Diego Silva, no Daphne | Calibración con dos personas promediadas; Daphne fija el protocolo y revisa las alertas; pregunta 14 actualizada |
| C98 | §9.1 | La tarea de explicación de la 1.5 no indica `next_step`: 70 de 72 primeros borradores rechazados por V-07 | Hallazgo registrado; propuesta de candidata 1.7 con «next_step: ver_comparacion» |
| C99 | §9.1, Anexo E | La 1.6 necesitaba que la línea SALIDA permitiera 450 caracteres y no tenía ejemplos escritos | Se registran la línea usada y los dos ejemplos evaluados (Anexo E.6) |
| C100 | §9.3 | V-03 rechazó como cifras los códigos `W1` y `CATALOGO_DEMO_V3`, y no decía nada de las cifras en palabras | V-03 trata los códigos de advertencia y de fuente como IDs; una cifra en palabras con unidad cuenta como cifra [SUPUESTO] |
| C101 | §9.3 | V-04: 2 posibles falsos positivos por negación frente a 3 detecciones reales | Tasa registrada; se mantiene la preferencia por el falso positivo |
| C102 | Preguntas | La regla de decisión no permite adoptar una versión que solo mejora robustez y costo | Pregunta 16 abierta |
| C103 | Encabezado, plan, §11.2 | Cierre de la versión 1.11 | Encabezado, pendientes externos, hito 3 y evolución de la suite actualizados |

## v1.9 → v1.10, cerrada (07-11-2026, cotejo con la CMF y preguntas resueltas)

| N.º | Sección | Hallazgo o decisión | Cambio en v1.10 |
|---|---|---|---|
| C91 | Plan, §7.7, §12, Anexo D | Cotejo de los valores cuota con la cartola diaria pública de la CMF en tres fechas: 27 de 27 coinciden | Requisito (1) de publicación cumplido por la vía (b); se cita la CMF como fuente; `HISTORICO_ENABLED=true` en la URL publicada; nuevo anexo D.8 con la tabla del cotejo; moneda confirmada |
| C92 | §11.3, preguntas | Daphne Loewenwarter hará la calibración humana | Pregunta 14 resuelta; calibración a ciegas con una persona, ampliable a dos |
| C93 | §1.1, preguntas | El grupo no tiene contacto con instituciones | Pregunta 15 resuelta: piloto institucional como plan, validación interna para el Proyecto Final y guía docente como borrador anexo |
| C94 | Preguntas | La pregunta 12 ya no condiciona la publicación | Marcada como resuelta en lo esencial; quedan consultas a Keith que no bloquean |
| C95 | §1.1, §11.3, preguntas | El grupo puede reunir 3 a 5 personas para la validación; Daphne hará sola la calibración humana; lo pendiente de Keith no afecta | Validación interna con 3 a 5 personas, informada como conteos y con criterios ajustados; regla para sumar una segunda persona solo si hay desacuerdo con el juez; pregunta 12 cerrada |

## v1.8 → v1.9, cerrada (06-11-2026, modelo de ingresos)

| N.º | Sección | Decisión o hallazgo | Cambio en v1.9 |
|---|---|---|---|
| C87 | §1.1, Plan, preguntas | El grupo eligió la licencia educativa institucional | Pregunta 13 resuelta; tabla de modelos reordenada; modelo elegido con clientes, licencia, estructura de precio, piloto, criterios de éxito, métricas y vía de expansión |
| C88 | §1.1, §2, §12 | El uso en liceos implicaría usuarios menores de edad, fuera del público de v0 | Clientes limitados a educación superior y programas para adultos; nuevo riesgo con su control |
| C89 | §1.1, Plan, §12 | Un informe por curso podría reidentificar estudiantes | Modo curso en P1, solo agregado y con un mínimo de 10 sesiones |
| C90 | Encabezado, cierre | No quedan decisiones de especificación pendientes | Versión cerrada; la pregunta 12 condiciona solo la publicación del panel; nueva pregunta 15 (piloto) |

## v1.7 → v1.8, borrador (06-11-2026, decisión del grupo sobre los valores cuota)

| N.º | Sección | Decisión o hallazgo | Cambio en v1.8 |
|---|---|---|---|
| C82 | Plan, RF-22, §7.7, preguntas | El grupo aprobó la opción B | Pregunta 10 resuelta; RF-22 y §7.7 aprobados; el panel histórico entra en P0, corte 2 |
| C83 | §7.7, §6.4, §6.5, §12 | Fuente y licencia de los valores cuota aún sin confirmar | Condición de publicación: confirmación de Keith (pregunta 12) y UF verificada contra el Banco Central; interruptor `HISTORICO_ENABLED`, apagado en la URL publicada hasta cumplirla |
| C84 | Encabezado, hitos, §9.5, §10, §11 | Requisitos y pruebas redactados como condicionales | A57–A60 forman parte de la suite vigente (A01–A64); A59 prueba también el panel desactivado; se eliminan los "si se aprueba la opción B" |
| C85 | Cierre de la versión | Solo queda una decisión del grupo | La v1.8 se cierra con la pregunta 13 (modelo de ingresos); la pregunta 12 condiciona la publicación del panel, no el cierre del SPEC |
| C86 | Plan, §7.7, §12, Anexo D, preguntas | El grupo informó que Keith extrae los valores cuota de los sistemas del banco donde trabaja, y la UF del 06-11-2026 (41.279,51) | Fuente registrada; el requisito (1) de publicación pasa a ser autorización del banco o cotejo con la CMF (recomendado). UF verificada por muestreo (cinco fechas coinciden con una fuente independiente; la UF informada coincide con la serie del SII): requisito (2) cumplido |

## v1.6 → v1.7, borrador (06-11-2026, observaciones del profesor Ahmat)

| N.º | Sección | Observación o hallazgo | Cambio en v1.7 |
|---|---|---|---|
| C73 | Plan, §6.3, §6.7 | "La IA debe quedar encendida en la URL publicada (con límite de gasto)" | `LLM_MODE=real` obligatorio en publicación; límite de gasto diario y mensual con reserva previa y bloqueo compartido, liquidación, interruptor, segunda capa en el proveedor y estado en `/health`; A61, A62 y A64 |
| C74 | §8.1, §8.2 | El gasto no se registraba | Tabla `llm_spend`, sin sesión ni contenido, con retención de 13 meses |
| C75 | §11.3, §9.1, §9.6 | "Falta un golden set de la función de IA con mejora medida entre versiones del prompt" | Golden set de 24 casos de la explicación; métricas de seguridad, robustez, calidad y operación; jueces a ciegas con calibración humana; protocolo pareado y regla de decisión; candidata 1.6 frente a la vigente 1.5; A63 |
| C76 | §1.1 | "Falta el modelo de ingresos" | Propuesta de valor, principio de neutralidad, cuatro modelos con prioridad, economía unitaria medida y métricas agregadas para validarlo |
| C77 | Plan, §6.7, §11 | "Conviene sacar el laboratorio Kubernetes del camino crítico" | Kind opcional, después del hito 6; el hito 4 usa dos instancias con Compose; A20 opcional |
| C78 | §10 | La pausa de la IA y el chat sin IA no tenían aviso | Estados "IA en pausa" y "Chat sin IA" |
| C79 | §12 | Sin riesgos de gasto, de evaluación ni de ingresos | Tres riesgos y un límite nuevos |
| C80 | Preguntas | Preguntas 6 y 11 respondidas por el profesor | Marcadas como resueltas; nuevas preguntas 13 (segmento y precio) y 14 (calibración humana) |
| C81 | Pregunta 10, lista de verificación, §7.7, §11 y §12 | La redacción hacía pensar que se seguía usando la base incompleta | La pregunta 10 indica que la versión 2 ya está incorporada y que solo falta la decisión de uso; las menciones a la versión 1 quedan solo en el Anexo C y en la tabla D.2. Tabla de §7.7 cotejada de nuevo contra la base: coincide |

## v1.5 → v1.6, borrador (06-11-2026, versión 2 de la base de valores cuota)

| N.º | Sección | Hallazgo | Cambio en v1.6 |
|---|---|---|---|
| C69 | Plan, §7.7, Anexo D | Keith entregó la versión 2 de la base, que completa abril a agosto de 2026 | Lista de verificación, fuentes (archivo `valores_cuota_v2.csv` y nuevo SHA-256), conteos de ventanas (73 y 49) y textos obligatorios actualizados; ya no se menciona un vacío |
| C70 | §7.7, Anexo D | Indicadores por recalcular con la base completa | Recalculados: solo cambia la volatilidad anualizada (entre 0,1 y 0,2 puntos). Totales, caídas máximas, peores ventanas y conteos de ventanas negativas no cambian, porque las ventanas agregadas fueron todas positivas |
| C71 | Anexo D | Faltaba verificar que la versión 2 no alterara los datos previos | Comparación fila a fila: las 21.636 filas anteriores son idénticas; el tramo agregado no muestra interpolación |
| C72 | §11 | A57 suponía un vacío en la base | A57 usa la versión 2 y conserva el caso del vacío como archivo de prueba |

## v1.4 → v1.5, borrador (06-11-2026, base de valores cuota de Keith Watt)

| N.º | Sección | Hallazgo | Cambio en v1.5 |
|---|---|---|---|
| C62 | Encabezado, Referencias, Anexo C | La v1.4 atribuía a una integrante del grupo las observaciones sobre la v1.3, pero provienen de una revisora externa | Atribución corregida; integrantes sin cambios |
| C63 | Plan | La lista de verificación de los valores cuota estaba sin aplicar | Lista aplicada punto por punto, con estado y [VERIFICAR] donde corresponde |
| C64 | Anexo D | Sin análisis de la base | Inventario, calidad de datos, método e indicadores en pesos corrientes y en pesos de hoy |
| C65 | §7.7, RF-22, §6.4, §6.5 | Sin propuesta concreta de uso | Opción B: panel educativo agregado por categoría, con fuentes versionadas, script fuera de línea, endpoint público y reglas de presentación; activable o eliminable sin afectar el resto |
| C66 | §4, RF-18 | El uso de una UF estática y de datos reales no estaba previsto | Fuera de alcance precisado; procedencia del panel separada de la del simulador |
| C67 | §9 | El LLM podía nombrar administradoras o proyectar desde el pasado | Prompt 1.5 (regla 12) y marcas y proyecciones en V-04 |
| C68 | §10, §11, §12 | Sin interfaz, pruebas ni riesgos para datos reales | Estado de interfaz, A57–A60, golden set de 38 casos, cinco riesgos y una materia normativa nuevos, fila del caso Emiliana |

## v1.3 → v1.4, borrador (04-11-2026, ajustes propuestos en una revisión externa y adoptados por el grupo)

| N.º | Sección | Hallazgo | Cambio en v1.4 |
|---|---|---|---|
| C54 | §7.5 | La v1.3 llamaba "nominal" a una tasa que la fórmula trata como efectiva anual | Nombre corregido a "tasa efectiva anual"; fórmula sin cambios; todas las tasas del simulador declaradas efectivas; "pesos corrientes" y "pesos de hoy" en lugar de "nominal" para valores |
| C55 | §7.5 | No había forma de ingresar una tasa nominal con capitalización mensual | Selector obligatorio del tipo de tasa y conversión `(1 + TNA / 12)^12 − 1`, mostrada junto a la tasa ingresada; el chat no convierte |
| C56 | Plan, §3.1 | La IA generativa real quedaba fuera de la primera versión | RF-21: explicación generativa de la comparación en P0; el chat con herramientas pasa a P1 |
| C57 | §6.3, §6.5, §8.1 | Sin contrato para la explicación | Algoritmo de una llamada sin herramientas, endpoint `POST /api/comparisons/{id}/explanation`, almacenamiento con la comparación y respaldo por plantilla |
| C58 | §9 | El prompt no distinguía la tarea de explicar | Prompt 1.4 con sección TAREAS y validador V-07 |
| C59 | §8.4, §8.5 | El aviso y las condiciones del LLM suponían que su uso era opcional | El aviso informa el envío de datos mínimos al proveedor; §8.5 debe cumplirse antes del hito 6 |
| C60 | §10, §11, §12 | Sin interfaz, pruebas ni riesgos para la explicación y la tasa | Estado de interfaz, A54–A56, golden set de 36 casos y tres riesgos nuevos |
| C61 | Plan | Decisiones que dependen de insumos aún no recibidos | Sección de pendientes externos (valores cuota y observaciones del profesor), lista de verificación para los valores cuota y condición de cierre de la versión |

## v1.2 → v1.3 (04-11-2026, revisión del grupo y revisión de ejecución)

| N.º | Sección | Hallazgo | Cambio en v1.3 |
|---|---|---|---|
| C36 | Encabezado | Integrantes desactualizados; versión de la suite poco visible | Integrantes actualizados según indicación del grupo; el encabezado indica la suite vigente (A01–A53) |
| C37 | §1, §2 | Faltaba conectar perfil, plazo, costo y moneda | Problema, brief y trabajos J2 y J6 reescritos |
| C38 | Plan | Sin priorización para el tiempo del taller | Prioridades P0, P1 y P2; kind pasa a P1 [SUPUESTO]; datos y productos reales quedan para P2 |
| C39 | §3.2 | Horizonte pedido en meses abstractos; sin aportes | M2 como mes y año; M9 obligatoria con $0 explícito |
| C40 | §3.2 | Moneda binaria (pesos o extranjera) | M8 con CLP, USD, EUR, otra o "No sé"; M7 en la moneda de M8 |
| C41 | §3.2 | W4 dependía del perfil y W5 no aclaraba el límite de la UF | W4 para metas en pesos; W5 con la aclaración sobre la UF frente a otra moneda |
| C42 | §3.3 | La ficha declaraba un "riesgo principal" y frases como "lo que más amenaza…" sin sustento | Mapa de cuatro riesgos por separado, con estado y sustento; sin jerarquía; desglose por alternativa |
| C43 | §3.3 | No se decía qué información faltaba | Tabla de información faltante (RF-20) |
| C44 | §5 | Sin forma de calcular la brecha antes del perfil | Calculadora sin perfil (nodo CB, RF-17) y pasos renumerados |
| C45 | §6.5 | Números en formato chileno podían llegar ambiguos a la API | Formato canónico en la API y conversión en la interfaz |
| C46 | §7.2 | D01 y D02 eran casi idénticas | Catálogo v3: D02 con aviso de 7 días y sin comisión; ficha técnica de D09 con supuestos, liquidez, costos y límites |
| C47 | §7.3 | No se explicaba qué significa cada plazo de retiro ni por qué había pocas alternativas | Significado de cada plazo, explicación de la escasez y limitación conocida con retiro de 0 días |
| C48 | §7.4 | Nada impedía comparar dos alternativas equivalentes | Paso SEL-0 de equivalencias |
| C49 | §7.5 | Simulación sin aportes, sin moneda extranjera, con un solo escenario y sin procedencia | Aportes, costo en otra moneda con descomposición inflación/tipo de cambio, brecha, aporte equivalente, hasta tres escenarios y procedencia de cada supuesto; ningún supuesto por defecto |
| C50 | §7.6 | Sin definición de fuentes oficiales futuras | Requisitos de `fuente_oficial` para P2 |
| C51 | §9 | El prompt podía jerarquizar riesgos o sugerir aportes | Prompt 1.3 (reglas 10 y 11) y frases nuevas en V-04 |
| C52 | §10 | Faltaban la calculadora, el desglose de riesgos y los escenarios en la interfaz | Nuevas rutas y estados; formato numérico accesible |
| C53 | §11 | Sin pruebas de costo, moneda, aportes en $0, escenarios ni equivalencias; confusión entre las suites de v1.0 y v1.1 | A44–A53, A09, A10, A28 y A37–A43 actualizados; §11.2 con la evolución de la suite |

## v1.1 → v1.2 (04-11-2026, a partir del caso Emiliana)

| N.º | Sección | Hallazgo de la prueba | Cambio en v1.2 |
|---|---|---|---|
| C26 | §1, §2 | La plataforma asignaba una etiqueta, pero no explicaba qué amenaza a la meta | Problema ampliado y nuevo trabajo J6 |
| C27 | §3.3 | "Conservador" era correcto pero insuficiente como resultado | Ficha de perfil y meta por dimensiones, riesgo principal (R-11) y frase resumen sin LLM |
| C28 | §3.2 | No se preguntaba el costo ni la moneda de la meta, así que no podía responder "¿me alcanza?" | M7 y M8 opcionales; cobertura del costo en pesos de hoy; la plataforma nunca busca precios ni tipos de cambio |
| C29 | §3.2 | "No perder" se traducía solo en preservar el monto nominal | W4 (inflación) y W5 (tipo de cambio) |
| C30 | §3.2, §7.3 | La respuesta más prudente (retiro en 0 días) dejaba sin comparación y sin explicación comprensible | Texto de ayuda neutral en M3 y explicación en lenguaje simple de cada motivo de exclusión |
| C31 | §7.2 | El segmento conservador comparaba alternativas casi idénticas (D01 y D02) | D09, depósito reajustable simulado con clase propia; catálogo v2 y prueba de regresión A42 |
| C32 | §7.5, §6.5 | El simulador solo daba valores nominales y existía solo en el chat | Poder de compra y costo futuro con inflación supuesta; formulario `POST /api/simulate` que funciona sin LLM |
| C33 | §5.1, §5.2, §10 | El diagrama no mostraba la ficha ni el simulador | Nodos FI y SIM, pasos 8 y 12, rutas y estados de interfaz |
| C34 | §9 | El prompt no explicaba la ficha y podía estimar precios | Prompt 1.2 con reglas 10 y 11; nuevos comportamientos esperados; plantillas actualizadas |
| C35 | §11 | Sin prueba de una meta con fecha y costo | A37 a A43, caso de referencia §11.1 y golden set ampliado a 29 casos |

## v1.0 → v1.1

| N.º | Sección | Problema en v1.0 | Corrección en v1.1 |
|---|---|---|---|
| C01 | Encabezado | Sin identificación del Grupo 2 ni de las versiones de prompt y catálogo | Ficha con grupo, integrantes, versiones internas y fuentes de diseño |
| C02 | Instrucción de uso | Sin convenciones normativas ni regla para resolver conflictos | DEBE/NO DEBE, [VERIFICAR], identificadores trazables, jerarquía y prohibición de alterar pruebas para que pasen |
| C03 | Hitos | Evidencias sin vínculo con pruebas concretas | Cada hito enumera los criterios que debe aprobar |
| C04 | §3.2 y flujo de usuario | El cuestionario mezclaba perfil y meta, mientras el diagrama confirma la meta después del perfil, incluso con perfil vigente | Bloque A y bloque B, con entidades y endpoints separados |
| C05 | §3.2 | "No sé" en gastos esenciales sin regla | M5 = No sé activa aclaración |
| C06 | §3.2 | Comprensión de la pérdida mezclada con experiencia; experiencia sin uso definido | K2 explícita; E1 solo ajusta la explicación |
| C07 | §3.2 | Objetivo "preservar capital" recogido pero sin efecto en filtros | R-08 lo convierte en preservación efectiva |
| C08 | §3.2 | Texto libre de 200 caracteres sin uso ni tratamiento | M6 de 60 caracteres, solo visualización y fuera del LLM |
| C09 | §3.2 | Vigencia de 12 meses irreconciliable con sesiones de 24 horas | Vigencia efectiva como mínimo de ambas; reloj inyectable |
| C10 | §5 | El diagrama no tenía consentimiento ni puertas de aclaración, la insuficiencia no tenía salida y todo cambio volvía al cuestionario | Diagrama Mermaid con nodos agregados y bifurcación situación/meta; pasos mapeados a nodos; tabla de estados |
| C11 | §6 y diagrama de componentes | Sin proveedor LLM; no distinguía módulos de servicios | Nodo LLM, flechas rotuladas y mapeo nodo → módulo → pruebas |
| C12 | §7.1 | No se sabía quién entregaba los argumentos del filtro y del comparador; el LLM podía invocarlos | Funciones del flujo solo vía API; el LLM solo explica, como indica el diagrama, con dos herramientas |
| C13 | §7.4 | Regla de selección ambigua y sesgada: perfiles moderados y arriesgados recibían solo opciones de riesgo 1 | Columna Clase y regla SEL-1 a SEL-5, verificada; A07 y A08 conservan su resultado |
| C14 | §7.3 | No había forma de calcular "qué condición limita" | Todos los motivos registrados, con conteo y orden definidos |
| C15 | §7.5 | El LLM podía inventar la tasa; "0,05" era ambiguo | Verificación de procedencia; tasas solo con %; supuestos repetidos en la salida |
| C16 | §6.5 | Faltaban endpoints de meta, historial y conversación (A13 no era comprobable); 503 por caída del LLM contradecía el modo plantilla | Contratos completos, tabla de códigos y ejemplo; caída del LLM → 200 con plantilla |
| C17 | §6.6 | Sin reglas para cookie tras proxy, CSRF previo a la sesión, XSS por salida del modelo ni almacenamiento del token | Sección de seguridad transversal |
| C18 | §6.7 | Purga y límites no funcionaban con dos réplicas; migraciones simultáneas; `port-forward` no prueba el reparto; `PORT` sin expandir en `CMD` de lista | Bloqueo consultivo, contadores en base de datos, migración como paso aparte, NodePort y nota sobre `CMD` |
| C19 | §9.2 | El LLM debía devolver `alternatives` y `disclaimer`, que a la vez inserta el backend | Borrador del LLM separado de la respuesta pública; tabla de estado; V-01 a V-06 |
| C20 | §9.1 | El prompt nombraba marcas reales y hablaba de "al menos tres" | Prompt genérico; exactamente tres; sin cifras en texto; dos herramientas |
| C21 | §9.4 | "Sus resultados pasados" era ambiguo | "Los resultados pasados" |
| C22 | §10 | Sin rutas ni estados de aclaración, límite o falta de consentimiento | Rutas por nodo, estados nuevos y objetivo WCAG 2.2 AA |
| C23 | §11 | 22 criterios sin hito; selección, CSRF, XSS, consentimiento, procedencia y cambio de meta desde el chat sin prueba | 36 criterios con hito y criticidad; golden set especificado |
| C24 | §8.4 y §12.4 | Sin marco concreto de datos personales ni de servicios Fintec | Ley 21.719 con fecha y proyecto de postergación; Ley 21.521, NCG 502 y NCG 559 como revisión previa a un servicio real |
| C25 | §8.3 | Minimización sin ejemplo concreto | Ejemplo de `CONTEXTO_SERVIDOR` y lista de campos que nunca viajan |
