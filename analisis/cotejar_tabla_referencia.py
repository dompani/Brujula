"""Compara la tabla de referencia de §7.7 del SPEC con los valores recalculados desde las fuentes.

Uso: python analisis/cotejar_tabla_referencia.py SPEC.md   (desde la raíz del repositorio)
Termina con código 1 si alguna cifra difiere en más de 0,05 puntos.
"""
import sys, re, subprocess, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = open(sys.argv[1], encoding="utf-8").read()
sec = spec.split("**Valores de referencia**")[1].split("**Reglas de presentación**")[0]
filas = [l for l in sec.splitlines() if l.startswith("| ") and not l.startswith("| Indicador") and not l.startswith("|---")]
doc = {}
for l in filas:
    c = [x.strip() for x in l.strip("|").split("|")]
    nums = [[float(v.replace("−", "-").replace("+", "").replace(",", ".")) for v in re.findall(r"[−+]?\d+(?:,\d+)?", x)] for x in c[1:]]
    doc[c[0]] = nums
out = subprocess.run([sys.executable, "-I", os.path.join(RAIZ, "analisis", "indicadores_historicos.py"), os.path.join(RAIZ, "data", "fuentes", "valores_cuota_v2.csv"), os.path.join(RAIZ, "data", "fuentes", "uf_fin_de_mes_v1.csv")], capture_output=True, text=True).stdout
calc = {}
for l in out.splitlines():
    m = re.match(r"^(\w+)\s+CONSERVADOR: (.*) \| MODERADO: (.*) \| AGRESIVO: (.*)$", l)
    if m: calc[m.group(1)] = [[float(x) for x in g.split(" · ")] for g in m.groups()[1:]]
mapa = {"Variación total en pesos corrientes": "totn", "Variación total en pesos de hoy (UF: +46,97 %)": "totr",
        "Volatilidad anualizada": "vol", "Caída máxima desde un máximo previo": "mdd",
        "Peor ventana de 12 meses, pesos corrientes": "peor12n", "Peor ventana de 12 meses, pesos de hoy": "peor12r",
        "Ventanas de 12 meses negativas, pesos corrientes (de 73)": "neg12n", "Ventanas de 12 meses negativas, pesos de hoy (de 73)": "neg12r",
        "Peor ventana de 36 meses, pesos corrientes": "peor36n", "Peor ventana de 36 meses, pesos de hoy": "peor36r",
        "Ventanas de 36 meses negativas, pesos corrientes (de 49)": "neg36n", "Ventanas de 36 meses negativas, pesos de hoy (de 49)": "neg36r"}
ok = True
for fila, clave in mapa.items():
    d = doc.get(fila); c = calc[clave]
    if d is None: print("FALTA fila:", fila); ok = False; continue
    iguales = all(abs(a - b) < 0.051 for x, y in zip(d, c) for a, b in zip(x, y))
    ok &= iguales
    print(("OK " if iguales else "DIF"), fila, "| SPEC:", d, "| calculado v2:", c if not iguales else "")
print("\nRESULTADO:", "la tabla del SPEC coincide con las fuentes" if ok else "HAY DIFERENCIAS")
sys.exit(0 if ok else 1)
