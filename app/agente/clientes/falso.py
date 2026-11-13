"""Cliente falso para pruebas y CI: nunca usa la red. Devuelve borradores predefinidos en orden."""
import json


class ClienteFalso:
    def __init__(self, respuestas: list | None = None, fallar: bool = False):
        self.respuestas = list(respuestas or [])
        self.fallar = fallar
        self.llamadas = []

    def completar(self, system: str, mensajes: list[dict], max_tokens: int, plazo_total_s: float = 30.0) -> dict:
        from .anthropic_real import ErrorProveedor
        self.llamadas.append(mensajes)
        if self.fallar:
            raise ErrorProveedor("proveedor_no_disponible")
        r = self.respuestas.pop(0) if self.respuestas else None
        texto = r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)
        return {"texto": texto, "tokens_in": 3000, "tokens_out": 400}


def borrador_valido(ids: list[str]) -> dict:
    return {"tipo": "personalizada",
            "summary": "Las tres alternativas simuladas difieren en cuánto tardan en devolver el dinero, en si "
                       "preservan capital y en su comisión simulada.",
            "explicaciones": [{"id": i, "texto": f"{i} es compatible con tu perfil y tu meta; revisa en la tabla su "
                                                 "plazo de retiro y su comisión simulada."} for i in ids],
            "limitations": ["Datos simulados; no incluye impuestos ni spreads."],
            "next_step": "ver_comparacion"}
