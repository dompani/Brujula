"""Validación de la meta, puerta de meta y advertencias: reglas R-06 a R-09 (§3.2)."""
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from . import politica as P
from .perfil import EntradaInvalida

RE_MES = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
RE_MONEDA = re.compile(r"^[A-Z]{3}$")


def horizonte_meses(target_month: str, hoy: datetime) -> int:
    m = RE_MES.match(target_month or "")
    if not m:
        raise EntradaInvalida(["target_month"])
    n = int(m.group(1)) * 12 + int(m.group(2)) - (hoy.year * 12 + hoy.month)
    if not 1 <= n <= 600:
        raise EntradaInvalida(["target_month"])
    return n


def validar_bloque_b(g: dict, hoy: datetime) -> dict:
    """R-06: valida el bloque B y deriva el horizonte. Devuelve la meta normalizada."""
    malos = []
    if g.get("objective") not in P.OPCIONES_M1:
        malos.append("objective")
    if g.get("max_wait_days") not in P.OPCIONES_M3:
        malos.append("max_wait_days")
    if not isinstance(g.get("amount_clp"), int) or not 1_000 <= g["amount_clp"] <= 1_000_000_000:
        malos.append("amount_clp")
    if g.get("essential_need") not in P.OPCIONES_M5:
        malos.append("essential_need")
    if g.get("label") is not None and (not isinstance(g["label"], str) or len(g["label"]) > 60):
        malos.append("label")
    mon = g.get("payment_currency")
    if not isinstance(mon, str) or not (mon in P.MONEDAS_FIJAS or RE_MONEDA.match(mon)):
        malos.append("payment_currency")
    ap = g.get("monthly_contribution_clp")
    if not isinstance(ap, int) or not 0 <= ap <= 100_000_000:
        malos.append("monthly_contribution_clp")
    costo = None
    if g.get("estimated_cost") not in (None, ""):
        try:
            costo = Decimal(str(g["estimated_cost"]))
            pesos = mon in ("CLP", "no_se")
            if not (0 < costo <= 1_000_000_000) or (pesos and costo != costo.to_integral_value()) \
                    or costo.as_tuple().exponent < -2:
                malos.append("estimated_cost")
        except (InvalidOperation, ValueError):
            malos.append("estimated_cost")
    try:
        n = horizonte_meses(g.get("target_month"), hoy)
    except EntradaInvalida:
        malos.append("target_month")
        n = None
    if malos:
        raise EntradaInvalida(malos)
    return {**g, "estimated_cost": costo, "horizon_months": n}


def evaluar_meta(meta: dict, perfil: dict) -> dict:
    """R-07 (puerta), R-08 (preservación) y R-09 (advertencias W1 a W5)."""
    origen = []
    if perfil["capacidad_declarada"] == "ninguna":
        origen.append("capacidad")
    if meta["objective"] == "preservar_capital":
        origen.append("objetivo")
    status, motivo = "vigente", None
    if meta["essential_need"] in ("si", "no_se"):
        status = "requiere_aclaracion"
        motivo = ("podrías necesitar este monto para gastos esenciales en los próximos doce meses"
                  if meta["essential_need"] == "si" else
                  "no sabes si necesitarás este monto para gastos esenciales en los próximos doce meses")
    return {"status": status, "motivo": motivo, "preservacion": bool(origen), "preservacion_origen": origen,
            "warnings": advertencias(meta, perfil)}


def advertencias(meta: dict, perfil: dict) -> list[dict]:
    w = []
    mon = meta["payment_currency"]
    if perfil["fondo_emergencia"] == "no":
        w.append({"codigo": "W1", "texto": "Indicaste que no tienes un fondo de emergencia separado de este monto: "
                  "conviene contar con uno.",
                  "contexto": "La persona indicó que no tiene un fondo de emergencia separado de este monto; "
                  "conviene contar con uno."})
    if meta["objective"] == "crecimiento_largo_plazo" and meta["horizon_months"] < P.UMBRAL_W2_MESES:
        t = ("Buscas crecimiento de largo plazo, pero necesitarás el dinero en menos de tres años: "
             "hay una tensión entre tu objetivo y tu horizonte.")
        w.append({"codigo": "W2", "texto": t, "contexto": t})
    if perfil["experiencia"] == "ninguna" and perfil.get("effective_risk") != "conservador":
        t = ("Si nunca has invertido, considera que las alternativas que no preservan capital pueden bajar "
             "de valor temporalmente; es una fluctuación normal, no un error.")
        w.append({"codigo": "W3", "texto": t, "contexto": t})
    if mon in ("CLP", "no_se") and meta["horizon_months"] >= 12:
        t = "Con inflación, un monto fijo en pesos compra menos con el tiempo."
        w.append({"codigo": "W4", "texto": t, "contexto": t})
    if mon == "no_se":
        t = "Confirma la moneda en que se pagará la meta."
        w.append({"codigo": "W5", "texto": t, "contexto": t})
    elif mon != "CLP":
        t = (f"Tu meta se paga en {mon}: su costo en pesos cambia con el tipo de cambio y con la inflación de "
             f"esa moneda. Una alternativa reajustable en UF sigue la inflación chilena, pero no asegura cubrir "
             f"un gasto en {mon}.")
        w.append({"codigo": "W5", "texto": t, "contexto": t})
    return w
