"""Explicación generativa de la comparación (RF-21, §6.3 pasos 1 a 7) con límite de gasto y control de salida."""
import json
import logging
import time
from pathlib import Path

from ..dominio import catalogo, politica as P
from ..salida import plantillas
from ..salida.validadores import LIMITE_EXPLICACION, NEXT_STEPS, validar_explicacion
from . import presupuesto
from .clientes.anthropic_real import ClienteAnthropic, ErrorProveedor
from .contexto import construir

RAIZ = Path(__file__).resolve().parents[2]
SYSTEM = (RAIZ / "prompts" / "system_brujula_v1_7.txt").read_text(encoding="utf-8")
MAX_TOKENS = 1500
LOG = logging.getLogger("brujula.explicacion")
ESQUEMA = {"tipo": "educativa | personalizada", "summary": "1 a 600 caracteres",
           "explicaciones": [{"id": "Dxx", "texto": f"1 a {LIMITE_EXPLICACION} caracteres"}],
           "limitations": ["1 a 200 caracteres; máximo 5 elementos"], "next_step": " | ".join(NEXT_STEPS)}


def mensaje_servidor(contexto: dict) -> str:
    return ("TAREA_SERVIDOR=explicar_comparacion\n\nESQUEMA BORRADOR_AGENTE:\n" + json.dumps(ESQUEMA, ensure_ascii=False)
            + "\n\nCONTEXTO_SERVIDOR:\n" + json.dumps(contexto, ensure_ascii=False, default=str))


def mensaje_reparacion(fallo: dict) -> str:
    return (f"El servidor rechazó tu borrador. {fallo['v']}: {fallo['motivo']}. Corrige solo eso, respeta todas las "
            "instrucciones del sistema y responde de nuevo solo con el objeto JSON BORRADOR_AGENTE (explicaciones de "
            f"máximo {LIMITE_EXPLICACION} caracteres), sin texto fuera del JSON.")


def _plantilla(ids, motivo, detalle=""):
    LOG.warning("explicacion_plantilla motivo=%s %s", motivo, detalle)
    porid = catalogo.por_id()
    t = plantillas.explicacion_sin_ia([porid[i] for i in ids])
    rotulo = P.ROTULO_PAUSA if motivo == "presupuesto_agotado" else P.ROTULO_SIN_IA
    return {**t, "rotulo": rotulo, "generated_by": "plantilla", "motivo": motivo, "model_id": None,
            "prompt_version": P.PROMPT_VERSION}


def explicar(eng, cfg, perfil_row, goal_row, comp_row, cliente=None, auditar=None) -> dict:
    ids = comp_row["payload"]["selected_ids"]
    if cliente is None:
        if not cfg.llm_real:
            return _plantilla(ids, "modo_demo", f"LLM_MODE={cfg.llm_mode} clave_presente={bool(cfg.llm_api_key)}")
        cliente = ClienteAnthropic(cfg.llm_api_key, cfg.llm_model, thinking=getattr(cfg, "llm_thinking", ""),
                                   effort=getattr(cfg, "llm_effort", ""))
    if cfg.kill_switch:
        return _plantilla(ids, "interruptor")
    contexto = construir(perfil_row, goal_row, comp_row)
    mensajes = [{"role": "user", "content": mensaje_servidor(contexto)}]
    inicio = time.monotonic()
    fallos = []
    for intento in range(2):  # borrador y, como máximo, una reparación
        est_in = (len(SYSTEM) + sum(len(m["content"]) for m in mensajes)) // 3
        reserva = presupuesto.reservar(eng, cfg, "explicacion", cfg.llm_model, P.PROMPT_VERSION, est_in, MAX_TOKENS)
        if reserva is None:
            return _plantilla(ids, "presupuesto_agotado")
        try:
            r = cliente.completar(SYSTEM, mensajes, MAX_TOKENS, plazo_total_s=max(5.0, 30.0 - (time.monotonic() - inicio)))
        except ErrorProveedor as e:
            presupuesto.liquidar(eng, cfg, reserva, e.tokens_in, e.tokens_out)
            if auditar:
                auditar("explicacion", "error", e.codigo, None, None)
            return _plantilla(ids, "proveedor_no_disponible",
                              f"codigo={e.codigo} mensaje={getattr(cliente, 'ultimo_mensaje', '')}")
        presupuesto.liquidar(eng, cfg, reserva, r["tokens_in"], r["tokens_out"])
        v = validar_explicacion(r["texto"], ids)
        if auditar:
            auditar("explicacion", "ok" if v["ok"] else "borrador_invalido",
                    None if v["ok"] else v["fallos"][0]["v"], r["tokens_in"], r["tokens_out"])
        if v["ok"]:
            b = v["borrador"]
            orden = {e["id"].upper(): e["texto"] for e in b["explicaciones"]}
            return {"summary": b["summary"], "explicaciones": [{"id": i, "texto": orden[i]} for i in ids],
                    "limitations": b["limitations"], "rotulo": P.ROTULO_IA, "generated_by": "llm", "motivo": None,
                    "model_id": cfg.llm_model, "prompt_version": P.PROMPT_VERSION}
        fallos.append(f"{v['fallos'][0]['v']}: {v['fallos'][0]['motivo']} (stop={r.get('stop_reason')}, "
                      f"tokens_out={r.get('tokens_out')})")
        if intento == 0:
            mensajes = mensajes + [{"role": "assistant", "content": r["texto"].strip() or "(sin texto)"},
                                   {"role": "user", "content": mensaje_reparacion(v["fallos"][0])}]
    return _plantilla(ids, "borrador_invalido", "fallos=" + " | ".join(fallos))
