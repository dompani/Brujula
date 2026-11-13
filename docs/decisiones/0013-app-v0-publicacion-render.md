# 0013. App v0 y publicación en Render

- **Fecha:** 13-11-2026
- **Decide:** Daphne Loewenwarter, por el Grupo 2, por plazo de entrega
- **SPEC:** §6.4, §6.7, §8.4, §8.5, §11.2, Anexo E.7 y §12 (pregunta 8)

## Contexto

El Proyecto Final exige la app publicada con la IA encendida y límite de gasto. La entrega vence el 13-11-2026. Configurar Cloud Run en Santiago (decisión 0012) exigía abrir una cuenta de facturación de Google Cloud, una base Cloud SQL y credenciales de despliegue.

## Decisión

1. **Publicación en Render**, plan gratuito: app en Docker y PostgreSQL gestionado, región de Oregón (Estados Unidos), definidos en `render.yaml` (Blueprint). Render despliega cada commit de `main` cuando las verificaciones de GitHub están en verde (`autoDeployTrigger: checksPass`). Cloud Run queda para una fase posterior.
2. **Titular de las cuentas** de IA y de publicación: Daphne Loewenwarter. La clave de la IA y el correo de contacto se ingresan en Render y nunca van al repositorio.
3. **Modelo de producción:** `claude-sonnet-5-5`, con tarifas de 2 y 10 USD por millón de tokens de entrada y de salida (página de precios del proveedor, 13-11-2026). Límites: 1 USD diario y 10 USD mensual; una explicación reserva como máximo cerca de 0,025 USD.
4. **Sin razonamiento extendido en la explicación.** `claude-sonnet-5-5` razona por defecto, y ese razonamiento consume el límite de 1.500 tokens de salida y alarga la respuesta más allá del plazo de 20 s. La app envía `thinking: between_tools` (sin herramientas, la respuesta es solo texto) y `effort: medium`, configurables con `LLM_THINKING` y `LLM_EFFORT`. Sin `temperature`, que este modelo no admite.
5. **Golden set con el modelo de producción:** pendiente. La URL se publica antes de repetirlo; mientras tanto cada explicación pasa por V-01 a V-07, con una reparación como máximo, y si falla se muestra la plantilla sin IA.

## Qué cubre la app v0

| Prioridad | Estado |
|---|---|
| P0 · Corte 1 | Meta con fecha, costo, moneda y aportes; ficha con brecha de hoy, mapa de riesgos e información faltante; simulador de hasta tres escenarios con procedencia; calculadora sin perfil |
| P0 · Corte 2 | Cuestionario y perfil (R-01 a R-05), puertas de aclaración, filtros, selección SEL-0 a SEL-5, comparación con desglose de riesgos, insuficiencia con condiciones limitantes; explicación con IA real, límite de gasto con reserva previa y bloqueo, control de salida y plantilla de respaldo; chat en modo automático sin IA |
| P0 · Historial | Panel «Así se movieron en el pasado» en `/metodologia`, generado por `scripts/procesar_historico.py` |
| P0 · Publicación | Dockerfile, `compose.yaml`, CI con pruebas en SQLite y PostgreSQL, construcción de la imagen y verificación de `/health` y `/ready`; Blueprint de Render |
| Simplificaciones | El cuestionario está en una sola página, no por pasos; el límite agregado por IP (§12.2) y la purga horaria se reemplazan por la purga al crear sesiones; las migraciones crean las tablas al arrancar; la suite de navegador (360, 768 y 1280 px) se ejecutó de forma local con Playwright y no está en CI |

## Prueba de humo (A64)

13-11-2026, 15:12, en https://brujula-y21u.onrender.com: `/health` con `llm.modo=real`; recorrido completo del caso Emiliana (perfil conservador, D01, D03 y D09, D02 como otra compatible); explicación con `generated_by=llm` que pasó V-01 a V-07 a la primera ([captura](../evidencias/2026-11-13_explicacion_ia_url_publicada.png)). Los dos primeros intentos cayeron en la plantilla porque `claude-sonnet-5-5` razonaba por defecto (punto 4); el respaldo funcionó como estaba previsto.

## Consecuencias

Los datos de la sesión se guardan en Estados Unidos y el aviso de privacidad lo informa. La instancia gratuita se suspende tras 15 minutos sin tráfico y tarda cerca de un minuto en despertar. La base gratuita vence a los 30 días: antes de esa fecha hay que pasarla a un plan pagado o recrearla. Para detener todo gasto: `LLM_KILL_SWITCH=true` en Render, desactivar la clave en la consola de Claude o suspender el servicio.
