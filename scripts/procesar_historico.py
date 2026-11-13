"""Genera data/historico_categorias_v1.json a partir de las fuentes (§7.7). Se ejecuta fuera de línea, nunca durante
el uso de la app. Sin nombres de administradoras, fondos ni RUN en la salida.

Uso: python scripts/procesar_historico.py   (desde la raíz del repositorio; requiere pandas)
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
F_VC = RAIZ / "data" / "fuentes" / "valores_cuota_v2.csv"
F_UF = RAIZ / "data" / "fuentes" / "uf_fin_de_mes_v1.csv"
SALIDA = RAIZ / "data" / "historico_categorias_v1.json"


def falla(msg):
    sys.exit(f"ERROR: {msg}")


df = pd.read_csv(F_VC, sep=";", dtype={"FECHA_INF": str, "RUN_FM": str})
for col in ("FECHA_INF", "ADMINISTRADORA", "PERFIL", "RUN_FM", "SERIE", "NOMBRE", "VALOR_CUOTA"):
    if col not in df.columns:
        falla(f"falta la columna {col}")
df["fecha"] = pd.to_datetime(df.FECHA_INF, format="%Y%m%d")
if df.isna().any().any():
    falla("hay nulos")
if df.duplicated(["fecha", "RUN_FM"]).any():
    falla("hay duplicados de fecha y RUN")
if (df.VALOR_CUOTA <= 0).any():
    falla("hay valores <= 0")
if not (df.groupby("RUN_FM")[["ADMINISTRADORA", "PERFIL", "SERIE"]].nunique() == 1).all().all():
    falla("un RUN tiene más de una administradora, perfil o serie")
perfil = df.drop_duplicates("RUN_FM").set_index("RUN_FM").PERFIL
p = df.pivot(index="fecha", columns="RUN_FM", values="VALOR_CUOTA").sort_index()
saltos = p.index.to_series().diff().dt.days
vacios = [str(d.date()) for d in saltos[saltos > 3].index]
if vacios:
    falla("la versión de la base trae vacíos; este script no los soporta aún")
r = p.pct_change(fill_method=None).iloc[1:]
if (r.abs() > 0.20).any().any():
    falla("variación diaria fuera de ±20 %")
uf = pd.read_csv(F_UF, sep=";", index_col=0).uf
uf.index = pd.PeriodIndex(uf.index, freq="M")
fm = p.groupby(p.index.to_period("M")).last()
base = pd.DataFrame([p.iloc[0].values], columns=p.columns, index=pd.PeriodIndex(["2019-10"], freq="M"))
nom = pd.concat([base, fm])
if uf.reindex(nom.index).isna().any():
    falla("hay un mes sin UF")
real = nom.div(uf.reindex(nom.index), axis=0)

filas = {}
for c in p.columns:
    d = p[c]
    m = nom[c].pct_change(fill_method=None).dropna()
    fila = {"variacion_total_corrientes": nom[c].iloc[-1] / nom[c].iloc[0] - 1,
            "variacion_total_hoy": real[c].iloc[-1] / real[c].iloc[0] - 1,
            "volatilidad_anual": m.std() * np.sqrt(12), "caida_maxima": (d / d.cummax() - 1).min()}
    for k in (12, 36):
        for lab, s in (("corrientes", nom[c]), ("hoy", real[c])):
            w = (s / s.shift(k) - 1).dropna()
            fila[f"peor_{k}m_{lab}"] = w.min()
            fila[f"negativas_{k}m_{lab}"] = int((w < 0).sum())
            fila[f"n_ventanas_{k}m"] = len(w)
    filas[c] = fila
t = pd.DataFrame(filas).T
t["perfil"] = perfil
CATS = {"CONSERVADOR": "conservador", "MODERADO": "moderado", "AGRESIVO": "agresivo"}
categorias = {}
for cat, clave in CATS.items():
    g = t[t.perfil == cat].drop(columns="perfil").astype(float)
    met = {}
    for col in g.columns:
        if col.startswith("n_ventanas"):
            continue
        es_conteo = col.startswith("negativas")
        v = g[col]
        met[col] = {k: (int(x) if es_conteo else round(float(x) * 100, 1))
                    for k, x in (("min", v.min()), ("mediana", v.median()), ("max", v.max()))}
    categorias[clave] = {"n_fondos": int(len(g)), "metricas": met}
fechas = ["2019-10", "2020-12", "2021-12", "2022-12", "2023-12", "2024-12", "2025-12", "2026-10"]
indice = {}
for lab, s in (("corrientes", nom), ("hoy", real)):
    idx = (s / s.iloc[0] * 100)
    med = idx.T.groupby(perfil).median().T
    indice[lab] = {CATS[c]: {f: round(float(med.loc[pd.Period(f, "M"), c]), 1) for f in fechas} for c in CATS}


def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()


salida = {
    "historical_id": "HISTORICO_CATEGORIAS_V1",
    "generated_at": "2026-11-13",
    "fuentes": [
        {"archivo": "data/fuentes/valores_cuota_v2.csv", "sha256": sha(F_VC),
         "procedencia": "Comisión para el Mercado Financiero (CMF), cartola diaria de fondos mutuos; base preparada "
                        "por el Grupo 2 y cotejada con la CMF (27 de 27 valores coinciden)",
         "fecha_consulta": "2026-11-07"},
        {"archivo": "data/fuentes/uf_fin_de_mes_v1.csv", "sha256": sha(F_UF),
         "procedencia": "Servicio de Impuestos Internos (SII), tablas anuales de la UF", "fecha_consulta": "2026-11-06"},
    ],
    "periodo": {"desde": "2019-11-01", "hasta": "2026-10-31"},
    "vacios": vacios,
    "ventanas": {"12": int(t.n_ventanas_12m.iloc[0]), "36": int(t.n_ventanas_36m.iloc[0])},
    "categorias": categorias,
    "indice_anual": indice,
    "notas": [
        "Datos históricos de 9 fondos mutuos reales de 3 administradoras chilenas, del 01-11-2019 al 31-10-2026.",
        "Incluye la pandemia de 2020 y el alza de inflación de 2021 a 2023. Las ventanas se superponen: no son probabilidades.",
        "Lo que pasó no indica lo que pasará.",
        "El valor cuota ya descuenta la remuneración del fondo; no incluye impuestos ni beneficios tributarios. Dos "
        "administradoras usan series APV y una, series B y B1, por lo que las cifras no comparan administradoras.",
        "Este panel no describe las alternativas simuladas de la comparación.",
        "Fuente de los valores cuota: Comisión para el Mercado Financiero (CMF), cartola diaria de fondos mutuos. "
        "Fuente de la UF: Servicio de Impuestos Internos.",
    ],
}
texto = json.dumps(salida, ensure_ascii=False, indent=1)
for prohibido in df.ADMINISTRADORA.unique().tolist() + df.RUN_FM.unique().tolist():
    if str(prohibido).lower() in texto.lower():
        falla(f"la salida contiene un nombre o RUN: {prohibido}")
SALIDA.write_text(texto + "\n", encoding="utf-8")
print("ok", SALIDA.relative_to(RAIZ))
