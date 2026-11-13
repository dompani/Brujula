"""Selección de tres alternativas distintas: SEL-0 a SEL-5 (§7.4). No usa comisiones ni datos comerciales."""
from . import politica as P


def firma(a: dict) -> tuple:
    return (a["clase"], a["riesgo"], a["horizonte_min_meses"], a["retiro_dias"], a["capital_preserved_sim"],
            a["inflation_adjusted_sim"])


def seleccionar(elegibles: list[dict], perfil_operativo: str) -> dict:
    nivel = P.NIVELES[perfil_operativo]
    orden = sorted(elegibles, key=lambda a: (a["riesgo"], a["id"]))  # SEL-2
    distintas, equivalentes, vistas = [], {}, {}
    for a in orden:  # SEL-0
        f = firma(a)
        if f in vistas:
            equivalentes[a["id"]] = vistas[f]
        else:
            vistas[f] = a["id"]
            distintas.append(a)
    if len(distintas) < 3:  # SEL-1
        return {"suficiente": False, "n_distintas": len(distintas), "seleccion": [], "equivalentes": equivalentes}
    sel = []
    for n in range(1, nivel + 1):  # SEL-3: escalera de riesgo
        c = [a for a in distintas if a["riesgo"] == n and a not in sel]
        if c:
            sel.append(c[0])
        if len(sel) == 3:
            break
    while len(sel) < 3:  # SEL-4: relleno por diversidad de clase
        clases = {a["clase"] for a in sel}
        resto = [a for a in distintas if a not in sel]
        sel.append(([a for a in resto if a["clase"] not in clases] or resto)[0])
    sel = sorted(sel, key=lambda a: (a["riesgo"], a["id"]))  # SEL-5
    return {"suficiente": True, "n_distintas": len(distintas), "seleccion": [a["id"] for a in sel],
            "equivalentes": equivalentes}
