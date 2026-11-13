"""Brújula Inversiones: aplicación web (FastAPI). Rutas de páginas y API de §6.5, seguridad de §6.6."""
import hashlib
import hmac
import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt

from . import config, db
from .agente import presupuesto
from .agente.explicacion import explicar
from .dominio import catalogo, politica as P
from .dominio.comparacion import TEXTO_ORDEN, comparar_alternativas, vista_alternativa
from .dominio.ficha import componer_ficha, mes_y_anio, pesos
from .dominio.meta import evaluar_meta, horizonte_meses, validar_bloque_b
from .dominio.perfil import EntradaInvalida, calcular_perfil
from .dominio.simulacion import simular_escenarios
from .salida import plantillas

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
RAIZ = Path(__file__).resolve().parents[1]
SCL = ZoneInfo("America/Santiago")
CFG = config.cargar()
ENG = db.motor(CFG.database_url)
db.migrar(ENG)
HISTORICO = json.loads((RAIZ / "data" / "historico_categorias_v1.json").read_text(encoding="utf-8"))
HISTORICO_SHA = hashlib.sha256((RAIZ / "data" / "historico_categorias_v1.json").read_bytes()).hexdigest()
GLOSARIO = json.loads((RAIZ / "data" / "glosario_v1.json").read_text(encoding="utf-8"))["terminos"]

app = FastAPI(title="Brújula Inversiones", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=RAIZ / "static"), name="static")
templates = Jinja2Templates(directory=RAIZ / "templates")
templates.env.globals.update(disclaimer=P.DISCLAIMER_V1_1, pesos=pesos, motivos=P.TEXTOS_MOTIVO,
                             significado_m3=P.SIGNIFICADO_M3)


def _scl(d) -> str:
    if isinstance(d, str):
        d = datetime.fromisoformat(d)
    d = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    return d.astimezone(SCL).strftime("%d-%m-%Y %H:%M")


templates.env.filters["scl"] = _scl

CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def err(status: int, code: str, message: str, fields=None, trace_id="") -> JSONResponse:
    return JSONResponse({"code": code, "message": message, "fields": fields or [], "trace_id": trace_id},
                        status_code=status)


class Fallo(Exception):
    def __init__(self, status, code, message, fields=None):
        self.status, self.code, self.message, self.fields = status, code, message, fields or []


@app.exception_handler(Fallo)
async def _fallo(request: Request, e: Fallo):
    return err(e.status, e.code, e.message, e.fields, getattr(request.state, "trace_id", ""))


@app.exception_handler(RequestValidationError)
async def _invalida(request: Request, e: RequestValidationError):
    campos = sorted({str(x["loc"][-1]) for x in e.errors() if x.get("loc")})
    return err(422, "entrada_invalida", "Revisa los campos indicados.", campos, getattr(request.state, "trace_id", ""))


@app.middleware("http")
async def seguridad(request: Request, call_next):
    request.state.trace_id = uuid.uuid4().hex[:16]
    ruta = request.url.path
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and ruta.startswith("/api/"):
        origen = (request.headers.get("origin") or "").rstrip("/")
        if origen not in CFG.allowed_origins:
            return err(403, "origen_no_permitido", "Origen no permitido.", trace_id=request.state.trace_id)
        cookie = request.cookies.get("bru_csrf", "")
        if not cookie or not hmac.compare_digest(cookie, request.headers.get("x-csrf-token", "")):
            return err(403, "csrf_invalido", "Recarga la página e intenta de nuevo.", trace_id=request.state.trace_id)
    try:
        resp = await call_next(request)
    except sa.exc.OperationalError:
        resp = err(503, "servicio_caido", "Servicio no disponible por un momento.", trace_id=request.state.trace_id)
    resp.headers["Content-Security-Policy"] = CSP
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    if ruta.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    if not ruta.startswith(("/api/", "/static/")) and "bru_csrf" not in request.cookies:
        resp.set_cookie("bru_csrf", secrets.token_urlsafe(24), httponly=False, samesite="strict",
                        secure=CFG.cookie_secure, path="/")
    return resp


