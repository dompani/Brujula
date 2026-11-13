"""Cotejo de la base de valores cuota con la cartola diaria de la CMF (Anexo D.8).

Uso: python analisis/cotejo_cmf.py data/fuentes/valores_cuota_v2.csv data/fuentes/cmf_cotejo/ffmm_todos_20191101_20191101.txt 20191101
"""
import sys, pandas as pd
k = pd.read_csv(sys.argv[1], sep=";", dtype={"FECHA_INF": str, "RUN_FM": str})
c = pd.read_csv(sys.argv[2], sep=";", dtype=str, encoding="latin1", index_col=False)
c["VALOR_CUOTA"] = c["VALOR_CUOTA"].astype(float)
fecha = sys.argv[3]
kk = k[k.FECHA_INF == fecha][["RUN_FM", "SERIE", "VALOR_CUOTA", "ADMINISTRADORA", "PERFIL"]]
cc = c[c.FECHA_INF == fecha][["RUN_FM", "SERIE", "VALOR_CUOTA", "MONEDA"]].rename(columns={"VALOR_CUOTA": "VC_CMF"})
m = kk.merge(cc, on=["RUN_FM", "SERIE"], how="left")
m["dif"] = (m.VALOR_CUOTA - m.VC_CMF).round(4)
m["coincide_2dec"] = (m.VC_CMF.round(2) - m.VALOR_CUOTA).abs() < 0.0051
print(m.sort_values(["ADMINISTRADORA", "PERFIL"]).to_string(index=False))
print("\nCoinciden:", int(m.coincide_2dec.sum()), "de", len(m))
