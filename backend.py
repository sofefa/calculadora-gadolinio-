# backend.py
# ===========================================================
# CALCULADORA ACADÉMICA DE GADOLINIO – RM (LÓGICA)
# ===========================================================
# Uso exclusivamente docente. No utilizar para decisiones clínicas reales.
# ===========================================================



from dataclasses import dataclass
from typing import Dict, Any

# ---------------------------------------
# Datos de fármacos y concentraciones
# ---------------------------------------
GAD_FARMACOS: Dict[str, Dict[str, Any]] = {
    "Dotarem":  {"concentracion": 0.5, "pediatrico_permitido": True},
    "Omniscan": {"concentracion": 0.5, "pediatrico_permitido": False},
    "Prohance": {"concentracion": 0.5, "pediatrico_permitido": True},
    "Gadovist": {"concentracion": 1.0, "pediatrico_permitido": True},
    "Gadavist": {"concentracion": 1.0, "pediatrico_permitido": True},
}

DOSIS_ESTANDAR_MMOL_KG = 0.1  # RM estándar


@dataclass
class PatientInput:
    nombre_completo: str
    edad: int
    peso_kg: float
    farmaco: str
    concentracion_mmol_ml: float
    tipo_estudio: str
    tecnica: str
    insuf_renal_significativa: bool
    alergia_previa: bool


def es_pediatrico(edad: int) -> bool:
    """True si la edad está entre 1 y 12 años (inclusive)."""
    return 1 <= edad <= 12


def calcular_volumen(
    peso_kg: float,
    concentracion_mmol_ml: float,
    dosis_mmol_kg: float = DOSIS_ESTANDAR_MMOL_KG
) -> float:
    """Volumen (mL) = (dosis_mmol_kg × peso_kg) / concentracion_mmol_ml"""
    if peso_kg <= 0:
        raise ValueError("El peso debe ser mayor a 0 kg.")
    if concentracion_mmol_ml <= 0:
        raise ValueError("La concentración debe ser mayor a 0.")
    if dosis_mmol_kg <= 0:
        raise ValueError("La dosis debe ser mayor a 0.")

    vol = (dosis_mmol_kg * peso_kg) / concentracion_mmol_ml
    return round(vol, 1)


def procesar_paciente(p: PatientInput) -> Dict[str, Any]:
    """Procesa la lógica académica, filtros clínicos simulados y cálculo."""
    resultado: Dict[str, Any] = {
        "ok": True,
        "volumen_ml": None,
        "mensajes": [],
        "advertencias": [],
    }

    # Validaciones básicas
    if p.edad <= 0:
        resultado["ok"] = False
        resultado["mensajes"].append("La edad debe ser mayor a 0 años.")
        return resultado

    if p.peso_kg <= 0:
        resultado["ok"] = False
        resultado["mensajes"].append("El peso debe ser mayor a 0 kg.")
        return resultado

    # Bloqueo por insuficiencia renal severa
    if p.insuf_renal_significativa:
        resultado["ok"] = False
        resultado["advertencias"].append(
            "Uso de contraste NO recomendado. Consultar con médico tratante "
            "(ERC avanzada, TFG < 30 mL/min o diálisis)."
        )
        return resultado

    pediatrico = es_pediatrico(p.edad)
    info_farmaco = GAD_FARMACOS.get(p.farmaco)

    # Si el fármaco no existe
    if info_farmaco is None:
        resultado["ok"] = False
        resultado["mensajes"].append("Fármaco de gadolinio no reconocido.")
        return resultado

    # Si es pediátrico y el fármaco no está permitido
    if pediatrico and not info_farmaco["pediatrico_permitido"]:
        resultado["ok"] = False
        resultado["advertencias"].append(
            "Fármaco NO permitido en población pediátrica (1–12 años)."
        )
        return resultado

    # Cálculo de volumen
    vol = calcular_volumen(p.peso_kg, p.concentracion_mmol_ml)
    resultado["volumen_ml"] = vol

    resultado["mensajes"].append(
        f"Volumen (mL) = (0,1 mmol/kg × {p.peso_kg:.1f} kg) / {p.concentracion_mmol_ml:.3f} mmol/mL"
    )

    # Advertencias académicas
    if pediatrico:
        resultado["advertencias"].append(
            "Paciente pediátrico: nunca se aumenta la dosis estándar de 0,1 mmol/kg."
        )

    if p.alergia_previa:
        resultado["advertencias"].append(
            "Antecedente de reacción alérgica. Considerar premedicación o alternativa."
        )

    return resultado