# ---------------------------------------------------------------- sesión

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def sesion_actual(request: Request, conn, requerida=True):
    token = request.cookies.get("bru_sid")
    fila = None
    if token:
        fila = conn.execute(sa.select(db.sessions).where(db.sessions.c.token_hash == _hash(token))).mappings().first()
    if fila and _aware(fila["expires_at"]) <= ahora():
        conn.execute(db.sessions.delete().where(db.sessions.c.id == fila["id"]))
        if requerida:
            raise Fallo(401, "sesion_vencida", "Tu sesión venció; puedes iniciar otra.")
        return None
    if not fila and requerida:
        raise Fallo(401, "sesion_requerida", "Primero acepta el aviso de privacidad.")
    return fila


def corr(sid: str) -> str:
    return hmac.new(CFG.hmac_secret.encode(), sid.encode(), "sha256").hexdigest()[:16]


def auditar(conn, trace_id, sid, operation, status, error_code=None, tokens_in=None, tokens_out=None, model_id=None):
    conn.execute(db.audit_events.insert().values(
        trace_id=trace_id, corr_token=corr(sid) if sid else None, operation=operation, policy_version=P.POLICY_VERSION,
        prompt_version=P.PROMPT_VERSION, model_id=model_id, status=status, error_code=error_code, tokens_in=tokens_in,
        tokens_out=tokens_out, created_at=ahora()))


def ultimo(conn, tabla, sid):
    return conn.execute(sa.select(tabla).where(tabla.c.session_id == sid).order_by(tabla.c.version.desc())
                        .limit(1)).mappings().first()


def perfil_vigente(conn, sid):
    p = ultimo(conn, db.profiles, sid)
    if not p:
        return None, "sin_perfil"
    if p["status"] == "requiere_aclaracion":
        return p, "perfil_aclaracion"
    if _aware(p["valid_until"]) <= ahora() or p["questionnaire_version"] != P.QUESTIONNAIRE_VERSION \
            or p["policy_version"] != P.POLICY_VERSION:
        return p, "perfil_vencido"
    return p, "perfil_vigente"


def estado_sesion(conn, sid) -> dict:
    p, est = perfil_vigente(conn, sid)
    g = comp = None
    if est == "perfil_vigente":
        g = ultimo(conn, db.goals, sid)
        if g and g["profile_version"] == p["version"]:
            if g["status"] == "requiere_aclaracion":
                est = "meta_aclaracion"
            else:
                comp = conn.execute(sa.select(db.comparisons).where(
                    db.comparisons.c.session_id == sid, db.comparisons.c.status == "activa")).mappings().first()
                est = "listo" if not comp else ("comparacion" if comp["result"] == "comparacion" else "insuficiente")
        else:
            g = None
    return {"state": est, "profile": p, "goal": g, "comparison": comp}


def _historicas(conn, sid):
    conn.execute(db.comparisons.update().where(db.comparisons.c.session_id == sid,
                                               db.comparisons.c.status == "activa").values(status="historica"))


def _purgar(conn):
    conn.execute(db.sessions.delete().where(db.sessions.c.expires_at <= ahora()))
    conn.execute(db.audit_events.delete().where(db.audit_events.c.created_at <= ahora() - timedelta(days=7)))


def limite(conn, sid: str, clave: str):
    """Límite por sesión (§12.2), compartido por todas las réplicas a través de la base."""
    minuto = ahora().strftime("%Y%m%d%H%M")
    kh = hashlib.sha256(f"{clave}|{sid}".encode()).hexdigest()
    total = conn.execute(sa.select(sa.func.coalesce(sa.func.sum(db.rate_limits.c.count), 0))
                         .where(db.rate_limits.c.key_hash == kh)).scalar()
    actual = conn.execute(sa.select(db.rate_limits.c.count).where(
        db.rate_limits.c.key_hash == kh, db.rate_limits.c.window_start == minuto)).scalar()
    if (actual or 0) >= CFG.rate_limit_session_per_min or total >= CFG.rate_limit_session_total:
        raise Fallo(429, "limite_excedido", "Alcanzaste el límite de uso; intenta en un minuto.")
    if actual is None:
        conn.execute(db.rate_limits.insert().values(key_hash=kh, window_start=minuto, count=1))
    else:
        conn.execute(db.rate_limits.update().where(db.rate_limits.c.key_hash == kh,
                                                   db.rate_limits.c.window_start == minuto).values(count=actual + 1))


