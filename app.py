import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis Clínico de Cardiología", page_icon="🩺", layout="wide")

st.title("🩺 Panel de Control e Indicadores Clínicos - Cardiología")
st.write("Carga tu archivo con pacientes para explorar distribuciones, promedios y métricas de riesgo.")

archivo_cargado = st.file_uploader("Seleccionar archivo Excel o CSV", type=["xlsx", "xls", "csv"])

if archivo_cargado is not None:
    try:
        # 1. Cargar archivo
        if archivo_cargado.name.endswith('.csv'):
            df = pd.read_csv(archivo_cargado)
        else:
            df = pd.read_excel(archivo_cargado)
        
        # 2. Vista previa compacta
        with st.expander("📋 Ver tabla completa de datos", expanded=False):
            st.dataframe(df, use_container_width=True)

        cols_numericas = df.select_dtypes(include=['number']).columns.tolist()
        cols_texto = df.select_dtypes(include=['object']).columns.tolist()

        # 3. Barra Lateral para Filtros
        st.sidebar.header("🔍 Filtros de Análisis")
        
        # Filtro por Departamento / Ciudad si existen
        df_filtrado = df.copy()
        if 'Departamento' in df.columns:
            deptos = ["Todos"] + list(df['Departamento'].dropna().unique())
            depto_sel = st.sidebar.selectbox("Filtrar por Departamento:", deptos)
            if depto_sel != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Departamento'] == depto_sel]

        if 'Ciudad' in df.columns:
            ciudades = ["Todas"] + list(df_filtrado['Ciudad'].dropna().unique())
            ciudad_sel = st.sidebar.selectbox("Filtrar por Ciudad:", ciudades)
            if ciudad_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado['Ciudad'] == ciudad_sel]

        # Pestanas de Visualización para Toma de Decisiones
        tab1, tab2, tab3 = st.tabs(["📊 Comparativa por Paciente", "📈 Distribución de Riesgo", "🗺️ Promedios por Ubicación"])

        # PESTAÑA 1: Comparativa por Paciente (Dispersión o Barras)
        with tab1:
            st.subheader("Análisis Individual / Muestra de Pacientes")
            
            tipo_grafico = st.radio("Tipo de visualización:", ["Dispersión (Puntos - Ideal para >50 pacientes)", "Barras (Ideal para muestra seleccionada)"], horizontal=True)
            
            # Selector de métricas
            metricas_sel = st.multiselect(
                "Métricas clínicas a visualizar:",
                options=cols_numericas,
                default=[m for m in ['PAS', 'PAD', 'FC', 'FEVI', 'LDL'] if m in cols_numericas]
            )

            # Limitador de pacientes para no saturar si elige barras
            if "Barras" in tipo_grafico:
                max_pacientes = st.slider("Número de pacientes a mostrar en pantalla:", 5, min(100, len(df_filtrado)), 20)
                df_graf = df_filtrado.head(max_pacientes)
                
                if metricas_sel:
                    fig_bar = px.bar(
                        df_graf, 
                        x='Nombre_Paciente' if 'Nombre_Paciente' in df_graf.columns else df_graf.index, 
                        y=metricas_sel,
                        barmode="group",
                        title=f"Métricas Clínicas (Primeros {max_pacientes} pacientes)",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                if metricas_sel:
                    fig_scatter = px.scatter(
                        df_filtrado, 
                        x='Nombre_Paciente' if 'Nombre_Paciente' in df_filtrado.columns else df_filtrado.index,
                        y=metricas_sel,
                        hover_data=['Edad', 'Ciudad'] if 'Ciudad' in df_filtrado.columns else [],
                        title="Distribución Individual de Indicadores por Paciente",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)

        # PESTAÑA 2: Distribución y Rangos Clínicos (Histogramas y Boxplots)
        with tab2:
            st.subheader("Análisis de Rangos y Valores Críticos")
            col1, col2 = st.columns(2)
            
            with col1:
                metrica_hist = st.selectbox("Selecciona métrica para ver su Histograma de Frecuencia:", cols_numericas)
                fig_hist = px.histogram(
                    df_filtrado, 
                    x=metrica_hist, 
                    nbins=20, 
                    marginal="box",
                    title=f"Distribución General de {metrica_hist}",
                    color_discrete_sequence=['#00CC96'],
                    template="plotly_dark"
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                if 'Edad' in cols_numericas and metrica_hist != 'Edad':
                    fig_scatter_corr = px.scatter(
                        df_filtrado,
                        x='Edad',
                        y=metrica_hist,
                        trendline="ols",
                        title=f"Relación entre Edad y {metrica_hist}",
                        color_discrete_sequence=['#AB63FA'],
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_scatter_corr, use_container_width=True)

        # PESTAÑA 3: Promedios por Ubicación
        with tab3:
            st.subheader("Comportamiento Regional de Indicadores")
            if 'Ciudad' in df.columns or 'Departamento' in df.columns:
                geo_col = 'Departamento' if 'Departamento' in df.columns else 'Ciudad'
                df_geo = df_filtrado.groupby(geo_col)[cols_numericas].mean().reset_index()
                
                metrica_geo = st.selectbox("Métrica para comparar promedios regionales:", cols_numericas, index=0)
                
                fig_geo = px.bar(
                    df_geo,
                    x=geo_col,
                    y=metrica_geo,
                    color=metrica_geo,
                    title=f"Promedio de {metrica_geo} por {geo_col}",
                    template="plotly_dark",
                    color_continuous_scale="Reds"
                )
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.info("El archivo no incluye columnas de 'Ciudad' o 'Departamento' para este análisis.")

    except Exception as e:
        st.error(f"Error procesando los datos: {e}")
else:
    st.info("Por favor, sube un archivo Excel o CSV para habilitar el panel clínico.")
