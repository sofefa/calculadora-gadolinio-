# app.py
# ===========================================================
# INTERFAZ WEB (STREAMLIT) - CALCULADORA GADOLINIO RM
# ===========================================================



import streamlit as st

from backend import (
    PatientInput,
    GAD_FARMACOS,
    es_pediatrico,
    procesar_paciente,
)

# ---------- CONFIGURACIÓN BÁSICA ----------
st.set_page_config(
    page_title="Calculadora académica de gadolinio – RM",
    layout="centered",
)

st.title("Calculadora académica de gadolinio para RM")
st.caption("Uso exclusivamente docente. No utilizar para decisiones clínicas reales.")

st.markdown(
    """
**Fórmula base**  
\\[
\\text{Volumen (mL)} = \\frac{0{,}1 \\;\\text{mmol/kg} \\times \\text{peso (kg)}}{\\text{concentración (mmol/mL)}}
\\]
""",
)

st.divider()

# ---------- ENTRADA DE DATOS ----------
st.subheader("Datos del paciente")

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre completo", value="")
    edad = st.number_input("Edad (años)", min_value=0, max_value=120, value=5, step=1)

with col2:
    peso = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0, value=20.0, step=0.5)

estudio = st.text_input("Estudio (ej: RM cerebral)", value="")
tecnica = st.text_input("Técnica (ej: T1 con gadolinio)", value="")

# Determinar si es pediátrico para filtrar fármacos
pedi = es_pediatrico(int(edad))

if pedi:
    opciones_farmaco = [f for f, info in GAD_FARMACOS.items() if info["pediatrico_permitido"]]
else:
    opciones_farmaco = list(GAD_FARMACOS.keys())

farmaco = st.selectbox("Fármaco", options=opciones_farmaco, index=0)

col3, col4 = st.columns(2)
with col3:
    insuf_renal_str = st.radio(
        "¿Tiene problemas renales significativos?",
        options=["No", "Sí"],
        index=0,
        help="Ej.: ERC avanzada, TFG < 30 mL/min, diálisis.",
    )
with col4:
    alergia_str = st.radio(
        "¿Ha tenido reacciones alérgicas al contraste?",
        options=["No", "Sí"],
        index=0,
    )

insuf_renal = insuf_renal_str == "Sí"
alergia = alergia_str == "Sí"

st.divider()

# ---------- BOTÓN Y PROCESAMIENTO ----------
if st.button("Calcular volumen de gadolinio"):
    # Validaciones básicas de interfaz
    if not nombre.strip():
        st.error("Ingrese el nombre completo del paciente.")
        st.stop()

    if edad <= 0:
        st.error("La edad debe ser mayor a 0 años.")
        st.stop()

    if peso <= 0:
        st.error("El peso debe ser mayor a 0 kg.")
        st.stop()

    conc = GAD_FARMACOS[farmaco]["concentracion"]

    paciente = PatientInput(
        nombre_completo=nombre.strip(),
        edad=int(edad),
        peso_kg=float(peso),
        farmaco=farmaco,
        concentracion_mmol_ml=conc,
        tipo_estudio=estudio.strip(),
        tecnica=tecnica.strip(),
        insuf_renal_significativa=insuf_renal,
        alergia_previa=alergia,
    )

    resultado = procesar_paciente(paciente)

    # ---------- RESUMEN DEL PACIENTE ----------
    pedi_tag = " (Pediátrico)" if es_pediatrico(paciente.edad) else ""

    with st.expander("Resumen del paciente", expanded=True):
        st.write(
            f"""
- **Nombre completo:** {paciente.nombre_completo}  
- **Edad:** {paciente.edad} años{pedi_tag}  
- **Peso:** {paciente.peso_kg:.1f} kg  
- **Estudio:** {paciente.tipo_estudio or "No especificado"}  
- **Técnica:** {paciente.tecnica or "No especificada"}  
- **Fármaco:** {paciente.farmaco} ({paciente.concentracion_mmol_ml} mmol/mL)
"""
        )

    # ---------- RESULTADO / ADVERTENCIAS ----------
    if not resultado["ok"]:
        if resultado["mensajes"]:
            st.error("No se pudo calcular el volumen:")
            for m in resultado["mensajes"]:
                st.write(f"- {m}")

        if resultado["advertencias"]:
            st.warning("Advertencias:")
            for a in resultado["advertencias"]:
                st.write(f"- {a}")
    else:
        vol = resultado["volumen_ml"]

        st.success(f"Volumen estimado de gadolinio: **{vol:.1f} mL**")
        st.caption("Calculado con dosis estándar (0,1 mmol/kg).")

        if resultado["mensajes"]:
            st.markdown("**Detalle del cálculo:**")
            for m in resultado["mensajes"]:
                st.write(f"- {m}")

        if resultado["advertencias"]:
            st.markdown("**⚠ Advertencias:**")
            for a in resultado["advertencias"]:
                st.write(f"- {a}")

        st.info(
            "Prototipo educativo. La indicación real de contraste depende del tecnólogo médico "
            "a cargo y de los protocolos institucionales."
        )
else:
    st.info("Complete los datos y presione **Calcular volumen de gadolinio**.")


