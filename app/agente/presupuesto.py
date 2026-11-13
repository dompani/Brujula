"""Límite de gasto de IA (§6.3): reserva previa con bloqueo, liquidación e interruptor."""
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import sqlalchemy as sa

from ..db import llm_spend

SCL = ZoneInfo("America/Santiago")
MILLON = Decimal(1_000_000)


def costo(cfg, tokens_in: int, tokens_out: int) -> Decimal:
    return (Decimal(tokens_in) * cfg.price_in + Decimal(tokens_out) * cfg.price_out) / MILLON


def _bloquear(conn) -> None:
    if conn.dialect.name == "postgresql":  # un solo reservador a la vez, aunque haya varias instancias
        conn.execute(sa.text("SELECT pg_advisory_xact_lock(72711)"))


def _usado(conn, columna, valor) -> Decimal:
    q = sa.select(sa.func.coalesce(sa.func.sum(sa.case(
        (llm_spend.c.status == "reservado", llm_spend.c.cost_reserved_usd),
        (llm_spend.c.status == "liquidado", llm_spend.c.cost_settled_usd), else_=0)), 0)).where(columna == valor)
    return Decimal(str(conn.execute(q).scalar() or 0))


def reservar(eng, cfg, operation: str, model_id: str, prompt_version: str, tokens_in_est: int,
             max_tokens: int, ahora: datetime | None = None):
    """Devuelve el id de la reserva, o None si no cabe en el límite diario o mensual."""
    ahora = (ahora or datetime.now(SCL)).astimezone(SCL)
    dia, mes = ahora.strftime("%Y-%m-%d"), ahora.strftime("%Y-%m")
    nueva = costo(cfg, tokens_in_est, max_tokens)
    with eng.begin() as conn:
        _bloquear(conn)
        if operation == "eval":
            if _usado(conn, llm_spend.c.operation, "eval") + nueva > cfg.budget_eval_usd:
                return None
        else:
            if _usado(conn, llm_spend.c.day, dia) + nueva > cfg.budget_daily_usd:
                return None
            if _usado(conn, llm_spend.c.month, mes) + nueva > cfg.budget_monthly_usd:
                return None
        r = conn.execute(llm_spend.insert().values(
            day=dia, month=mes, operation=operation, model_id=model_id, prompt_version=prompt_version,
            cost_reserved_usd=nueva, status="reservado", created_at=ahora))
        return r.inserted_primary_key[0]


def liquidar(eng, cfg, reserva_id: int, tokens_in: int | None, tokens_out: int | None) -> None:
    """Registra el costo real. Si la llamada falló sin informar tokens, la reserva se cuenta como gastada."""
    with eng.begin() as conn:
        fila = conn.execute(sa.select(llm_spend).where(llm_spend.c.id == reserva_id)).mappings().one()
        real = fila["cost_reserved_usd"] if tokens_in is None else costo(cfg, tokens_in, tokens_out or 0)
        conn.execute(llm_spend.update().where(llm_spend.c.id == reserva_id).values(
            tokens_in=tokens_in, tokens_out=tokens_out, cost_settled_usd=real, status="liquidado"))


def estado(eng, cfg) -> str:
    """activo, pausado_presupuesto o apagado (para /health; sin montos)."""
    if not cfg.llm_real or cfg.kill_switch:
        return "apagado"
    ahora = datetime.now(SCL)
    try:
        with eng.connect() as conn:
            dia = _usado(conn, llm_spend.c.day, ahora.strftime("%Y-%m-%d"))
            mes = _usado(conn, llm_spend.c.month, ahora.strftime("%Y-%m"))
    except Exception:
        return "activo"
    minimo = costo(cfg, 4000, 1500)
    if dia + minimo > cfg.budget_daily_usd or mes + minimo > cfg.budget_monthly_usd:
        return "pausado_presupuesto"
    return "activo"
