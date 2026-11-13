"""calcular_perfil: reglas R-01 a R-05 del SPEC (§3.2). Sin red ni base de datos."""
from datetime import datetime

from . import politica as P


class EntradaInvalida(ValueError):
    def __init__(self, fields):
        super().__init__("entrada_invalida")
        self.fields = fields


def _tolerancia(s: int) -> str:
    return "conservador" if s <= 2 else "moderado" if s <= 5 else "arriesgado"


def _disposicion(s: int) -> str:
    return "baja" if s <= 2 else "media" if s <= 5 else "alta"


def validar_bloque_a(a: dict) -> None:
    """R-01: todas las respuestas presentes y dentro de sus opciones."""
    malos = [k for k in ("t1", "t2", "t3", "t4") if a.get(k) not in P.OPCIONES_T]
    for k, ops in (("k1", P.OPCIONES_K1), ("k2", P.OPCIONES_K2), ("e1", P.OPCIONES_E1), ("f1", P.OPCIONES_F1)):
        if a.get(k) not in ops:
            malos.append(k)
    if malos:
        raise EntradaInvalida(malos)


def calcular_perfil(a: dict, ahora: datetime | None = None) -> dict:
    validar_bloque_a(a)
    s = a["t1"] + a["t2"] + a["t3"] + a["t4"]
    tolerancia = _tolerancia(s)
    base = {"score_s": s, "tolerance": tolerancia, "disposicion": _disposicion(s), "experiencia": a["e1"],
            "fondo_emergencia": a["f1"], "capacidad_declarada": a["k1"]}
    # R-02: puerta de perfil
    motivos = []
    if a["k1"] == "no_se":
        motivos.append("no sabes cuánta pérdida podrías absorber sin afectar tus gastos esenciales")
    if a["k2"] == "no":
        motivos.append("indicaste que no comprendes que podrías recibir menos dinero del que invertiste")
    if motivos:
        return {**base, "status": "requiere_aclaracion", "capacity_cap": None, "effective_risk": None,
                "preservation_by_capacity": False, "motivo": " y ".join(motivos),
                "reasons": ["Con estas respuestas, la demo no calcula un perfil operativo."]}
    # R-04: techo por capacidad
    techo = {"ninguna": "conservador", "hasta_10": "moderado", "mas_10": "arriesgado"}[a["k1"]]
    preserva = a["k1"] == "ninguna"
    # R-05: perfil operativo = mínimo entre tolerancia y techo
    operativo = P.NIVEL_A_PERFIL[min(P.NIVELES[tolerancia], P.NIVELES[techo])]
    razones = [f"Tu disposición a asumir riesgo es {_disposicion(s)}: corresponde a un perfil {tolerancia}."]
    if a["k1"] == "ninguna":
        razones.append("Declaraste que no podrías absorber pérdidas: el techo por capacidad es conservador "
                       "y la comparación exige alternativas que preserven capital en la simulación.")
    elif a["k1"] == "hasta_10":
        razones.append("Declaraste que podrías absorber una pérdida acotada: el techo por capacidad es moderado.")
    else:
        razones.append("Tu capacidad de pérdida declarada no agrega un techo adicional.")
    if operativo != tolerancia:
        razones.append(f"Tu perfil operativo es {operativo}: la tolerancia es tu disposición a asumir riesgo, "
                       "y el techo refleja tu capacidad económica declarada.")
    return {**base, "status": "vigente", "capacity_cap": techo, "effective_risk": operativo,
            "preservation_by_capacity": preserva, "motivo": None, "reasons": razones}
