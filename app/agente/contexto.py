"""CONTEXTO_SERVIDOR (§8.3): lo único que viaja al LLM. Sin cookies, IDs internos, M6, M7 ni respuestas T1–T4."""
from ..dominio import catalogo, politica as P

MONEDA = {"no_se": "No sé"}


def construir(perfil_row, goal_row, comp_row) -> dict:
    r = perfil_row["result"]
    g = goal_row["data"]
    ev = goal_row["evaluation"]
    payload = comp_row["payload"]
    ficha = payload["ficha"]
    porid = catalogo.por_id()
    alternativas = []
    for i in payload["selected_ids"]:
        a = porid[i]
        alternativas.append({
            "id": a["id"], "nombre": a["categoria"], "clase": a["clase"], "riesgo": a["riesgo"],
            "horizonte_min_meses": a["horizonte_min_meses"], "retiro_dias": a["retiro_dias"],
            "monto_min_clp": a["monto_min_clp"], "comision_anual_pct": float(a["comision_anual_pct"]),
            "preserva_capital_sim": a["capital_preserved_sim"], "reajusta_inflacion_sim": a["inflation_adjusted_sim"],
            "return_pct": None, "risk_explanation": a["risk_explanation"], "costs_not_included": a["costs_not_included"],
            "simulated": True, "source_id": a["source_id"], "currency": a["currency"],
            "desglose": payload["exposure_by_alternative"][i],
        })
    return {
        "estado": "comparacion",
        "perfil": {"tolerancia": r["tolerance"], "techo_capacidad": r["capacity_cap"], "operativo": r["effective_risk"],
                   "vigente_hasta": perfil_row["valid_until"], "experiencia": r["experiencia"]},
        "meta": {"objetivo": g["objective"], "horizonte_meses": g["horizon_months"],
                 "espera_max_dias": g["max_wait_days"], "monto_clp": g["amount_clp"],
                 "preservacion_requerida": ev["preservacion"], "preservacion_origen": ev["preservacion_origen"],
                 "moneda_pago": MONEDA.get(g["payment_currency"], g["payment_currency"]),
                 "aporte_mensual_clp": g["monthly_contribution_clp"], "brecha_hoy": ficha["brecha_hoy"]},
        "ficha": {"plazo": ficha["dimensiones"]["plazo"], "liquidez_requerida": ficha["dimensiones"]["liquidez_requerida"],
                  "riesgos": ficha["riesgos"], "faltante": ficha["faltante"]},
        "advertencias": [{"codigo": w["codigo"], "texto": w["contexto"]} for w in ev["warnings"]],
        "comparacion": {"ids": payload["selected_ids"],
                        "orden": "riesgo ascendente; el orden no es una recomendación",
                        "alternativas": alternativas, "otras_compatibles": payload["other_eligible_ids"],
                        "equivalentes": payload["equivalentes"], "excluidas": payload["exclusions"]},
        "versiones": {"policy": P.POLICY_VERSION, "perfil": comp_row["profile_version"],
                      "meta": comp_row["goal_version"]},
    }