# ---------------------------------------------------------------- esquemas

class Estricto(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SesionIn(Estricto):
    consent: Literal[True]
    consent_version: str = Field(max_length=10)
    adult_declared: Literal[True]


class Borrar(Estricto):
    confirm: Literal[True]


class PerfilIn(Estricto):
    questionnaire_version: str = Field(max_length=10)
    t1: StrictInt
    t2: StrictInt
    t3: StrictInt
    t4: StrictInt
    k1: str = Field(max_length=12)
    k2: str = Field(max_length=4)
    e1: str = Field(max_length=10)
    f1: str = Field(max_length=24)


class MetaIn(Estricto):
    objective: str = Field(max_length=32)
    target_month: str = Field(max_length=7)
    max_wait_days: StrictInt
    amount_clp: StrictInt
    essential_need: str = Field(max_length=6)
    label: str | None = Field(default=None, max_length=60)
    estimated_cost: str | None = Field(default=None, max_length=16, pattern=r"^\d{1,10}(\.\d{1,2})?$")
    payment_currency: str = Field(max_length=5)
    monthly_contribution_clp: StrictInt


class EscenarioIn(Estricto):
    nombre: str | None = Field(default=None, max_length=30)
    tipo_tasa: Literal["efectiva_anual", "nominal_anual_mensual"]
    tasa_anual_pct: str = Field(max_length=12, pattern=r"^-?\d{1,3}(\.\d{1,4})?$")
    inflacion_cl_pct: str | None = Field(default=None, max_length=12, pattern=r"^-?\d{1,3}(\.\d{1,4})?$")
    tc_inicial: str | None = Field(default=None, max_length=14, pattern=r"^\d{1,7}(\.\d{1,4})?$")
    inflacion_moneda_meta_pct: str | None = Field(default=None, max_length=12, pattern=r"^-?\d{1,3}(\.\d{1,4})?$")
    variacion_tc_pct: str | None = Field(default=None, max_length=12, pattern=r"^-?\d{1,3}(\.\d{1,4})?$")
    referencias: dict[str, str] | None = None
    origen: str | None = Field(default=None, max_length=16)


class MetaSimIn(Estricto):
    amount_clp: StrictInt
    monthly_contribution_clp: StrictInt
    target_month: str = Field(max_length=7)
    estimated_cost: str | None = Field(default=None, max_length=16, pattern=r"^\d{1,10}(\.\d{1,2})?$")
    payment_currency: str = Field(max_length=5)


class SimularIn(Estricto):
    meta: MetaSimIn | None = None
    escenarios: list[EscenarioIn] = Field(min_length=1, max_length=3)


class ChatIn(Estricto):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, max_length=36)


def _vacio(cuerpo: bytes):
    if cuerpo and cuerpo.strip() not in (b"", b"{}"):
        raise Fallo(422, "entrada_invalida", "Esta operación no recibe datos.", ["body"])


# ---------------------------------------------------------------- salud

@app.get("/health")
def health():
    return {"status": "ok", "version": CFG.app_version, "git_sha": CFG.git_sha,
            "llm": {"modo": "real" if CFG.llm_real else "demo", "estado": presupuesto.estado(ENG, CFG)}}


@app.get("/ready")
def ready():
    try:
        with ENG.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        cat = catalogo.cargar()
        assert cat["source_id"] == P.SOURCE_ID and HISTORICO["historical_id"] == "HISTORICO_CATEGORIAS_V1"
    except Exception:
        return JSONResponse({"status": "no_listo"}, status_code=503)
    return {"status": "listo", "catalogo_sha256": cat["checksum_sha256"], "historico_sha256": HISTORICO_SHA}


