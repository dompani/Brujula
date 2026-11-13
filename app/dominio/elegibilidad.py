"""filtrar_alternativas: filtros de elegibilidad y liquidez (§7.3)."""
from . import politica as P


def motivos_exclusion(a: dict, nivel: int, monto: int, horizonte: int, retiro: int, preservacion: bool) -> list[str]:
    m = []
    if a["riesgo"] > nivel:
        m.append("riesgo")
    if monto < a["monto_min_clp"]:
        m.append("monto_minimo")
    if horizonte < a["horizonte_min_meses"]:
        m.append("horizonte")
    if a["retiro_dias"] > retiro:
        m.append("retiro")
    if preservacion and not a["capital_preserved_sim"]:
        m.append("preservacion")
    if a.get("currency", "CLP") != "CLP":
        m.append("moneda")
    if not a.get("active", True):
        m.append("inactivo")
    if not a.get("data_usable", True):
        m.append("dato_no_utilizable")
    return m


def filtrar_alternativas(catalogo: list[dict], perfil_operativo: str, monto: int, horizonte: int, retiro: int,
                         preservacion: bool) -> tuple[list[dict], dict]:
    nivel = P.NIVELES[perfil_operativo]
    elegibles, excluidas = [], {}
    for a in catalogo:
        m = motivos_exclusion(a, nivel, monto, horizonte, retiro, preservacion)
        if m:
            excluidas[a["id"]] = m
        else:
            elegibles.append(a)
    return elegibles, excluidas


def condiciones_limitantes(catalogo: list[dict], perfil_operativo: str, excluidas: dict) -> list[dict]:
    """Entre las alternativas que cumplen el nivel de riesgo, cuenta cada motivo de exclusión."""
    nivel = P.NIVELES[perfil_operativo]
    conteo = {}
    for a in catalogo:
        if a["riesgo"] <= nivel and a["id"] in excluidas:
            for m in excluidas[a["id"]]:
                conteo[m] = conteo.get(m, 0) + 1
    orden = sorted(conteo.items(), key=lambda kv: (-kv[1], P.ORDEN_MOTIVOS.index(kv[0])))
    return [{"codigo": k, "conteo": n, "explicacion": P.TEXTOS_MOTIVO[k]} for k, n in orden]
