"""Indicadores del panel histórico (§7.7 y Anexo D del SPEC) a partir de las fuentes.

Uso: python analisis/indicadores_historicos.py data/fuentes/valores_cuota_v2.csv data/fuentes/uf_fin_de_mes_v1.csv
No es el script de la app (scripts/procesar_historico.py, que implementa el agente en el hito 2):
es el análisis que produjo los valores de referencia del SPEC.
"""
import sys, json, pandas as pd, numpy as np
f_vc, f_uf = sys.argv[1], sys.argv[2]
df = pd.read_csv(f_vc, sep=";", dtype={"FECHA_INF": str, "RUN_FM": str})
df["fecha"] = pd.to_datetime(df.FECHA_INF, format="%Y%m%d")
assert not df.isna().any().any() and not df.duplicated(["fecha", "RUN_FM", "SERIE"]).any() and (df.VALOR_CUOTA > 0).all()
meta = df.drop_duplicates("RUN_FM").set_index("RUN_FM")
assert (df.groupby("RUN_FM")[["ADMINISTRADORA", "PERFIL", "SERIE"]].nunique() == 1).all().all()
p = df.pivot(index="fecha", columns="RUN_FM", values="VALOR_CUOTA").sort_index()
saltos = p.index.to_series().diff().dt.days
vacios = saltos[saltos > 3]
print("vacíos:", vacios.to_dict())
r = p.pct_change(fill_method=None)
assert (r.iloc[1:].abs() <= 0.20).all().all() or len(vacios)
uf = pd.read_csv(f_uf, sep=";", index_col=0).uf; uf.index = pd.PeriodIndex(uf.index, freq="M")
fm = p.groupby(p.index.to_period("M")).last()
base = pd.DataFrame([p.iloc[0].values], columns=p.columns, index=pd.PeriodIndex(["2019-10"], freq="M"))
nom = pd.concat([base, fm]); assert uf.reindex(nom.index).notna().all()
real = nom.div(uf.reindex(nom.index), axis=0)
perf = meta.PERFIL
filas = {}; extra = {}
for c in p.columns:
    d = p[c]; dd = d / d.cummax() - 1
    m = nom[c].pct_change(fill_method=None).dropna()
    row = {"totn": nom[c].iloc[-1] / nom[c].iloc[0] - 1, "totr": real[c].iloc[-1] / real[c].iloc[0] - 1,
           "vol": m.std() * np.sqrt(12), "mdd": dd.min()}
    for k in (12, 36):
        for lab, s in (("n", nom[c]), ("r", real[c])):
            w = (s / s.shift(k) - 1).dropna()
            row[f"peor{k}{lab}"] = w.min(); row[f"neg{k}{lab}"] = int((w < 0).sum()); row[f"cnt{k}"] = len(w)
            extra[(c, k, lab)] = w
    filas[c] = row
t = pd.DataFrame(filas).T; t["perfil"] = perf
orden = ["CONSERVADOR", "MODERADO", "AGRESIVO"]
anos = (p.index[-1] - p.index[0]).days / 365.25
uftot = uf["2026-10"] / uf["2019-10"] - 1
print(f"años {anos:.3f} | UF total {uftot*100:.2f} % | anual {((1+uftot)**(1/anos)-1)*100:.2f} %")
print("ventanas 12:", int(t.cnt12.iloc[0]), "| 36:", int(t.cnt36.iloc[0]))
def fmt(col, pct=True):
    g = t.groupby("perfil")[col].agg(["min", "median", "max"]).loc[orden].astype(float)
    if pct: g = (g * 100).round(1)
    return " | ".join(f"{k}: {g.loc[k,'min']} · {g.loc[k,'median']} · {g.loc[k,'max']}" for k in orden)
for col in ["totn", "totr", "vol", "mdd", "peor12n", "peor12r", "peor36n", "peor36r"]:
    print(f"{col:8}", fmt(col))
for col in ["neg12n", "neg12r", "neg36n", "neg36r"]:
    print(f"{col:8}", fmt(col, pct=False))
print("\nreal anual:", fmt("totr").replace("·", "·"))
ra = ((1 + t.totr.astype(float)) ** (1 / anos) - 1)
print("real anual por perfil:", (ra.groupby(t.perfil).agg(["min", "median", "max"]) * 100).round(1).loc[orden].to_dict("index"))
# Índices de fin de año
fechas = [pd.Period(x, "M") for x in ["2019-10", "2020-12", "2021-12", "2022-12", "2023-12", "2024-12", "2025-12", "2026-10"]]
for lab, s in (("nominal", nom), ("real", real)):
    idx = (s / s.iloc[0] * 100)
    med = idx.T.groupby(perf).median().T[orden]
    print("\n", lab); print(med.loc[fechas].round(1).to_string())
    if lab == "real":
        c = med["CONSERVADOR"]; print("mín. conservador real:", round(c.min(), 1), c.idxmin())
        post = c.loc["2023-01":]; print("primer mes ≥100 tras 2022:", post[post >= 100].index[0])
# meses de término de ventanas
for cat in orden:
    cols = perf[perf == cat].index
    w36r = pd.concat([extra[(c, 36, "r")] for c in cols]); neg = w36r[w36r < 0]
    w12n = pd.concat([extra[(c, 12, "n")] for c in cols])
    print(cat, "36m real negativas terminan:", neg.index.min(), "→", neg.index.max(), "| peor 12m nominal termina:", w12n.idxmin())
# caída máxima por categoría y fecha
for c in p.columns:
    d = p[c]; dd = d / d.cummax() - 1
    print(c, perf[c], "mdd", round(dd.min()*100, 2), dd.idxmin().date())
# drawdown en el tramo nuevo
print("\nmdd dentro de abr–ago 2026:")
for c in p.columns:
    d = p[c]; dd = (d / d.cummax() - 1).loc["2026-04-01":"2026-08-31"]
    print(c, perf[c], round(dd.min()*100, 2))