# ---------------------------------------------------------------- API: sesión

@app.post("/api/session", status_code=201)
def crear_sesion(body: SesionIn, response: Response):
    if body.consent_version != P.CONSENT_VERSION:
        raise Fallo(409, "conflicto_version", "El aviso de privacidad cambió; recarga la página.")
    token, sid = secrets.token_urlsafe(32), str(uuid.uuid4())
    vence = ahora() + timedelta(hours=CFG.session_ttl_hours)
    with ENG.begin() as conn:
        _purgar(conn)
        conn.execute(db.sessions.insert().values(id=sid, token_hash=_hash(token), consent_version=body.consent_version,
                                                 adult_declared=True, created_at=ahora(), expires_at=vence))
    response.set_cookie("bru_sid", token, httponly=True, samesite="lax", secure=CFG.cookie_secure, path="/",
                        max_age=CFG.session_ttl_hours * 3600)
    return {"session_state": "sin_perfil", "expires_at": vence.isoformat()}


@app.get("/api/session")
def ver_sesion(request: Request):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        e = estado_sesion(conn, s["id"])
    return {"session_state": e["state"], "expires_at": _aware(s["expires_at"]).isoformat(),
            "profile_version": e["profile"]["version"] if e["profile"] else None,
            "goal_version": e["goal"]["version"] if e["goal"] else None}


@app.delete("/api/session", status_code=204)
async def borrar_sesion(request: Request):
    try:
        Borrar.model_validate_json(await request.body() or b"{}")
    except Exception:
        raise Fallo(422, "entrada_invalida", "Confirma el borrado.", ["confirm"])
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        conn.execute(db.sessions.delete().where(db.sessions.c.id == s["id"]))
    r = Response(status_code=204)
    r.delete_cookie("bru_sid", path="/")
    return r


# ---------------------------------------------------------------- API: perfil y meta

def _vista_perfil(p):
    if not p:
        return {"status": "inexistente"}
    r = p["result"]
    return {"version": p["version"], "status": p["status"], "tolerance": r["tolerance"],
            "capacity_cap": r["capacity_cap"], "effective_risk": r["effective_risk"], "reasons": r["reasons"],
            "motivo": r.get("motivo"), "preservation_by_capacity": r["preservation_by_capacity"],
            "calculated_at": _aware(p["calculated_at"]).isoformat(), "valid_until": _aware(p["valid_until"]).isoformat()}


@app.get("/api/profile")
def ver_perfil(request: Request):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        p, est = perfil_vigente(conn, s["id"])
    v = _vista_perfil(p)
    if est == "perfil_vencido":
        v["status"] = "vencido"
    return v


@app.post("/api/profile", status_code=201)
def crear_perfil(request: Request, body: PerfilIn):
    if body.questionnaire_version != P.QUESTIONNAIRE_VERSION:
        raise Fallo(409, "conflicto_version", "El cuestionario cambió; recarga la página.")
    respuestas = body.model_dump(exclude={"questionnaire_version"})
    try:
        r = calcular_perfil(respuestas)
    except EntradaInvalida as e:
        raise Fallo(422, "entrada_invalida", "Responde todas las preguntas.", e.fields)
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        prev = ultimo(conn, db.profiles, s["id"])
        version = (prev["version"] + 1) if prev else 1
        conn.execute(db.profiles.update().where(db.profiles.c.session_id == s["id"],
                                                db.profiles.c.status == "vigente").values(status="reemplazado"))
        _historicas(conn, s["id"])
        calc = ahora()
        vence = min(calc + timedelta(days=30 * CFG.profile_validity_months), _aware(s["expires_at"]))
        conn.execute(db.profiles.insert().values(
            session_id=s["id"], version=version, questionnaire_version=P.QUESTIONNAIRE_VERSION,
            policy_version=P.POLICY_VERSION, answers=respuestas, result=r, status=r["status"], calculated_at=calc,
            valid_until=vence))
        p = ultimo(conn, db.profiles, s["id"])
    return _vista_perfil(p)


