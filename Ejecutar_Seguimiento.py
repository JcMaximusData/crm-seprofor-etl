import pandas as pd
from db import supabase

# 🔹 URL de tu Google Sheets en CSV
URL = "https://docs.google.com/spreadsheets/d/1v4hCcuQN_kiN8o0uC-ClMC-vN0seJpgzCEAYt3pGaB8/export?format=csv&gid=767032110"

# 🔹 1) Leer data
df = pd.read_csv(URL)

# 🔹 2) Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.upper()

# 🔹 3) Funciones helper
def col(df, name):
    return df[name] if name in df.columns else pd.Series([None] * len(df))

# 🔹 4) Parseos seguros
marca_temporal = pd.to_datetime(col(df, "MARCA TEMPORAL"), dayfirst=True, errors="coerce") \
                    .dt.strftime("%Y-%m-%d %H:%M:%S")

fecha_contacto = pd.to_datetime(col(df, "FECHA DE CONTACTO"), dayfirst=True, errors="coerce") \
                    .dt.strftime("%Y-%m-%d")

fecha_visita = pd.to_datetime(col(df, "FECHA DE VISITA"), dayfirst=True, errors="coerce") \
                    .dt.strftime("%Y-%m-%d")

monto_proyecto = pd.to_numeric(col(df, "MONTO DEL PROYECTO"), errors="coerce")
abono_inicial  = pd.to_numeric(col(df, "ABONO INICIAL"), errors="coerce")

# 🔹 5) Mapeo
df_final = pd.DataFrame({
    "marca_temporal": marca_temporal,
    "empresa": col(df, "EMPRESA DUEÑA DEL PROYECTO").astype(str).str.strip(),
    "proyecto": col(df, "NOMBRE DEL PROYECTO").astype(str).str.strip(),
    "empresa_constructora": col(df, "EMPRESA QUE CONSTRUYE").astype(str).str.strip(),
    "fecha_contacto": fecha_contacto,
    "fecha_visita": fecha_visita,
    "nombre_contacto": col(df, "NOMBRE DE CONTACTO").astype(str).str.strip(),
    "numero_contacto": col(df, "NUMERO DE CONTACTO").astype(str).str.strip(),
    "canal": col(df, "CANAL").astype(str).str.strip(),
    "asesor_comercial": col(df, "ASESOR COMERCIAL").astype(str).str.strip(),
    "tipo_prospeccion": col(df, "TIPO DE PROSPECCIÓN").astype(str).str.strip(),
    "contacto_logrado": col(df, "¿SE LOGRÓ CONTACTO?").astype(str).str.strip(),
    "nivel_interes": col(df, "NIVEL DE INTERÉS").astype(str).str.strip(),
    "estado": col(df, "ESTADO").astype(str).str.strip(),
    "estado_negociacion": col(df, "ESTADO DE NEGOCIACIÓN").astype(str).str.strip(),
    "se_cotizo": col(df, "¿SE COTIZÓ?").astype(str).str.strip(),
    "monto_proyecto": monto_proyecto,
    "abono_inicial": abono_inicial,
    "se_cerro_venta": col(df, "¿SE CERRÓ LA VENTA?").astype(str).str.strip(),
    "motivo_perdida": col(df, "MOTIVO DE PÉRDIDA").astype(str).str.strip(),
    "comentarios": col(df, "COMENTARIOS").astype(str).str.strip(),
})

# 🔹 6) Limpiar vacíos
df_final = df_final.replace({"": None, "nan": None, "None": None})

# =====================================================
# 🔥 7) DETECTAR DUPLICADOS (ANTI-JOIN)
# =====================================================

print("🔍 Consultando registros existentes...")

existentes = supabase.table("seguimiento") \
    .select("empresa, proyecto, fecha_contacto") \
    .execute()

df_existentes = pd.DataFrame(existentes.data)

if not df_existentes.empty:
    df_merge = df_final.merge(
        df_existentes,
        on=["empresa", "proyecto", "fecha_contacto"],
        how="left",
        indicator=True
    )

    df_nuevos = df_merge[df_merge["_merge"] == "left_only"].drop(columns=["_merge"])
else:
    df_nuevos = df_final.copy()

print(f"🆕 Nuevos registros detectados: {len(df_nuevos)}")

# =====================================================
# 🔥 8) INSERT SOLO NUEVOS
# =====================================================
df_final = df_final.where(pd.notnull(df_final), None)
records = df_nuevos.to_dict(orient="records")

if len(records) == 0:
    print("😎 No hay datos nuevos para insertar")
else:
    batch_size = 100

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        supabase.table("seguimiento").insert(batch).execute()
        print(f"✔ Insertados {i + len(batch)} registros")

    print("🔥 Carga incremental completa")
