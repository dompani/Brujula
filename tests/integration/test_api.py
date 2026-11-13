"""Flujo completo por la API con SQLite, cliente falso y modo demo (sin red)."""
import os
import tempfile

os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL") or "sqlite:///" + os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["LLM_MODE"] = "demo"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import main  # noqa: E402
from app.agente.clientes.falso import ClienteFalso, borrador_valido  # noqa: E402
from app.agente.explicacion import explicar  # noqa: E402

ORIGEN = {"Origin": "http://testserver"}


def cliente():
    c = TestClient(main.app)
    c.get("/")
    c.headers.update({**ORIGEN, "X-CSRF-Token": c.cookies.get("bru_csrf")})
    return c


def emiliana(c):
    assert c.post("/api/session", json={"consent": True, "consent_version": "1.0", "adult_declared": True}).status_code == 201
    r = c.post("/api/profile", json={"questionnaire_version": "1.3", "t1": 0, "t2": 0, "t3": 1, "t4": 1,
                                     "k1": "ninguna", "k2": "si", "e1": "basica", "f1": "no"})
    assert r.status_code == 201 and r.json()["effective_risk"] == "conservador"
    from datetime import datetime
    from zoneinfo import ZoneInfo
    hoy = datetime.now(ZoneInfo("America/Santiago"))
    mes = f"{hoy.year + 3}-{hoy.month:02d}"
    r = c.post("/api/goal", json={"objective": "meta_concreta", "target_month": mes, "max_wait_days": 180,
                                  "amount_clp": 10000000, "essential_need": "no", "estimated_cost": "12000000",
                                  "payment_currency": "no_se", "monthly_contribution_clp": 0})
    assert r.status_code == 201, r.text
    return r.json()


def test_flujo_emiliana_y_explicacion_sin_ia():
    c = cliente()
    g = emiliana(c)
    assert [w["codigo"] for w in g["warnings"]] == ["W1", "W4", "W5"]
    r = c.post("/api/compare")
    assert r.status_code == 200
    comp = r.json()
    assert comp["selected_ids"] == ["D01", "D03", "D09"] and comp["other_eligible_ids"] == ["D02"]
    assert c.get("/api/session").json()["session_state"] == "comparacion"
    r = c.post(f"/api/comparisons/{comp['id']}/explanation")
    d = r.json()
    assert r.status_code == 200 and d["generated_by"] == "plantilla" and d["motivo"] == "modo_demo"
    assert [e["id"] for e in d["explicaciones"]] == ["D01", "D03", "D09"]
    for p in ("/", "/perfil/resultado", "/meta", "/comparacion", "/metodologia", "/mis-datos", "/calculadora"):
        assert c.get(p).status_code == 200, p


def test_csrf_y_origen():
    c = TestClient(main.app)
    c.get("/")
    cuerpo = {"consent": True, "consent_version": "1.0", "adult_declared": True}
    assert c.post("/api/session", json=cuerpo, headers=ORIGEN).json()["code"] == "csrf_invalido"
    r = c.post("/api/session", json=cuerpo, headers={"Origin": "https://malo.example", "X-CSRF-Token": c.cookies.get("bru_csrf")})
    assert r.status_code == 403 and r.json()["code"] == "origen_no_permitido"


def test_meta_sin_perfil_y_campos_extra():
    c = cliente()
    c.post("/api/session", json={"consent": True, "consent_version": "1.0", "adult_declared": True})
    r = c.post("/api/goal", json={"objective": "meta_concreta", "target_month": "2030-01", "max_wait_days": 7,
                                  "amount_clp": 100000, "essential_need": "no", "payment_currency": "CLP",
                                  "monthly_contribution_clp": 0})
    assert r.status_code == 409 and r.json()["code"] == "perfil_requerido"
    r = c.post("/api/profile", json={"questionnaire_version": "1.3", "t1": 0, "t2": 0, "t3": 0, "t4": 0,
                                     "k1": "mas_10", "k2": "si", "e1": "basica", "f1": "si", "riesgo": "arriesgado"})
    assert r.status_code == 422
    r = c.post("/api/goal", json={"objective": "x", "amount_clp": "10.000.000"})
    assert r.status_code == 422