def _vista_meta(g):
    if not g:
        return {"status": "inexistente"}
    return {"version": g["version"], "status": g["status"], "warnings": [
        {"codigo": w["codigo"], "texto": w["texto"]} for w in g["evaluation"]["warnings"]],
        "motivo": g["evaluation"].get("motivo"), "ficha": g["profile_card"], "data": g["data"]}


@app.get("/api/goal")
def ver_meta(request: Request):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        e = estado_sesion(conn, s["id"])
    return _vista_meta(e["goal"])


@app.post("/api/goal", status_code=201)
def crear_meta(request: Request, body: MetaIn):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        p, est = perfil_vigente(conn, s["id"])
        if est == "sin_perfil":
            raise Fallo(409, "perfil_requerido", "Primero responde el cuestionario de perfil.")
        if est == "perfil_vencido":
            raise Fallo(409, "perfil_vencido", "Tu perfil venció; responde el cuestionario de nuevo.")
        if est == "perfil_aclaracion":
            raise Fallo(409, "requiere_aclaracion", "Tu perfil requiere aclaración antes de registrar una meta.")
        try:
            m = validar_bloque_b(body.model_dump(), datetime.now(SCL))
        except EntradaInvalida as e:
            raise Fallo(422, "entrada_invalida", "Revisa los campos indicados.", e.fields)
        ev = evaluar_meta(m, p["result"])
        ficha = componer_ficha(p["result"], m, ev)
        prev = ultimo(conn, db.goals, s["id"])
        conn.execute(db.goals.update().where(db.goals.c.session_id == s["id"],
                                             db.goals.c.status == "vigente").values(status="reemplazada"))
        _historicas(conn, s["id"])
        datos = {**m, "estimated_cost": None if m["estimated_cost"] is None else str(m["estimated_cost"])}
        conn.execute(db.goals.insert().values(
            session_id=s["id"], version=(prev["version"] + 1) if prev else 1, profile_version=p["version"], data=datos,
            evaluation=ev, profile_card=ficha, status=ev["status"], created_at=ahora()))
        g = ultimo(conn, db.goals, s["id"])
    return _vista_meta(g)


# ---------------------------------------------------------------- API: comparación

def _vista_comparacion(c):
    pay = c["payload"]
    porid = catalogo.por_id()
    return {"id": c["id"], "status": pay["status"], "activa": c["status"] == "activa",
            "profile_reference": {"profile_version": c["profile_version"], "goal_version": c["goal_version"],
                                  "policy_version": c["policy_version"]},
            "alternatives": [vista_alternativa(porid[i]) for i in pay["selected_ids"]],
            "selected_ids": pay["selected_ids"], "other_eligible_ids": pay["other_eligible_ids"],
            "equivalents": pay["equivalentes"], "exclusions": pay["exclusions"],
            "limiting_conditions": pay["limiting_conditions"], "n_compatibles": pay.get("n_compatibles"),
            "warnings": pay.get("warnings", []), "ficha": pay["ficha"],
            "exposure_by_alternative": pay["exposure_by_alternative"], "orden": TEXTO_ORDEN,
            "summary": (plantillas.comparacion(pay["ficha"]["frase"]) if pay["status"] == "comparacion"
                        else plantillas.insuficiencia(pay["n_compatibles"], pay["limiting_conditions"])),
            "explanation": c["explanation"], "disclaimer": P.DISCLAIMER_V1_1}


