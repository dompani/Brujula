"""Constantes versionadas de la política de la demo (§3.2, §7.3, §9.4 del SPEC)."""

QUESTIONNAIRE_VERSION = "1.3"
POLICY_VERSION = "1.4"
PROMPT_VERSION = "1.7"
CONSENT_VERSION = "1.0"
SOURCE_ID = "CATALOGO_DEMO_V3"

NIVELES = {"conservador": 1, "moderado": 2, "arriesgado": 3}
NIVEL_A_PERFIL = {v: k for k, v in NIVELES.items()}

# Bloque A
OPCIONES_T = (0, 1, 2)
OPCIONES_K1 = ("ninguna", "hasta_10", "mas_10", "no_se")
OPCIONES_K2 = ("si", "no")
OPCIONES_E1 = ("ninguna", "basica", "avanzada")
OPCIONES_F1 = ("si", "no", "prefiero_no_responder")

# Bloque B
OPCIONES_M1 = ("preservar_capital", "meta_concreta", "crecimiento_largo_plazo")
OPCIONES_M3 = (0, 7, 30, 180)
OPCIONES_M5 = ("si", "no", "no_se")
MONEDAS_FIJAS = ("CLP", "USD", "EUR", "no_se")

UMBRAL_W2_MESES = 36  # aprobado como política educativa provisional (pregunta 3)

DISCLAIMER_V1_1 = (
    "Demostración académica con alternativas y costos simulados. El perfil obtenido es una aproximación "
    "educativa y no una evaluación profesional completa. Esta plataforma no recibe dinero ni ejecuta "
    "inversiones. Las inversiones reales pueden generar pérdidas y los resultados pasados no garantizan "
    "resultados futuros. Verifica la información y las condiciones antes de decidir y, cuando corresponda, "
    "consulta a un profesional habilitado."
)

ROTULO_IA = ("Explicación generada con IA a partir de resultados calculados por reglas. "
             "Si algo no coincide con la tabla, vale la tabla.")
ROTULO_SIN_IA = "Explicación automática sin IA."
ROTULO_PAUSA = ("La explicación con IA alcanzó su límite de uso por hoy; "
                "esta es una explicación automática sin IA.")

TEXTOS_MOTIVO = {
    "riesgo": "Supera el nivel de riesgo de tu perfil.",
    "monto_minimo": "Exige un monto mínimo mayor que el que tienes disponible.",
    "horizonte": "Requiere un horizonte más largo que el de tu meta.",
    "retiro": "Tarda más en devolver el dinero que el plazo que puedes esperar.",
    "preservacion": "No preserva el capital en la simulación, y tu perfil o tu objetivo lo exigen.",
    "moneda": "No está disponible en esta demo.",
    "inactivo": "No está disponible en esta demo.",
    "dato_no_utilizable": "No está disponible en esta demo.",
}
ORDEN_MOTIVOS = list(TEXTOS_MOTIVO)

SIGNIFICADO_M3 = {
    0: "Necesitas poder tener el dinero el mismo día en que lo pides",
    7: "Puedes esperar hasta una semana",
    30: "Puedes esperar hasta un mes",
    180: "Puedes esperar hasta seis meses",
}
LIQUIDEZ_REQUERIDA = {0: "inmediata", 7: "alta", 30: "media", 180: "baja"}

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre")

TEXTO_ESCALADA = (
    "Esta demostración no reemplaza una evaluación profesional. Si necesitas decidir sobre tu dinero, "
    "consulta a un profesional cuya habilitación puedas verificar en fuentes oficiales, como el registro "
    "público de la Comisión para el Mercado Financiero (CMF)."
)
