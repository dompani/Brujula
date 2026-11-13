"""comparar_alternativas: filtro, selección y desglose de riesgos por alternativa (§5.2 pasos 10 a 12)."""
from . import catalogo, politica as P
from .elegibilidad import condiciones_limitantes, filtrar_alternativas
from .ficha import componer_ficha
from .seleccion import seleccionar


def desglose(a: dict, moneda_meta: str) -> dict:
    return {
        "mercado": "no_expuesta" if a["capital_preserved_sim"] else "expuesta",
        "inflacion_cl": "reajusta" if a["inflation_adjusted_sim"] else "no_reajusta",
        "moneda_meta": ("no_aplica" if moneda_meta == "CLP" else "por_confirmar" if moneda_meta == "no_se"
                        else f"no cubre {moneda_meta}"),
    }


def comparar_alternativas(perfil: dict, meta: dict, evaluacion: dict, cat: list[dict] | None = None) -> dict:
    cat = cat if cat is not None else catalogo.alternativas()
    op = perfil["effective_risk"]
    eleg, excl = filtrar_alternativas(cat, op, meta["amount_clp"], meta["horizon_months"], meta["max_wait_days"],
                                      evaluacion["preservacion"])
    sel = seleccionar(eleg, op)
    porid = {a["id"]: a for a in cat}
    if not sel["suficiente"]:
        return {"status": "alternativas_insuficientes", "n_compatibles": sel["n_distintas"],
                "elegibles": [a["id"] for a in eleg], "equivalentes": sel["equivalentes"], "exclusions": excl,
                "limiting_conditions": condiciones_limitantes(cat, op, excl), "selected_ids": [],
                "other_eligible_ids": [], "exposure_by_alternative": {},
                "ficha": componer_ficha(perfil, meta, evaluacion)}
    ids = sel["seleccion"]
    elegidas = [porid[i] for i in ids]
    otras = [a["id"] for a in sorted(eleg, key=lambda a: (a["riesgo"], a["id"]))
             if a["id"] not in ids and a["id"] not in sel["equivalentes"]]
    return {"status": "comparacion", "selected_ids": ids, "other_eligible_ids": otras,
            "equivalentes": sel["equivalentes"], "exclusions": excl, "limiting_conditions": [],
            "exposure_by_alternative": {a["id"]: desglose(a, meta["payment_currency"]) for a in elegidas},
            "ficha": componer_ficha(perfil, meta, evaluacion, elegidas)}


def vista_alternativa(a: dict) -> dict:
    """Campos homogéneos para la interfaz y la API (§6.5)."""
    return {"id": a["id"], "name": a["categoria"], "clase": a["clase"], "risk_level": a["riesgo"],
            "horizon_min_months": a["horizonte_min_meses"], "liquidity_days": a["retiro_dias"],
            "min_amount_clp": a["monto_min_clp"], "annual_fee_pct": a["comision_anual_pct"],
            "preserves_capital_sim": a["capital_preserved_sim"], "inflation_adjusted_sim": a["inflation_adjusted_sim"],
            "currency": a["currency"], "risk_explanation": a["risk_explanation"], "data_status": "simulado",
            "costs_not_included": a["costs_not_included"], "source_id": a["source_id"]}


TEXTO_ORDEN = "Se muestran de menor a mayor riesgo; el orden no es un ranking ni una recomendación."
_ = P  # constantes disponibles para quien importe este módulo