def test_sin_sesion_y_borrado():
    c = cliente()
    assert c.get("/api/session").status_code == 401
    emiliana(c)
    assert c.request("DELETE", "/api/session", json={"confirm": True}).status_code == 204
    assert c.get("/api/session").status_code == 401


def test_calculadora_y_fuente_oficial():
    c = cliente()
    c.post("/api/session", json={"consent": True, "consent_version": "1.0", "adult_declared": True})
    r = c.post("/api/simulate", json={"meta": {"amount_clp": 1000000, "monthly_contribution_clp": 0,
                                               "target_month": "2030-01", "payment_currency": "CLP"},
                                      "escenarios": [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "5"}]})
    assert r.status_code == 200 and r.json()["escenarios"][0]["valor_final"] > 1000000
    r = c.post("/api/simulate", json={"meta": {"amount_clp": 1000000, "monthly_contribution_clp": 0,
                                               "target_month": "2030-01", "payment_currency": "CLP"},
                                      "escenarios": [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "5",
                                                      "origen": "fuente_oficial"}]})
    assert r.status_code == 422 and r.json()["code"] == "origen_no_habilitado"


def _filas(c):
    import sqlalchemy as sa
    with main.ENG.begin() as conn:
        comp = conn.execute(sa.select(main.db.comparisons).order_by(main.db.comparisons.c.id.desc())).mappings().first()
        sid = comp["session_id"]
        e = main.estado_sesion(conn, sid)
    p = {**e["profile"], "valid_until": "2027-01-01T00:00:00-03:00"}
    return p, e["goal"], comp


class CfgReal:
    llm_real, kill_switch, llm_model = True, False, "modelo-de-prueba"

    def __getattr__(self, k):
        return getattr(main.CFG, k)


def test_explicacion_con_cliente_falso_valido_reparado_y_plantilla():
    c = cliente()
    emiliana(c)
    c.post("/api/compare")
    p, g, comp = _filas(c)
    ids = comp["payload"]["selected_ids"]
    cfg = CfgReal()
    r = explicar(main.ENG, cfg, p, g, comp, cliente=ClienteFalso([borrador_valido(ids)]))
    assert r["generated_by"] == "llm" and [e["id"] for e in r["explicaciones"]] == ids
    malo = dict(borrador_valido(ids), summary="Garantizado: ganarás 5 % al año con D04.")
    falso = ClienteFalso([malo, borrador_valido(ids)])
    r = explicar(main.ENG, cfg, p, g, comp, cliente=falso)
    assert r["generated_by"] == "llm" and len(falso.llamadas) == 2
    r = explicar(main.ENG, cfg, p, g, comp, cliente=ClienteFalso([malo, malo]))
    assert r["generated_by"] == "plantilla" and r["motivo"] == "borrador_invalido"
    r = explicar(main.ENG, cfg, p, g, comp, cliente=ClienteFalso(fallar=True))
    assert r["generated_by"] == "plantilla" and r["motivo"] == "proveedor_no_disponible"


def test_presupuesto_agotado():
    from decimal import Decimal
    c = cliente()
    emiliana(c)
    c.post("/api/compare")
    p, g, comp = _filas(c)

    class Pobre(CfgReal):
        budget_daily_usd = Decimal("0.001")
    r = explicar(main.ENG, Pobre(), p, g, comp, cliente=ClienteFalso([borrador_valido(comp["payload"]["selected_ids"])]))
    assert r["generated_by"] == "plantilla" and r["motivo"] == "presupuesto_agotado"


def test_health_y_ready():
    c = TestClient(main.app)
    h = c.get("/health").json()
    assert h["llm"]["modo"] == "demo" and "git_sha" in h
    assert c.get("/ready").json()["status"] == "listo"
    assert c.get("/api/historico").status_code == 200
