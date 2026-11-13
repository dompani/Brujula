"""Verificación ejecutable de los ejemplos de §7.4 (selección) y §7.5 (simulación) del SPEC.

Uso: python analisis/verificar_reglas_catalogo_v3.py   (termina con código 1 si algún caso no coincide)
"""
from decimal import Decimal as D, getcontext, ROUND_HALF_UP, ROUND_CEILING

getcontext().prec = 28
NIV = {"conservador": 1, "moderado": 2, "arriesgado": 3}
ORDEN_MOTIVOS = ["riesgo", "monto_minimo", "horizonte", "retiro", "preservacion"]

# id, clase, riesgo, h_min, retiro, monto_min, preserva, reajusta
CAT_V3 = [
    ("D01", "liquidez", 1, 1, 0, 1_000, True, False),
    ("D02", "liquidez", 1, 1, 7, 1_000, True, False),   # v3: aviso de 7 días (antes 0)
    ("D03", "renta_fija", 1, 3, 30, 10_000, True, False),
    ("D04", "renta_fija", 1, 6, 7, 10_000, False, False),
    ("D05", "mixto", 2, 24, 7, 10_000, False, False),
    ("D06", "mixto", 2, 36, 7, 10_000, False, False),
    ("D07", "renta_variable", 3, 60, 7, 10_000, False, False),
    ("D08", "renta_variable", 3, 60, 7, 10_000, False, False),
    ("D09", "reajustable", 1, 3, 90, 10_000, True, True),
]


def firma(d):  # atributos que definen equivalencia (SEL-0)
    return (d[1], d[2], d[3], d[4], d[6], d[7])


def filtrar(cat, nivel, monto, h, ret, pres):
    eleg, excl = [], {}
    for d in cat:
        m = []
        if d[2] > nivel: m.append("riesgo")
        if monto < d[5]: m.append("monto_minimo")
        if h < d[3]: m.append("horizonte")
        if d[4] > ret: m.append("retiro")
        if pres and not d[6]: m.append("preservacion")
        (excl.__setitem__(d[0], m) if m else eleg.append(d))
    return eleg, excl


def seleccionar(eleg, nivel):
    orden = sorted(eleg, key=lambda d: (d[2], d[0]))
    distintas, equivalentes, vistas = [], {}, {}
    for d in orden:  # SEL-0
        f = firma(d)
        if f in vistas: equivalentes[d[0]] = vistas[f]
        else: vistas[f] = d[0]; distintas.append(d)
    if len(distintas) < 3:
        return None, equivalentes, len(distintas)
    sel = []
    for n in range(1, nivel + 1):
        c = [d for d in distintas if d[2] == n and d not in sel]
        if c: sel.append(c[0])
        if len(sel) == 3: break
    while len(sel) < 3:
        clases = {d[1] for d in sel}
        resto = [d for d in distintas if d not in sel]
        sel.append(([d for d in resto if d[1] not in clases] or resto)[0])
    return [d[0] for d in sorted(sel, key=lambda d: (d[2], d[0]))], equivalentes, len(distintas)


def limitantes(cat, nivel, excl):
    c = {}
    for d in cat:
        if d[2] <= nivel and d[0] in excl:
            for m in excl[d[0]]: c[m] = c.get(m, 0) + 1
    return sorted(c.items(), key=lambda kv: (-kv[1], ORDEN_MOTIVOS.index(kv[0])))


def caso(nombre, perfil, monto, h, ret, pres, esperado, cat=CAT_V3):
    eleg, excl = filtrar(cat, NIV[perfil], monto, h, ret, pres)
    sel, eq, n = seleccionar(eleg, NIV[perfil])
    res = sel if sel else f"insuficiente({n})"
    ok = res == esperado
    extra = "" if sel else f" limitantes={limitantes(cat, NIV[perfil], excl)}"
    otras = [d[0] for d in eleg if sel and d[0] not in sel]
    print(f"{'OK ' if ok else 'ERR'} {nombre}: elegibles={[d[0] for d in eleg]} -> {res} otras={otras}{extra}")
    return ok


ok = True
print("== Selección con catálogo v3")
ok &= caso("A07", "conservador", 100_000, 12, 30, False, ["D01", "D02", "D03"])
ok &= caso("A08", "conservador", 100_000, 12, 30, True, ["D01", "D02", "D03"])
ok &= caso("A09", "conservador", 100_000, 1, 0, False, "insuficiente(1)")
ok &= caso("A10", "conservador", 5_000, 12, 30, False, "insuficiente(2)")
ok &= caso("A23", "moderado", 1_000_000, 36, 7, False, ["D01", "D04", "D05"])
ok &= caso("A24", "arriesgado", 1_000_000, 60, 7, False, ["D01", "D05", "D07"])
ok &= caso("A25", "arriesgado", 1_000_000, 36, 7, False, ["D01", "D04", "D05"])
ok &= caso("A26", "arriesgado", 1_000_000, 12, 30, True, ["D01", "D02", "D03"])
ok &= caso("A34", "moderado", 1_000_000, 12, 7, False, ["D01", "D02", "D04"])
ok &= caso("A37 Emiliana 180", "conservador", 10_000_000, 36, 180, True, ["D01", "D03", "D09"])
ok &= caso("Emiliana 30", "conservador", 10_000_000, 36, 30, True, ["D01", "D02", "D03"])
ok &= caso("Emiliana 7", "conservador", 10_000_000, 36, 7, True, "insuficiente(2)")
ok &= caso("A38 Emiliana 0", "conservador", 10_000_000, 36, 0, True, "insuficiente(1)")