@app.post("/api/compare")
async def comparar(request: Request):
    _vacio(await request.body())
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        e = estado_sesion(conn, s["id"])
        if e["state"] in ("sin_perfil", "perfil_vencido", "perfil_aclaracion"):
            raise Fallo(409, "perfil_requerido" if e["state"] == "sin_perfil" else
                        "perfil_vencido" if e["state"] == "perfil_vencido" else "requiere_aclaracion",
                        "Tu perfil no permite comparar todavía.")
        if e["state"] == "perfil_vigente":
            raise Fallo(409, "meta_requerida", "Primero registra tu meta.")
        if e["state"] == "meta_aclaracion":
            raise Fallo(409, "requiere_aclaracion", "Tu meta requiere aclaración antes de comparar.")
        p, g = e["profile"], e["goal"]
        meta = {**g["data"]}
        res = comparar_alternativas(p["result"], meta, g["evaluation"])
        res["warnings"] = [{"codigo": w["codigo"], "texto": w["texto"]} for w in g["evaluation"]["warnings"]]
        _historicas(conn, s["id"])
        r = conn.execute(db.comparisons.insert().values(
            session_id=s["id"], profile_version=p["version"], goal_version=g["version"],
            policy_version=P.POLICY_VERSION, status="activa",
            result="comparacion" if res["status"] == "comparacion" else "insuficiente", payload=res,
            created_at=ahora()))
        c = conn.execute(sa.select(db.comparisons).where(db.comparisons.c.id == r.inserted_primary_key[0])).mappings().one()
        auditar(conn, request.state.trace_id, s["id"], "comparar", res["status"])
    out = _vista_comparacion(c)
    out["trace_id"] = request.state.trace_id
    return out


@app.get("/api/comparisons")
def historial(request: Request):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        filas = conn.execute(sa.select(db.comparisons).where(db.comparisons.c.session_id == s["id"])
                             .order_by(db.comparisons.c.id.desc())).mappings().all()
    return {"comparisons": [{"id": c["id"], "status": "activa" if c["status"] == "activa" else "historica",
                             "result": c["result"], "selected_ids": c["payload"]["selected_ids"],
                             "created_at": _aware(c["created_at"]).isoformat()} for c in filas]}


@app.post("/api/comparisons/{cid}/explanation")
async def explicacion(request: Request, cid: int):
    _vacio(await request.body())
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        c = conn.execute(sa.select(db.comparisons).where(db.comparisons.c.id == cid, db.comparisons.c.session_id ==
                                                         s["id"])).mappings().first()
        if not c or c["result"] != "comparacion":
            raise Fallo(404, "no_encontrado", "No encontramos esa comparación.")
        if c["status"] != "activa":
            raise Fallo(409, "conflicto_version", "Esta comparación es histórica; vuelve a comparar.")
        if c["explanation"]:
            return {"comparison_id": cid, **c["explanation"], "disclaimer": P.DISCLAIMER_V1_1,
                    "trace_id": request.state.trace_id}
        limite(conn, s["id"], "explicacion")
        e = estado_sesion(conn, s["id"])
        p, g = e["profile"], e["goal"]
    trace, sid = request.state.trace_id, s["id"]

    def _aud(op, status, code, tin, tout):
        with ENG.begin() as cx:
            auditar(cx, trace, sid, op, status, code, tin, tout, CFG.llm_model)

    pr = {**p, "valid_until": _aware(p["valid_until"]).astimezone(SCL).isoformat()}
    res = explicar(ENG, CFG, pr, g, c, auditar=_aud)
    if res["generated_by"] == "llm":  # la plantilla no se guarda: la persona puede reintentar con IA
        with ENG.begin() as conn:
            conn.execute(db.comparisons.update().where(db.comparisons.c.id == cid).values(
                explanation=res, explanation_generated_by=res["generated_by"], explanation_model_id=res["model_id"],
                explanation_prompt_version=res["prompt_version"]))
    return {"comparison_id": cid, **res, "disclaimer": P.DISCLAIMER_V1_1, "trace_id": trace}


# ---------------------------------------------------------------- API: simulación, histórico y chat

