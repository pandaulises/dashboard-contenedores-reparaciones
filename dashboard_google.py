import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard Contenedores en Vivo", layout="wide")

# --- CONEXIÓN CON GOOGLE SHEETS ---
# REEMPLAZA EL ENLACE DE ABAJO POR EL TUYO
URL_ORIGINAL = "https://docs.google.com/spreadsheets/d/1-x0dWR18MNYymjqSi2Wn7xK4NSA0s79tjLmhSfXaKZM/edit?gid=0#gid=0"

def cargar_datos(url):
    # Esta línea es "magia": convierte el link de edición en un link de descarga directa de datos
    csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
    # Si el link no tiene gid, usamos el formato básico
    if '/edit' in url and '/export' not in csv_url:
        csv_url = url.split('/edit')[0] + '/export?format=csv'
    return pd.read_csv(csv_url)

try:
    df = cargar_datos(URL_ORIGINAL)
    # Limpiamos espacios en los nombres de las columnas por si acaso
    df.columns = df.columns.str.strip()

    st.title("🚀 Dashboard de Operaciones - Google Sheets")
    st.markdown("Los datos se sincronizan automáticamente con la hoja compartida.")

    # --- BARRA LATERAL: FILTROS ---
    st.sidebar.header("Filtros de Control")
    
    # Filtro por Naviera
    navieras = df["Naviera"].unique().tolist()
    naviera_sel = st.sidebar.multiselect("Selecciona Navieras:", navieras, default=navieras)

    # Filtro por Quien Realizó (Reparó)
    reparadores = df["Reparó"].unique().tolist()
    reparador_sel = st.sidebar.multiselect("Selecciona Personal:", reparadores, default=reparadores)

    # Aplicar Filtros
    mask = (df["Naviera"].isin(naviera_sel)) & (df["Reparó"].isin(reparador_sel))
    df_filtrado = df[mask]

    # --- FILA 1 DE GRÁFICAS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Gráfica por Naviera")
        fig_nav = px.bar(df_filtrado, x="Naviera", color="Naviera", text_auto=True,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_nav, use_container_width=True)

    with col2:
        st.subheader("🏗️ Gráfica por Tipo de Contenedor")
        fig_tipo = px.pie(df_filtrado, names="Tipo", hole=0.4, 
                          color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_tipo, use_container_width=True)

    # --- FILA 2 DE GRÁFICAS ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🛠️ Trabajo Realizado (Frecuencia)")
        # Contamos cuántas veces se repite cada trabajo
        trabajos = df_filtrado["Trabajos Realizados"].value_counts().reset_index()
        trabajos.columns = ["Trabajo", "Cantidad"]
        fig_trab = px.bar(trabajos, y="Trabajo", x="Cantidad", orientation='h', 
                          color="Cantidad", color_continuous_scale="Viridis")
        st.plotly_chart(fig_trab, use_container_width=True)

    with col4:
        st.subheader("👷 ¿Quién Realizó el Trabajo?")
        fig_quien = px.histogram(df_filtrado, x="Reparó", color="Reparó",
                                 title="Productividad por Operador")
        st.plotly_chart(fig_quien, use_container_width=True)

    # --- TABLA DE DATOS CRUDA ---
    with st.expander("Ver tabla de datos completa"):
        st.write(df_filtrado)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Revisa que tu enlace de Google Sheets sea público y que el nombre de las columnas coincida.")
