"""Ficha de perfil y meta (R-11, §3.3): dimensiones, brecha de hoy, mapa de riesgos e información faltante."""
from decimal import Decimal

from . import politica as P

ESTADOS = {
    "aplica": "aplica", "indirecto": "indirecto", "por_confirmar": "por confirmar", "no_aplica": "no aplica",
    "depende_de_la_alternativa": "depende de la alternativa",
    "no_aplica_a_las_comparadas": "no aplica a las alternativas comparadas",
    "controlada_por_el_filtro": "controlada por el filtro",
}
NOMBRE_RIESGO = {"inflacion_cl": "inflación chilena", "moneda": "moneda", "mercado": "mercado",
                 "liquidez": "liquidez"}
MENSAJES_FALTANTE = {
    "costo": "Sin costo estimado no se puede calcular la brecha.",
    "moneda": "Confirma la moneda en que se pagará la meta para separar el riesgo de moneda.",
    "tipo_cambio": "Para expresar la brecha en pesos, ingresa el tipo de cambio que supones; la demo no lo consulta.",
}
META_TEXTO = {"preservar_capital": "objetivo de preservar capital", "meta_concreta": "meta concreta",
              "crecimiento_largo_plazo": "objetivo de crecimiento"}


def pesos(n) -> str:
    n = int(n)
    s = f"{abs(n):,}".replace(",", ".")
    return f"-${s}" if n < 0 else f"${s}"


def mes_y_anio(target_month: str) -> str:
    y, m = target_month.split("-")
    return f"{P.MESES[int(m) - 1]} de {y}"


def plazo(n: int) -> str:
    return "corto" if n <= 12 else "mediano" if n <= 60 else "largo"


def moneda_texto(mon: str) -> str:
    return "No sé" if mon == "no_se" else mon


def componer_ficha(perfil: dict, meta: dict, evaluacion: dict, seleccionadas: list[dict] | None = None) -> dict:
    mon = meta["payment_currency"]
    fecha = mes_y_anio(meta["target_month"])
    costo = meta.get("estimated_cost")
    costo = Decimal(costo) if costo not in (None, "") else None
    # Brecha de hoy
    faltante, brecha_valor, brecha_codigo = [], None, None
    if costo is None:
        faltante.append("costo")
    elif mon in ("CLP", "no_se"):
        brecha_valor = int(meta["amount_clp"] - costo)
        brecha_codigo = "sobra" if brecha_valor >= 0 else "falta"
    else:
        faltante.append("tipo_cambio")
    if mon == "no_se":
        faltante.append("moneda")
    # Mapa de riesgos (sin orden de importancia)
    infl = "aplica" if mon in ("CLP", "no_se") else "indirecto"
    moneda = "no_aplica" if mon == "CLP" else "por_confirmar" if mon == "no_se" else "aplica"
    mercado = "depende_de_la_alternativa"
    if seleccionadas is not None and seleccionadas and all(a["capital_preserved_sim"] for a in seleccionadas):
        mercado = "no_aplica_a_las_comparadas"
    riesgos = {"inflacion_cl": infl, "moneda": moneda, "mercado": mercado, "liquidez": "controlada_por_el_filtro"}
    sustento = {
        "inflacion_cl": (f"Tu meta se paga en pesos: con inflación, un monto fijo en pesos compra menos hacia {fecha}."
                         if infl == "aplica" else
                         f"Afecta lo que compran tus pesos, pero el costo de tu meta depende de la inflación de {mon} "
                         "y del tipo de cambio."),
        "moneda": ("Tu meta se paga en pesos." if moneda == "no_aplica" else
                   "Confirma la moneda en que se pagará la meta." if moneda == "por_confirmar" else
                   f"Tu meta se paga en {mon}: su costo en pesos cambia con el tipo de cambio. Ninguna alternativa "
                   f"del catálogo está en {mon}."),
        "mercado": ("Las tres alternativas comparadas preservan capital en la simulación (propiedad ficticia del "
                    "catálogo)." if mercado == "no_aplica_a_las_comparadas" else
                    f"Las alternativas que no preservan capital en la simulación pueden bajar de valor antes de "
                    f"{fecha}; la tabla indica cuáles."),
        "liquidez": (f"Las alternativas compatibles devuelven el dinero en {meta['max_wait_days']} días o menos; "
                     "las que tardan más quedaron fuera."),
    }
    aporte = meta["monthly_contribution_clp"]
    aporte_txt = "$0 (declarado)" if aporte == 0 else pesos(aporte)
    pl = plazo(meta["horizon_months"])
    liq = P.LIQUIDEZ_REQUERIDA[meta["max_wait_days"]]
    estados_txt = ", ".join(f"{NOMBRE_RIESGO[k]} ({ESTADOS[v]})" for k, v in riesgos.items())
    frase = (f"Perfil {perfil['effective_risk']} · {META_TEXTO[meta['objective']]} para {fecha} ({pl} plazo) · "
             f"liquidez requerida {liq} · aporte mensual {aporte_txt}. Riesgos a revisar por separado: {estados_txt}.")
    return {
        "frase": frase,
        "dimensiones": {
            "disposicion": perfil["disposicion"], "capacidad": perfil["capacidad_declarada"],
            "perfil_operativo": perfil["effective_risk"], "objetivo": META_TEXTO[meta["objective"]],
            "fecha": fecha, "horizonte_meses": meta["horizon_months"], "plazo": pl, "liquidez_requerida": liq,
            "espera_max_dias": meta["max_wait_days"],
            "preservacion": evaluacion["preservacion"], "preservacion_origen": evaluacion["preservacion_origen"],
            "ahorro": pesos(meta["amount_clp"]), "aporte": aporte_txt,
            "costo": None if costo is None else (pesos(costo) if mon in ("CLP", "no_se") else f"{costo} {mon}"),
            "moneda": moneda_texto(mon),
        },
        "brecha_hoy": brecha_codigo, "brecha_hoy_valor": brecha_valor,
        "riesgos": riesgos, "riesgos_texto": {k: ESTADOS[v] for k, v in riesgos.items()}, "sustento": sustento,
        "faltante": faltante, "faltante_texto": [MENSAJES_FALTANTE[f] for f in faltante],
    }