print("\n== SEL-0 con fixture de prueba que duplica D01")
dup = CAT_V3 + [("D10", "liquidez", 1, 1, 0, 1_000, True, False)]
ok &= caso("A50a duplicado, A07", "conservador", 100_000, 12, 30, False, ["D01", "D02", "D03"], dup)
solo_eq = [CAT_V3[0], ("D10", "liquidez", 1, 1, 0, 1_000, True, False), CAT_V3[2]]
eleg, _ = filtrar(solo_eq, 1, 100_000, 12, 30, False)
sel, eq, n = seleccionar(eleg, 1)
good = sel is None and n == 2 and eq == {"D10": "D01"}; ok &= good
print(f"{'OK ' if good else 'ERR'} A50b tres elegibles con dos equivalentes -> insuficiente({n}); equivalentes={eq}")


def q(x): return x.quantize(D(1), rounding=ROUND_HALF_UP)


def simular(C, r, meses, A=0, pi_cl=None, costo=None, moneda="CLP", tc0=None, pi_ext=None, v_tc=None):
    t = D(meses) / 12
    i = (1 + D(r)) ** (D(1) / 12) - 1
    f = (1 + i) ** meses
    vf = D(C) * f + (D(A) * meses if i == 0 else D(A) * (f - 1) / i)
    out = {"VF": q(vf), "aportes": D(A) * meses, "interes": q(vf) - C - D(A) * meses}
    if pi_cl is not None: out["poder_compra_hoy"] = q(vf / (1 + D(pi_cl)) ** t)
    cf = None
    if costo is not None:
        if moneda == "CLP":
            out["costo_hoy_clp"] = D(costo)
            if pi_cl is not None: cf = D(costo) * (1 + D(pi_cl)) ** t
        elif tc0 is not None:
            hoy = D(costo) * D(tc0); out["costo_hoy_clp"] = q(hoy)
            if pi_ext is not None and v_tc is not None:
                con_infl = D(costo) * (1 + D(pi_ext)) ** t * D(tc0)
                cf = con_infl * (1 + D(v_tc)) ** t
                out["efecto_inflacion_meta"] = q(con_infl) - q(hoy)
                out["efecto_tipo_cambio"] = q(cf) - q(con_infl)
        else:
            out["brecha"] = "no_calculable_sin_tipo_de_cambio"
        if "costo_hoy_clp" in out: out["brecha_hoy"] = D(C) - out["costo_hoy_clp"]
    if cf is not None:
        out["costo_futuro_clp"] = q(cf)
        out["brecha_futura"] = out["VF"] - q(cf)
        falta = cf - D(C) * f
        req = falta / meses if i == 0 else falta * i / (f - 1)
        out["aporte_equivalente"] = max(D(0), req).quantize(D(1), rounding=ROUND_CEILING)
    return out


print("\n== Simulaciones")
def show(n, o): print(n, {k: (str(v) if isinstance(v, D) else v) for k, v in o.items()})
a16 = simular(1_000_000, "0.05", 12); show("A16", a16); ok &= a16["VF"] == 1_050_000
show("A39 Emiliana r0 pi3 M7=12M CLP A=0", simular(10_000_000, "0", 36, 0, "0.03", 12_000_000))
show("A45 r4 pi3 A=100.000", simular(10_000_000, "0.04", 36, 100_000, "0.03", 12_000_000))
show("A46 Europa EUR 9.000, TC0 1.000, pi_ext 2%, vtc 4%, r0, A0", simular(10_000_000, "0", 36, 0, None, 9_000, "EUR", 1_000, "0.02", "0.04"))
show("A47 EUR sin TC", simular(10_000_000, "0", 36, 0, None, 9_000, "EUR"))
show("A47b EUR con TC sin pi_M ni v", simular(10_000_000, "0", 36, 0, None, 9_000, "EUR", 1_000))
show("A49 escenario 1 r=0 pi=2", simular(10_000_000, "0", 36, 0, "0.02", 12_000_000))
show("A49 escenario 2 r=3 pi=3", simular(10_000_000, "0.03", 36, 0, "0.03", 12_000_000))
show("A49 escenario 3 r=-5 pi=4", simular(10_000_000, "-0.05", 36, 0, "0.04", 12_000_000))
print("\nRESULTADO:", "TODO OK" if ok else "HAY ERRORES")
import sys; sys.exit(0 if ok else 1)
