"""Carga y verificación del catálogo ficticio (§7.2)."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RUTA = RAIZ / "data" / "catalogo_demo_v3.json"


@lru_cache
def cargar() -> dict:
    datos = RUTA.read_bytes()
    cat = json.loads(datos)
    for a in cat["alternativas"]:
        assert a["simulated"] is True and a["source_id"] == cat["source_id"] and a["return_pct"] is None
    return {"source_id": cat["source_id"], "checksum_sha256": hashlib.sha256(datos).hexdigest(),
            "alternativas": cat["alternativas"]}


def alternativas() -> list[dict]:
    return cargar()["alternativas"]


def por_id() -> dict:
    return {a["id"]: a for a in alternativas()}
