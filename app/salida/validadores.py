"""Control de salida de la explicación de la comparación: V-01 a V-05 y V-07 (§9.3).

Mismas reglas que la herramienta del golden set (tools/golden_set/src/comparacion_1_7/logica.js), para que la
app valide como se validó la versión 1.7 del prompt.
"""
import json
import re
import unicodedata
from pathlib import Path

DIR = Path(__file__).parent
NEXT_STEPS = ["responder_cuestionario", "actualizar_perfil", "confirmar_meta", "actualizar_meta", "ver_comparacion",
              "simular", "ver_metodologia", "consultar_profesional", "reintentar", "ninguno"]
NEXT_EXPLICACION = ["ver_comparacion", "simular", "ninguno"]
CAMPOS = ["tipo", "summary", "explicaciones", "limitations", "next_step"]
LIMITE_EXPLICACION = 300


def _lista(nombre):
    return [l.strip() for l in (DIR / nombre).read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


FRASES_PROHIBIDAS = _lista("frases_prohibidas_v1.txt")
MARCAS = _lista("marcas_v1.txt")
RANKING = _lista("ranking_v1.txt")
NUM_PALABRA = ("(cero|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|dieciseis|"
               "diecisiete|dieciocho|diecinueve|veinte|veinti[a-z]+|treinta|cuarenta|cincuenta|sesenta|setenta|"
               "ochenta|noventa|cien|ciento|doscientos|trescientos|quinientos|mil|millon|millones)")
UNIDAD = "(dias?|semanas?|mes|meses|anos?|por ciento|pesos|uf|dolares|euros|puntos?)"
RE_CIFRA_PALABRA = re.compile(r"(^|[^a-z])" + NUM_PALABRA + r"(\s+y\s+[a-z]+)?\s+(de\s+)?" + UNIDAD + r"([^a-z]|$)")
RE_HTML = re.compile(r"<\s*/?\s*[a-z!][^>]*>", re.I)


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def _contiene(texto_norm: str, frase: str) -> bool:
    return re.search(r"(^|[^a-z0-9])" + re.escape(frase) + r"([^a-z0-9]|$)", texto_norm) is not None


def textos(b) -> list[str]:
    out = []
    if isinstance(b, dict):
        if isinstance(b.get("summary"), str):
            out.append(b["summary"])
        for e in b.get("explicaciones") or []:
            if isinstance(e, dict) and isinstance(e.get("texto"), str):
                out.append(e["texto"])
        for l in b.get("limitations") or []:
            if isinstance(l, str):
                out.append(l)
    return out


def _extraer_json(texto: str):
    t = (texto or "").strip()
    return json.loads(t)


def validar_explicacion(texto: str, ids: list[str]) -> dict:
    """Devuelve {ok, fallos: [{v, motivo}], borrador}. La primera falla es la que detiene la cadena."""
    fallos, b = [], None
    t = (texto or "").strip()
    if "```" in t:
        fallos.append({"v": "V-01", "motivo": "trae un bloque de código Markdown"})
    try:
        b = _extraer_json(t)
    except (ValueError, TypeError):
        fallos.append({"v": "V-01", "motivo": "no es JSON válido o trae texto fuera del JSON"})
    if b is not None and not isinstance(b, dict):
        fallos.append({"v": "V-01", "motivo": "el JSON no es un objeto"})
        b = None
    if b:
        extra = [k for k in b if k not in CAMPOS]
        if extra:
            fallos.append({"v": "V-01", "motivo": "campos no permitidos: " + ", ".join(extra)})
        faltan = [k for k in CAMPOS if k not in b]
        if faltan:
            fallos.append({"v": "V-01", "motivo": "faltan campos: " + ", ".join(faltan)})
        if b.get("tipo") not in ("educativa", "personalizada"):
            fallos.append({"v": "V-01", "motivo": "tipo fuera del esquema"})
        s = b.get("summary")
        if not isinstance(s, str) or not 1 <= len(s) <= 600:
            fallos.append({"v": "V-01", "motivo": "summary vacío o de más de 600 caracteres"})
        ex = b.get("explicaciones")
        if not isinstance(ex, list):
            fallos.append({"v": "V-01", "motivo": "explicaciones no es una lista"})
        else:
            for i, e in enumerate(ex):
                if not isinstance(e, dict):
                    fallos.append({"v": "V-01", "motivo": f"explicación {i + 1} no es un objeto"})
                    continue
                if [k for k in e if k not in ("id", "texto")]:
                    fallos.append({"v": "V-01", "motivo": "campos no permitidos en una explicación"})
                if not isinstance(e.get("id"), str):
                    fallos.append({"v": "V-01", "motivo": "explicación sin id"})
                tx = e.get("texto")
                if not isinstance(tx, str) or not 1 <= len(tx) <= LIMITE_EXPLICACION:
                    fallos.append({"v": "V-01", "motivo": f"la explicación de {e.get('id')} tiene "
                                   f"{len(tx) if isinstance(tx, str) else 0} caracteres (máximo {LIMITE_EXPLICACION})"})
        lim = b.get("limitations")
        if not isinstance(lim, list) or len(lim) > 5:
            fallos.append({"v": "V-01", "motivo": "limitations no es una lista de hasta 5 elementos"})
        elif any(not isinstance(l, str) or not 1 <= len(l) <= 200 for l in lim):
            fallos.append({"v": "V-01", "motivo": "una limitación está vacía o supera 200 caracteres"})
        if b.get("next_step") not in NEXT_STEPS:
            fallos.append({"v": "V-01", "motivo": "next_step fuera del esquema"})
        if any(RE_HTML.search(x) for x in textos(b)):
            fallos.append({"v": "V-01", "motivo": "contiene etiquetas HTML"})
    if b:
        todo = textos(b)
        encontrados = {m.upper() for x in todo for m in re.findall(r"\bD\d{2}\b", x, re.I)}
        for e in b.get("explicaciones") or []:
            if isinstance(e, dict) and isinstance(e.get("id"), str):
                encontrados.add(e["id"].upper())
        ajenos = sorted(x for x in encontrados if x not in ids)
        if ajenos:
            fallos.append({"v": "V-02", "motivo": "menciona IDs fuera de la comparación: " + ", ".join(ajenos)})
        sin_ids = [re.sub(r"\b[A-Z][A-Z_]*_V\d+\b", "", re.sub(r"\bW[1-5]\b", "", re.sub(r"\bD\d{2}\b", "", x, flags=re.I)))
                   for x in todo]
        if any(re.search(r"\d", x) for x in sin_ids):
            fallos.append({"v": "V-03", "motivo": "escribe cifras"})
        if any(RE_CIFRA_PALABRA.search(normalizar(x)) for x in sin_ids):
            fallos.append({"v": "V-03", "motivo": "escribe una cifra en palabras"})
        norm = " \n ".join(normalizar(x) for x in todo)
        for f in FRASES_PROHIBIDAS:
            if f in norm:
                fallos.append({"v": "V-04", "motivo": f'frase prohibida "{f}"'})
        if any(_contiene(norm, m) for m in MARCAS):
            fallos.append({"v": "V-04", "motivo": "nombra una marca real"})
        ns = b.get("next_step")
        if ns in NEXT_STEPS and ns not in NEXT_EXPLICACION:
            fallos.append({"v": "V-07", "motivo": f'next_step "{ns}" no está permitido en la explicación de una '
                           "comparación (solo ver_comparacion, simular o ninguno)"})
        if b.get("tipo") != "personalizada":
            fallos.append({"v": "V-07", "motivo": "tipo debe ser personalizada"})
        if isinstance(b.get("explicaciones"), list):
            lista = [e["id"].upper() if isinstance(e, dict) and isinstance(e.get("id"), str) else "?"
                     for e in b["explicaciones"]]
            if not (len(lista) == 3 and all(lista.count(x) == 1 for x in ids)):
                fallos.append({"v": "V-07", "motivo": "explicaciones debe traer exactamente " + ", ".join(ids) +
                               ", una vez cada uno"})
        for r in RANKING:
            if _contiene(norm, r):
                fallos.append({"v": "V-07", "motivo": f'presenta un orden o una preferencia ("{r}")'})
    orden = {"V-01": 1, "V-02": 2, "V-03": 3, "V-04": 4, "V-05": 5, "V-07": 7}
    fallos.sort(key=lambda f: orden[f["v"]])
    return {"ok": not fallos, "fallos": fallos, "borrador": b}