@app.post("/api/simulate")
def simular(request: Request, body: SimularIn):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        e = estado_sesion(conn, s["id"])
    if body.meta is not None:
        m = body.meta.model_dump()
        if m["payment_currency"] not in P.MONEDAS_FIJAS and not (len(m["payment_currency"]) == 3 and
                                                                  m["payment_currency"].isalpha() and
                                                                  m["payment_currency"].isupper()):
            raise Fallo(422, "entrada_invalida", "Moneda inválida.", ["payment_currency"])
        try:
            m["horizon_months"] = horizonte_meses(m["target_month"], datetime.now(SCL))
        except EntradaInvalida:
            raise Fallo(422, "entrada_invalida", "La fecha de la meta debe ser futura.", ["target_month"])
    elif e["goal"]:
        m = e["goal"]["data"]
    else:
        raise Fallo(409, "meta_requerida", "Escribe los datos de tu meta.")
    escenarios = [x.model_dump(exclude_none=True) for x in body.escenarios]
    if any(x.get("origen") == "fuente_oficial" for x in escenarios):
        raise Fallo(422, "origen_no_habilitado", "En esta demo los supuestos los ingresas tú.", ["origen"])
    try:
        out = simular_escenarios(m, escenarios, datetime.now(SCL).isoformat(timespec="minutes"))
    except EntradaInvalida as ex:
        code = "origen_no_habilitado" if ex.fields == ["origen_no_habilitado"] else "entrada_invalida"
        raise Fallo(422, code, "Revisa los supuestos.", ex.fields)
    out["disclaimer"] = P.DISCLAIMER_V1_1
    out["aviso"] = plantillas.CALCULADORA if body.meta is not None else None
    return out


@app.get("/api/historico")
def historico():
    if not CFG.historico_enabled:
        raise Fallo(404, "no_encontrado", "No disponible.")
    return JSONResponse(HISTORICO, headers={"Cache-Control": "public, max-age=3600"})


EXPRESIONES_PERSONALES = ("invertir", "me conviene", "recomienda", "mi perfil", "mis alternativas", "cuál elijo",
                          "cual elijo")
EXPRESIONES_SIMULACION = ("simula", "cuánto tendré", "cuanto tendre", "me alcanza", "cuánto me falta", "cuanto me falta")


@app.post("/api/chat")
def chat(request: Request, body: ChatIn):
    """Chat en modo automático, sin IA (P0): glosario, derivación al simulador y plantillas del Anexo B."""
    with ENG.begin() as conn:
        s = sesion_actual(request, conn)
        limite(conn, s["id"], "chat")
        e = estado_sesion(conn, s["id"])
    texto = body.message.lower()
    status, next_step, summary = "educativo", "ninguno", None
    for termino, definicion in GLOSARIO.items():
        if termino in texto:
            summary = f"{termino.capitalize()}: {definicion}"
            break
    if summary is None and any(x in texto for x in EXPRESIONES_SIMULACION):
        summary = ("Para simular, usa el formulario «Simular mi meta»: escribe tu tasa y, si quieres, la inflación "
                   "que supones. La demo no propone valores.")
        next_step = "simular"
    elif summary is None and ("riesgo" in texto and ("importante" in texto or "principal" in texto)):
        summary = ("Los riesgos de tu ficha se revisan por separado: inflación chilena, moneda, mercado y liquidez. "
                   "Su peso depende de las alternativas, de la moneda de tu meta y de tus supuestos; por eso la demo "
                   "no los ordena.")
    elif summary is None and any(x in texto for x in EXPRESIONES_PERSONALES):
        st = e["state"]
        if st in ("sin_perfil", "perfil_vencido"):
            status, next_step = "perfil_requerido", "responder_cuestionario"
            summary = ("Para mostrarte alternativas adaptadas necesito que completes el cuestionario de perfil. "
                       "Mientras tanto, puedo explicarte conceptos como riesgo, liquidez o comisiones.")
        elif st in ("perfil_aclaracion", "meta_aclaracion"):
            status, next_step = "requiere_aclaracion", "consultar_profesional"
            summary = plantillas.aclaracion("tus respuestas requieren aclaración")
        elif st == "insuficiente":
            status, next_step = "alternativas_insuficientes", "actualizar_meta"
            summary = "Con tu meta actual no hay tres alternativas compatibles; revisa las condiciones limitantes."
        elif st == "comparacion":
            status, next_step = "comparacion", "ver_comparacion"
            summary = plantillas.comparacion(e["comparison"]["payload"]["ficha"]["frase"])
        else:
            next_step = "confirmar_meta" if st == "perfil_vigente" else "ver_comparacion"
            summary = "Registra tu meta y compara alternativas para ver diferencias entre ellas."
    if summary is None:
        summary = "Puedo explicarte conceptos como riesgo, horizonte, liquidez o comisiones. ¿Cuál te interesa?"
    return {"status": status, "summary": summary, "alternatives": [], "next_step": next_step,
            "generated_by": "plantilla", "rotulo": "Asistente en modo automático, sin IA. La explicación con IA está "
            "en la comparación.", "disclaimer": P.DISCLAIMER_V1_1, "trace_id": request.state.trace_id}


