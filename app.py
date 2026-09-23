import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Análisis Clínico de Cardiología", page_icon="🩺", layout="wide")

st.title("🩺 Análisis Clínico de Pacientes - Cardiología")
st.write("Sube un archivo de Excel (.xlsx) para visualizar las métricas y gráficos de seguimiento.")

# Carga del archivo Excel
archivo_cargado = st.file_uploader("Seleccionar archivo Excel", type=["xlsx", "xls"])

if archivo_cargado is not None:
    try:
        df = pd.read_excel(archivo_cargado)
        
        st.subheader("📋 Vista Previa de Datos")
        st.dataframe(df.head(10), use_container_width=True)

        columnas = df.columns.tolist()
        
        # Selección de métricas para graficar
        metricas = st.multiselect(
            "Selecciona las métricas que deseas graficar:",
            options=columnas,
            default=[col for col in ['PAS', 'PAD', 'FC', 'FEVI', 'LDL'] if col in columnas]
        )

        if metricas:
            st.subheader("📊 Gráfica de Métricas Clínicas")
            fig = px.line(
                df, 
                y=metricas, 
                title="Evolución de Parámetros Cardíacos",
                template="plotly_dark",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Por favor selecciona al menos una métrica para visualizar la gráfica.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para mostrar el análisis.")
