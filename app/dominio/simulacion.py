"""simular_escenarios (§7.5): pesos corrientes, poder de compra, costos, brechas y aporte equivalente.

Cálculo con Decimal (precisión 28). Ningún supuesto se completa por defecto: si falta uno, el resultado que lo
necesita queda como "no calculado" con su motivo.
"""
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal, InvalidOperation, localcontext

from .perfil import EntradaInvalida

CIEN = Decimal(100)


def _q(x: Decimal) -> int:
    return int(x.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _pct(valor, campo: str, obligatorio: bool, malos: list) -> Decimal | None:
    if valor in (None, ""):
        if obligatorio:
            malos.append(campo)
        return None
    try:
        d = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        malos.append(campo)
        return None
    if not (Decimal(-100) < d <= CIEN) or not d.is_finite():
        malos.append(campo)
        return None
    return d / CIEN


NO_CALC = {
    "pi_cl": "Sin inflación supuesta, solo se muestran valores en pesos corrientes y la brecha de hoy.",
    "costo": "Sin costo estimado no se puede calcular la brecha.",
    "tc": "Para expresar la brecha en pesos, ingresa el tipo de cambio que supones; la demo no lo consulta.",
    "ext": ("Para proyectar el costo futuro, indica la inflación supuesta de {m} y la variación supuesta del "
            "tipo de cambio; pueden ser 0 % si así lo supones."),
}


def simular_escenarios(meta: dict, escenarios: list[dict], ahora_iso: str) -> dict:
    """meta: {amount_clp, monthly_contribution_clp, horizon_months, estimated_cost?, payment_currency}."""
    if not 1 <= len(escenarios) <= 3:
        raise EntradaInvalida(["escenarios"])
    C, A, n = meta["amount_clp"], meta["monthly_contribution_clp"], meta["horizon_months"]
    malos = []
    if not isinstance(C, int) or C <= 0:
        malos.append("amount_clp")
    if not isinstance(A, int) or not 0 <= A <= 100_000_000:
        malos.append("monthly_contribution_clp")
    if not isinstance(n, int) or not 1 <= n <= 600:
        malos.append("horizon_months")
    if malos:
        raise EntradaInvalida(malos)
    mon = meta["payment_currency"]
    costo = meta.get("estimated_cost")
    costo = Decimal(str(costo)) if costo not in (None, "") else None
    resultados = []
    for k, e in enumerate(escenarios, 1):
        resultados.append(_escenario(k, e, C, A, n, mon, costo, ahora_iso))
    return {"escenarios": resultados, "etiqueta": "Escenario hipotético con tus supuestos",
            "nota": "Es un cálculo con supuestos visibles, no un pronóstico ni una recomendación. Sin comisiones ni impuestos.",
            "datos_meta": {"capital": C, "aporte_mensual": A, "meses": n, "moneda": mon,
                           "costo": None if costo is None else str(costo)}}


def _escenario(k, e, C, A, n, mon, costo, ahora_iso):
    malos = []
    for clave in e:
        if clave not in ("nombre", "tipo_tasa", "tasa_anual_pct", "inflacion_cl_pct", "tc_inicial",
                         "inflacion_moneda_meta_pct", "variacion_tc_pct", "referencias", "origen"):
            malos.append(clave)
    if e.get("origen") not in (None, "persona"):
        raise EntradaInvalida(["origen_no_habilitado"])
    nombre = e.get("nombre") or f"Escenario {k}"
    if len(nombre) > 30:
        malos.append("nombre")
    if e.get("tipo_tasa") not in ("efectiva_anual", "nominal_anual_mensual"):
        malos.append("tipo_tasa")
    tasa = _pct(e.get("tasa_anual_pct"), "tasa_anual_pct", True, malos)
    pi_cl = _pct(e.get("inflacion_cl_pct"), "inflacion_cl_pct", False, malos)
    pi_m = _pct(e.get("inflacion_moneda_meta_pct"), "inflacion_moneda_meta_pct", False, malos)
    v = _pct(e.get("variacion_tc_pct"), "variacion_tc_pct", False, malos)
    tc0 = None
    if e.get("tc_inicial") not in (None, ""):
        try:
            tc0 = Decimal(str(e["tc_inicial"]))
            if not (0 < tc0 <= 1_000_000):
                malos.append("tc_inicial")
        except (InvalidOperation, ValueError):
            malos.append("tc_inicial")
    refs = e.get("referencias") or {}
    if not isinstance(refs, dict) or any(not isinstance(x, str) or len(x) > 80 for x in refs.values()):
        malos.append("referencias")
    if malos:
        raise EntradaInvalida(malos)
    with localcontext() as ctx:
        ctx.prec = 28
        r = (1 + tasa / 12) ** 12 - 1 if e["tipo_tasa"] == "nominal_anual_mensual" else tasa
        i = (1 + r) ** (Decimal(1) / 12) - 1
        f = (1 + i) ** n
        t = Decimal(n) / 12
        vf = C * f + (A * n if i == 0 else A * (f - 1) / i)
        out = {"nombre": nombre, "hipotetico": True, "perdida": r < 0,
               "tasa_efectiva_anual_pct": str((r * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
               "tipo_tasa": e["tipo_tasa"],
               "valor_final": _q(vf), "aportes": A * n, "interes": _q(vf) - C - A * n,
               "no_calculado": {}}
        out["poder_compra_hoy"] = _q(vf / (1 + pi_cl) ** t) if pi_cl is not None else None
        if pi_cl is None:
            out["no_calculado"]["poder_compra_hoy"] = NO_CALC["pi_cl"]
        costo_hoy = costo_fut = None
        if costo is None:
            out["no_calculado"]["brecha"] = NO_CALC["costo"]
        elif mon in ("CLP", "no_se"):
            costo_hoy = costo
            if pi_cl is not None:
                costo_fut = costo * (1 + pi_cl) ** t
            else:
                out["no_calculado"]["costo_futuro"] = NO_CALC["pi_cl"]
        elif tc0 is None:
            out["no_calculado"]["brecha"] = NO_CALC["tc"]
        else:
            costo_hoy = costo * tc0
            if pi_m is not None and v is not None:
                con_infl = costo * (1 + pi_m) ** t * tc0
                costo_fut = con_infl * (1 + v) ** t
                out["efecto_inflacion_meta"] = _q(con_infl) - _q(costo_hoy)
                out["efecto_tipo_cambio"] = _q(costo_fut) - _q(con_infl)
            else:
                out["no_calculado"]["costo_futuro"] = NO_CALC["ext"].format(m=mon)
        out["costo_hoy"] = _q(costo_hoy) if costo_hoy is not None else None
        out["brecha_hoy"] = C - _q(costo_hoy) if costo_hoy is not None else None
        out["costo_futuro"] = _q(costo_fut) if costo_fut is not None else None
        out["brecha_futura"] = out["valor_final"] - _q(costo_fut) if costo_fut is not None else None
        if costo_fut is not None:
            falta = costo_fut - C * f
            req = falta / n if i == 0 else falta * i / (f - 1)
            out["aporte_equivalente"] = int(max(Decimal(0), req).quantize(Decimal(1), rounding=ROUND_CEILING))
        else:
            out["aporte_equivalente"] = None
    sup = []
    for campo, unidad, valor in (("tasa_anual_pct", "% anual", e.get("tasa_anual_pct")),
                                 ("inflacion_cl_pct", "% anual", e.get("inflacion_cl_pct")),
                                 ("tc_inicial", "CLP por unidad", e.get("tc_inicial")),
                                 ("inflacion_moneda_meta_pct", "% anual", e.get("inflacion_moneda_meta_pct")),
                                 ("variacion_tc_pct", "% anual", e.get("variacion_tc_pct"))):
        if valor not in (None, ""):
            sup.append({"nombre": campo, "valor": str(valor), "unidad": unidad, "origen": "persona",
                        "referencia": refs.get(campo), "fuente": "Ingresado por ti", "fecha": ahora_iso})
    out["supuestos"] = sup
    return out
