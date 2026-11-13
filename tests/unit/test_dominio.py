"""Casos verificados del SPEC: §3.2 (P1–P6), §3.3 (Emiliana), §7.4 (selección) y §7.5 (simulación)."""
from datetime import datetime

import pytest

from app.dominio import catalogo
from app.dominio.comparacion import comparar_alternativas
from app.dominio.elegibilidad import condiciones_limitantes, filtrar_alternativas
from app.dominio.ficha import componer_ficha
from app.dominio.meta import evaluar_meta, validar_bloque_b
from app.dominio.perfil import EntradaInvalida, calcular_perfil
from app.dominio.seleccion import seleccionar
from app.dominio.simulacion import simular_escenarios

HOY = datetime(2026, 11, 13)


def bloque_a(t, k1, k2="si", e1="basica", f1="si"):
    return {"t1": t[0], "t2": t[1], "t3": t[2], "t4": t[3], "k1": k1, "k2": k2, "e1": e1, "f1": f1}


@pytest.mark.parametrize("t,k1,k2,esperado", [
    ((0, 0, 1, 1), "mas_10", "si", "conservador"),
    ((1, 1, 1, 0), "mas_10", "si", "moderado"),
    ((2, 2, 2, 2), "hasta_10", "si", "moderado"),
    ((2, 2, 2, 2), "ninguna", "si", "conservador"),
    ((2, 1, 2, 1), "no_se", "si", None),
    ((1, 1, 1, 1), "mas_10", "no", None),
])
def test_perfiles_p1_a_p6(t, k1, k2, esperado):
    p = calcular_perfil(bloque_a(t, k1, k2))
    assert p["effective_risk"] == esperado
    assert p["status"] == ("vigente" if esperado else "requiere_aclaracion")


def test_p4_preservacion_por_capacidad():
    p = calcular_perfil(bloque_a((2, 2, 2, 2), "ninguna"))
    assert p["preservation_by_capacity"] and p["tolerance"] == "arriesgado"


def test_bloque_a_invalido():
    with pytest.raises(EntradaInvalida) as e:
        calcular_perfil({"t1": 3, "t2": 0, "t3": 0, "t4": 0, "k1": "x", "k2": "si", "e1": "basica", "f1": "si"})
    assert set(e.value.fields) == {"t1", "k1"}


def caso_sel(perfil, monto, h, ret, pres):
    eleg, excl = filtrar_alternativas(catalogo.alternativas(), perfil, monto, h, ret, pres)
    return eleg, excl, seleccionar(eleg, perfil)


@pytest.mark.parametrize("nombre,perfil,monto,h,ret,pres,esperado", [
    ("A07", "conservador", 100_000, 12, 30, False, ["D01", "D02", "D03"]),
    ("A08", "conservador", 100_000, 12, 30, True, ["D01", "D02", "D03"]),
    ("A09", "conservador", 100_000, 1, 0, False, 1),
    ("A10", "conservador", 5_000, 12, 30, False, 2),
    ("A23", "moderado", 1_000_000, 36, 7, False, ["D01", "D04", "D05"]),
    ("A24", "arriesgado", 1_000_000, 60, 7, False, ["D01", "D05", "D07"]),
    ("A25", "arriesgado", 1_000_000, 36, 7, False, ["D01", "D04", "D05"]),
    ("A26", "arriesgado", 1_000_000, 12, 30, True, ["D01", "D02", "D03"]),
    ("A34", "moderado", 1_000_000, 12, 7, False, ["D01", "D02", "D04"]),
    ("A37", "conservador", 10_000_000, 36, 180, True, ["D01", "D03", "D09"]),
    ("Emiliana 30", "conservador", 10_000_000, 36, 30, True, ["D01", "D02", "D03"]),
    ("Emiliana 7", "conservador", 10_000_000, 36, 7, True, 2),
    ("A38", "conservador", 10_000_000, 36, 0, True, 1),
])
def test_seleccion_catalogo_v3(nombre, perfil, monto, h, ret, pres, esperado):
    _, _, s = caso_sel(perfil, monto, h, ret, pres)
    if isinstance(esperado, list):
        assert s["seleccion"] == esperado, nombre
    else:
        assert not s["suficiente"] and s["n_distintas"] == esperado, nombre


def test_a09_y_a38_condiciones_limitantes():
    cat = catalogo.alternativas()
    _, excl = filtrar_alternativas(cat, "conservador", 100_000, 1, 0, False)
    assert [(c["codigo"], c["conteo"]) for c in condiciones_limitantes(cat, "conservador", excl)][:2] == \
        [("retiro", 4), ("horizonte", 3)]
    _, excl = filtrar_alternativas(cat, "conservador", 10_000_000, 36, 0, True)
    assert [(c["codigo"], c["conteo"]) for c in condiciones_limitantes(cat, "conservador", excl)] == \
        [("retiro", 4), ("preservacion", 1)]


def test_a50_equivalentes():
    d10 = dict(catalogo.por_id()["D01"], id="D10")
    cat = catalogo.alternativas() + [d10]
    eleg, _ = filtrar_alternativas(cat, "conservador", 100_000, 12, 30, False)
    s = seleccionar(eleg, "conservador")
    assert s["seleccion"] == ["D01", "D02", "D03"] and s["equivalentes"] == {"D10": "D01"}


def emiliana():
    perfil = calcular_perfil(bloque_a((0, 0, 1, 1), "ninguna", f1="no"))
    meta = validar_bloque_b({"objective": "meta_concreta", "target_month": "2029-11", "max_wait_days": 180,
                             "amount_clp": 10_000_000, "essential_need": "no", "estimated_cost": "12000000",
                             "payment_currency": "no_se", "monthly_contribution_clp": 0}, HOY)
    return perfil, meta, evaluar_meta(meta, perfil)


