import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis Clínico de Cardiología", page_icon="🩺", layout="wide")

st.title("🩺 Análisis Clínico de Pacientes - Cardiología")
st.write("Sube un archivo de Excel (.xlsx) para visualizar las métricas y gráficos de seguimiento.")

archivo_cargado = st.file_uploader("Seleccionar archivo Excel", type=["xlsx", "xls", "csv"])

if archivo_cargado is not None:
    try:
        # Cargar CSV o Excel según la extensión
        if archivo_cargado.name.endswith('.csv'):
            df = pd.read_csv(archivo_cargado)
        else:
            df = pd.read_excel(archivo_cargado)
        
        st.subheader("📋 Vista Previa de Datos")
        st.dataframe(df.head(10), use_container_width=True)

        # Filtrar únicamente columnas numéricas para graficar
        cols_numericas = df.select_dtypes(include=['number']).columns.tolist()
        cols_todas = df.columns.tolist()

        if cols_numericas:
            st.subheader("📊 Gráfica de Métricas Clínicas")
            
            # Selector para el Eje X (por defecto el nombre o índice)
            eje_x = st.selectbox(
                "Selecciona la columna para el eje horizontal (X):",
                options=cols_todas,
                index=0
            )

            # Selección de métricas numéricas
            metricas = st.multiselect(
                "Selecciona las métricas clínicas a graficar (Eje Y):",
                options=cols_numericas,
                default=[col for col in ['PAS', 'PAD', 'FC', 'FEVI', 'LDL'] if col in cols_numericas]
            )

            if metricas:
                fig = px.line(
                    df, 
                    x=eje_x,
                    y=metricas, 
                    title=f"Evolución de Parámetros Cardíacos según {eje_x}",
                    template="plotly_dark",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Por favor selecciona al menos una métrica numérica para graficar.")
        else:
            st.error("No se encontraron columnas numéricas en el archivo subido.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel o CSV para comenzar.")
