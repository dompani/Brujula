"""Plantillas deterministas (Anexo B del SPEC)."""
from ..dominio import politica as P


def pct(texto) -> str:
    return f"{float(texto):.2f}".replace(".", ",") + " %"


def explicacion_sin_ia(alternativas: list[dict]) -> dict:
    """Respaldo de RF-21: una línea por alternativa, sin IA. Las cifras vienen del catálogo, no de un modelo."""
    expl = []
    for a in alternativas:
        expl.append({"id": a["id"], "texto": (
            f"{a['categoria']}: riesgo {a['riesgo']} de 3; plazo de retiro {a['retiro_dias']} días; "
            f"{'preserva' if a['capital_preserved_sim'] else 'no preserva'} capital y "
            f"{'se reajusta' if a['inflation_adjusted_sim'] else 'no se reajusta'} por inflación en la simulación; "
            f"comisión anual simulada {pct(a['comision_anual_pct'])}.")})
    return {"summary": "Las diferencias están en la tabla.", "explicaciones": expl,
            "limitations": ["Catálogo simulado; no incluye impuestos ni spreads."]}


def insuficiencia(n: int, condiciones: list[dict]) -> str:
    conds = "; ".join(f"{c['codigo'].replace('_', ' ')} ({c['conteo']}): {c['explicacion']}" for c in condiciones)
    return (f"Con tu meta actual, el catálogo simulado tiene {n} alternativa(s) compatible(s) y se necesitan tres "
            f"para comparar. Lo que más limita: {conds} Puedes revisar tu meta; esta demo no relaja los filtros ni "
            "sugiere asumir más riesgo.")


def comparacion(frase: str) -> str:
    return (f"{frase} Estas son tres alternativas simuladas compatibles con tu perfil y tu meta. Se muestran de menor a "
            "mayor riesgo; el orden no es una recomendación. La tabla muestra, para cada una, cómo se relaciona con "
            "los riesgos de mercado, de inflación chilena y de moneda.")


def aclaracion(motivo: str) -> str:
    return (f"Con tus respuestas, esta demo no muestra una comparación personalizada: {motivo}. Puedes revisar el "
            "contenido educativo, corregir tus respuestas o conversar con un profesional habilitado antes de invertir.")


CALCULADORA = ("Este cálculo usa tus datos y tus supuestos; no es un pronóstico ni una recomendación, y no guardamos "
               "estos datos. Para ver alternativas compatibles con tu perfil, responde el cuestionario.")
ERROR = "No pude completar esta respuesta. Tu comparación sigue disponible; intenta nuevamente en unos minutos."