def test_emiliana_ficha_y_comparacion():
    perfil, meta, ev = emiliana()
    assert meta["horizon_months"] == 36 and ev["preservacion_origen"] == ["capacidad"]
    assert [w["codigo"] for w in ev["warnings"]] == ["W1", "W4", "W5"]
    comp = comparar_alternativas(perfil, meta, ev)
    assert comp["selected_ids"] == ["D01", "D03", "D09"] and comp["other_eligible_ids"] == ["D02"]
    f = comp["ficha"]
    assert f["frase"] == ("Perfil conservador · meta concreta para noviembre de 2029 (mediano plazo) · liquidez "
                          "requerida baja · aporte mensual $0 (declarado). Riesgos a revisar por separado: inflación "
                          "chilena (aplica), moneda (por confirmar), mercado (no aplica a las alternativas "
                          "comparadas), liquidez (controlada por el filtro).")
    assert f["brecha_hoy"] == "falta" and f["brecha_hoy_valor"] == -2_000_000 and f["faltante"] == ["moneda"]
    assert comp["exposure_by_alternative"]["D09"] == {"mercado": "no_expuesta", "inflacion_cl": "reajusta",
                                                      "moneda_meta": "por_confirmar"}


def test_meta_en_mes_actual_invalida():
    with pytest.raises(EntradaInvalida):
        validar_bloque_b({"objective": "meta_concreta", "target_month": "2026-11", "max_wait_days": 7,
                          "amount_clp": 100_000, "essential_need": "no", "payment_currency": "CLP",
                          "monthly_contribution_clp": 0}, HOY)


def test_puerta_de_meta():
    perfil, meta, _ = emiliana()
    meta["essential_need"] = "no_se"
    assert evaluar_meta(meta, perfil)["status"] == "requiere_aclaracion"


def sim(C, n, esc, A=0, costo=None, mon="CLP"):
    return simular_escenarios({"amount_clp": C, "monthly_contribution_clp": A, "horizon_months": n,
                               "estimated_cost": costo, "payment_currency": mon}, esc, "2026-11-13T10:00:00-03:00")


def test_a16_a54():
    r = sim(1_000_000, 12, [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "5"}])["escenarios"][0]
    assert r["valor_final"] == 1_050_000 and r["interes"] == 50_000 and r["poder_compra_hoy"] is None
    r = sim(1_000_000, 12, [{"tipo_tasa": "nominal_anual_mensual", "tasa_anual_pct": "6"}])["escenarios"][0]
    assert r["tasa_efectiva_anual_pct"] == "6.17" and r["valor_final"] == 1_061_678


def test_a39_a45_emiliana():
    r = sim(10_000_000, 36, [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "0", "inflacion_cl_pct": "3"}],
            costo="12000000")["escenarios"][0]
    assert (r["valor_final"], r["poder_compra_hoy"], r["brecha_hoy"], r["costo_futuro"], r["brecha_futura"],
            r["aporte_equivalente"]) == (10_000_000, 9_151_417, -2_000_000, 13_112_724, -3_112_724, 86_465)
    r = sim(10_000_000, 36, [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "4", "inflacion_cl_pct": "3"}],
            A=100_000, costo="12000000")["escenarios"][0]
    assert (r["valor_final"], r["aportes"], r["interes"], r["poder_compra_hoy"], r["brecha_futura"],
            r["aporte_equivalente"]) == (15_062_749, 3_600_000, 1_462_749, 13_784_549, 1_950_025, 48_874)


def test_a46_a47_europa():
    e = {"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "0", "tc_inicial": "1000",
         "inflacion_moneda_meta_pct": "2", "variacion_tc_pct": "4"}
    r = sim(10_000_000, 36, [e], costo="9000", mon="EUR")["escenarios"][0]
    assert (r["costo_hoy"], r["brecha_hoy"], r["efecto_inflacion_meta"], r["efecto_tipo_cambio"], r["costo_futuro"],
            r["brecha_futura"], r["aporte_equivalente"]) == (9_000_000, 1_000_000, 550_872, 1_192_560, 10_743_432,
                                                              -743_432, 20_651)
    r = sim(10_000_000, 36, [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "0"}], costo="9000",
            mon="EUR")["escenarios"][0]
    assert r["brecha_hoy"] is None and "brecha" in r["no_calculado"]
    r = sim(10_000_000, 36, [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "0", "tc_inicial": "1000"}],
            costo="9000", mon="EUR")["escenarios"][0]
    assert r["brecha_hoy"] == 1_000_000 and r["costo_futuro"] is None


def test_a49_tres_escenarios():
    esc = [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": r, "inflacion_cl_pct": p}
           for r, p in (("0", "2"), ("3", "3"), ("-5", "4"))]
    rs = sim(10_000_000, 36, esc, costo="12000000")["escenarios"]
    assert [x["brecha_futura"] for x in rs] == [-2_734_496, -2_185_454, -4_924_618]
    assert [x["aporte_equivalente"] for x in rs] == [75_959, 58_127, 147_275]
    assert rs[2]["perdida"]


def test_origen_fuente_oficial_rechazado():
    with pytest.raises(EntradaInvalida) as e:
        sim(1_000_000, 12, [{"tipo_tasa": "efectiva_anual", "tasa_anual_pct": "5", "origen": "fuente_oficial"}])
    assert e.value.fields == ["origen_no_habilitado"]
