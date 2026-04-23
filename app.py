import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

#🔹 CONFIGURACIÓN

SUPABASE_URL = st.secrets["https://fxijvjmkoixadmddfiej.supabase.co"]
SUPABASE_KEY = st.secrets["sb_publishable_u2ibzh1juoGqnZrPvoApQg_4RQp6lxg"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="CRM Seprofor", layout="wide")

st.title("📊 CRM - Gestión Comercial")

#=====================================================
#🔹 1. CARGAR PROYECTOS
#=====================================================

@st.cache_data
def cargar_proyectos():
    data = supabase.table("proyectos").select("id, nombre").execute()
    return pd.DataFrame(data.data)

df_proyectos = cargar_proyectos()

#=====================================================
#🔹 2. SELECCIÓN
#=====================================================

proyecto = st.selectbox(
"Selecciona proyecto",
df_proyectos["nombre"] if not df_proyectos.empty else []
)

proyecto_id = None
if proyecto:
    proyecto_id = df_proyectos[df_proyectos["nombre"] == proyecto]["id"].values[0]

# =====================================================
# 🔹 3. FORMULARIO GESTIÓN
# =====================================================

st.subheader("📝 Registrar Gestión")

with st.form("form_gestion"):

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox("Tipo gestión", ["Llamada", "WhatsApp", "Visita"])
        resultado = st.selectbox("Resultado", ["Contacto", "No contacto"])
        estado = st.selectbox(
            "Estado",
            ["Prospecto", "Interesado", "Cotizado", "Negociando", "Cerrado", "Perdido"]
        )

    with col2:
        asesor = st.text_input("Asesor")
        monto = st.number_input("Monto", value=0)
        comentario = st.text_area("Comentario")

    submit = st.form_submit_button("Guardar")

    if submit and proyecto_id:

        data = {
            "proyecto_id": proyecto_id,
            "fecha_visita": datetime.now().isoformat(),
            "tipo_prospeccion": tipo,
            "contacto_logrado": resultado,
            "estado": estado,
            "comentarios": comentario,
            "monto": monto,
            "asesor": asesor
        }

        supabase.table("gestiones").insert(data).execute()

        st.success("✅ Gestión guardada")

# =====================================================
# 🔹 4. HISTORIAL
# =====================================================

st.subheader("📋 Historial")

if proyecto_id:

    data = supabase.table("gestiones") \
        .select("*") \
        .eq("proyecto_id", proyecto_id) \
        .order("fecha_visita", desc=True) \
        .execute()

    df_hist = pd.DataFrame(data.data)

    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Sin gestiones aún")