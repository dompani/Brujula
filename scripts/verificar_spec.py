"""Comprobaciones estructurales de SPEC.md.

Uso: python scripts/verificar_spec.py SPEC.md   (termina con código 1 si hay errores)
Revisa: 12 secciones numeradas; tablas con columnas consistentes; criterios de la suite vigente
definidos una vez en §11 y asignados a un hito; hitos coherentes; referencias a secciones existentes;
bloques de código balanceados.
"""
import re
import sys

ruta = sys.argv[1]
texto = open(ruta, encoding="utf-8").read()
lineas = texto.splitlines()
errores = []

# 1. Marcadores de continuación pendientes
if "CONTINUA_PARTE" in texto:
    errores.append("Quedó un marcador de continuación")

# 2. Doce secciones numeradas en orden
secciones = [int(m.group(1)) for m in re.finditer(r"^## (\d+)\. ", texto, re.M)]
if secciones != list(range(1, 13)):
    errores.append(f"Secciones numeradas: {secciones}")

# 3. Tablas con número de columnas consistente (fuera de bloques de código)
en_codigo = False
tabla = []
def revisar(tabla):
    if not tabla:
        return
    def cols(l):
        l = re.sub(r"`[^`]*`", "X", l)  # ignorar pipes dentro de código en línea
        return l.strip().strip("|").count("|") + 1
    n = cols(tabla[0][1])
    for num, l in tabla:
        if cols(l) != n:
            errores.append(f"Línea {num}: {cols(l)} columnas, se esperaban {n}")
for i, l in enumerate(lineas, 1):
    if l.startswith("```"):
        en_codigo = not en_codigo
        continue
    if not en_codigo and l.startswith("|"):
        tabla.append((i, l))
    else:
        revisar(tabla); tabla = []
revisar(tabla)

# 4. Criterios A01–A36 definidos exactamente una vez en la tabla de §11
definidos = re.findall(r"^\| (A\d{2}) \| ", texto, re.M)
seccion11 = texto.split("## 11.")[1].split("## 12.")[0]
en11 = re.findall(r"^\| (A\d{2}) \| ", seccion11, re.M)
m_suite = re.search(r"Suite de aceptación vigente \| A01–A(\d{2})", texto)
if not m_suite:
    errores.append("No se encontró la suite vigente en el encabezado")
ultimo = int(m_suite.group(1)) if m_suite else 64
esperados = [f"A{i:02d}" for i in range(1, ultimo + 1)]
if en11 != esperados:
    errores.append(f"Criterios en §11: {en11}")

# 5. Cada criterio aparece asignado en la tabla de hitos
hitos = texto.split("### Plan de ejecución en seis hitos")[1].split("Los seis hitos")[0]
asignados = set()
for a, b in re.findall(r"A(\d{2})(?:–A(\d{2}))?", hitos):
    ini, fin = int(a), int(b or a)
    asignados.update(f"A{i:02d}" for i in range(ini, fin + 1))
faltan = sorted(set(esperados) - asignados)
if faltan:
    errores.append(f"Criterios sin hito: {faltan}")

# 6. Coherencia hito de cada criterio en §11 vs tabla de hitos
filas_hitos = re.findall(r"^\| (\d)\. [^|]+\|[^|]+\| ([^|]*) \|", hitos, re.M)
mapa = {}
for h, crits in filas_hitos:
    for a, b in re.findall(r"A(\d{2})(?:–A(\d{2}))?", crits):
        for i in range(int(a), int(b or a) + 1):
            mapa.setdefault(f"A{i:02d}", set()).add(h)
for fila in re.findall(r"^\| (A\d{2}) \| ([^|]+) \|", seccion11, re.M):
    a, h = fila
    hs = set(re.findall(r"\d", h))
    if not hs <= mapa.get(a, set()) and not mapa.get(a, set()) <= hs:
        errores.append(f"{a}: hito en §11 {hs} vs plan {mapa.get(a)}")

# 7. Referencias cruzadas a secciones existentes
subsec = set(re.findall(r"^#{2,3} (\d+(?:\.\d+)?)", texto, re.M))
for ref in set(re.findall(r"§(\d+(?:\.\d+)?)", texto)):
    if ref not in subsec:
        errores.append(f"Referencia a §{ref} inexistente")

# 8. Bloques de código balanceados y mermaid presentes
if texto.count("```") % 2:
    errores.append("Bloques de código desbalanceados")
print("Bloques mermaid:", texto.count("```mermaid"))
print("Líneas:", len(lineas), "| Palabras:", len(texto.split()))
print("ERRORES:" if errores else "SIN ERRORES", *errores, sep="\n  ")
sys.exit(1 if errores else 0)