# ---------------------------------------------------------------- páginas

def _ctx(request: Request, **kw):
    with ENG.begin() as conn:
        s = sesion_actual(request, conn, requerida=False)
        e = estado_sesion(conn, s["id"]) if s else {"state": "sin_sesion", "profile": None, "goal": None,
                                                     "comparison": None}
        hist = []
        if s:
            hist = conn.execute(sa.select(db.comparisons.c.id, db.comparisons.c.status, db.comparisons.c.created_at)
                                .where(db.comparisons.c.session_id == s["id"])).mappings().all()
    return {"request": request, "sesion": s, "estado": e, "n_comparaciones": len(hist),
            "consent_version": P.CONSENT_VERSION, "questionnaire_version": P.QUESTIONNAIRE_VERSION,
            "contacto": CFG.privacy_contact_email, "historico_on": CFG.historico_enabled, **kw}


def pagina(request, plantilla, **kw):
    return templates.TemplateResponse(request, plantilla, _ctx(request, **kw))


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return pagina(request, "inicio.html")


@app.get("/privacidad", response_class=HTMLResponse)
def privacidad(request: Request):
    return pagina(request, "privacidad.html")


def _requiere_sesion(request):
    with ENG.begin() as conn:
        return sesion_actual(request, conn, requerida=False)


@app.get("/perfil", response_class=HTMLResponse)
def perfil_pag(request: Request):
    if not _requiere_sesion(request):
        return RedirectResponse("/privacidad", status_code=303)
    return pagina(request, "perfil.html")


@app.get("/perfil/resultado", response_class=HTMLResponse)
def perfil_resultado(request: Request):
    if not _requiere_sesion(request):
        return RedirectResponse("/privacidad", status_code=303)
    return pagina(request, "perfil_resultado.html", escalada=P.TEXTO_ESCALADA)


@app.get("/orientacion", response_class=HTMLResponse)
def orientacion(request: Request):
    return pagina(request, "orientacion.html", escalada=P.TEXTO_ESCALADA)


@app.get("/meta", response_class=HTMLResponse)
def meta_pag(request: Request):
    if not _requiere_sesion(request):
        return RedirectResponse("/privacidad", status_code=303)
    hoy = datetime.now(SCL)
    return pagina(request, "meta.html", mes_minimo=f"{hoy.year + (hoy.month // 12)}-{hoy.month % 12 + 1:02d}",
                  escalada=P.TEXTO_ESCALADA, mes_y_anio=mes_y_anio)


@app.get("/comparacion", response_class=HTMLResponse)
def comparacion_pag(request: Request):
    if not _requiere_sesion(request):
        return RedirectResponse("/privacidad", status_code=303)
    ctx = _ctx(request)
    comp = ctx["estado"]["comparison"]
    vista = _vista_comparacion(comp) if comp else None
    porid = catalogo.por_id()
    return templates.TemplateResponse(request, "comparacion.html", {**ctx, "comp": vista, "porid": porid,
                                                                    "pct": plantillas.pct})


@app.get("/calculadora", response_class=HTMLResponse)
def calculadora(request: Request):
    return pagina(request, "calculadora.html")


@app.get("/metodologia", response_class=HTMLResponse)
def metodologia(request: Request):
    return pagina(request, "metodologia.html", historico=HISTORICO, glosario=GLOSARIO, catalogo=catalogo.alternativas(),
                  pct=plantillas.pct)


@app.get("/mis-datos", response_class=HTMLResponse)
def mis_datos(request: Request):
    return pagina(request, "mis_datos.html")
