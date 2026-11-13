"""Cliente real del proveedor (Anthropic, Messages API). Solo se instancia con LLM_MODE=real y clave."""
import time

import httpx

URL = "https://api.anthropic.com/v1/messages"
TRANSITORIOS = {408, 409, 429, 500, 502, 503, 504, 529}


class ErrorProveedor(Exception):
    def __init__(self, codigo, tokens_in=None, tokens_out=None):
        super().__init__(codigo)
        self.codigo, self.tokens_in, self.tokens_out = codigo, tokens_in, tokens_out


class ClienteAnthropic:
    def __init__(self, api_key: str, model: str, timeout_s: float = 20.0, thinking: str = "", effort: str = ""):
        self.api_key, self.model, self.timeout_s = api_key, model, timeout_s
        self.thinking, self.effort = thinking, effort
        self.ultimo_mensaje = ""

    def completar(self, system: str, mensajes: list[dict], max_tokens: int, plazo_total_s: float = 30.0) -> dict:
        """Devuelve {texto, tokens_in, tokens_out}. Como máximo un reintento por fallo transitorio."""
        inicio = time.monotonic()
        cuerpo = {"model": self.model, "max_tokens": max_tokens, "system": system, "messages": mensajes}
        # Sonnet 5.5 razona por defecto y ese razonamiento consume max_tokens y tiempo. Sin herramientas,
        # "between_tools" deja solo texto (decisión 0013). Configurable para otros modelos.
        if self.thinking:
            cuerpo["thinking"] = {"type": self.thinking}
        if self.effort:
            cuerpo["output_config"] = {"effort": self.effort}
        cab = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        ultimo = "proveedor_no_disponible"
        for intento in range(2):
            restante = plazo_total_s - (time.monotonic() - inicio)
            if restante <= 1:
                break
            try:
                r = httpx.post(URL, json=cuerpo, headers=cab, timeout=min(self.timeout_s, restante))
            except httpx.HTTPError as ex:
                ultimo = f"proveedor_no_disponible:{type(ex).__name__}"
            else:
                if r.status_code == 200:
                    d = r.json()
                    texto = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
                    u = d.get("usage") or {}
                    return {"texto": texto, "tokens_in": u.get("input_tokens"), "tokens_out": u.get("output_tokens"),
                            "stop_reason": d.get("stop_reason")}
                try:
                    e = r.json().get("error") or {}
                except ValueError:
                    e = {}
                ultimo = f"proveedor_http_{r.status_code}:{e.get('type', '')}"
                self.ultimo_mensaje = str(e.get("message", ""))[:200]
                if r.status_code not in TRANSITORIOS:
                    break
            if intento == 0:
                time.sleep(1.0)
        raise ErrorProveedor(ultimo)
