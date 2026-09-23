import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis Clínico de Cardiología", page_icon="🩺", layout="wide")

st.title("🩺 Panel de Control e Indicadores Clínicos - Cardiología")
st.write("Carga tu archivo con pacientes para explorar distribuciones, rangos etarios y métricas de riesgo.")

archivo_cargado = st.file_uploader("Seleccionar archivo Excel o CSV", type=["xlsx", "xls", "csv"])

if archivo_cargado is not None:
    try:
        # 1. Cargar archivo
        if archivo_cargado.name.endswith('.csv'):
            df = pd.read_csv(archivo_cargado)
        else:
            df = pd.read_excel(archivo_cargado)

        # 2. Categorización epidemiológica de Edad (si existe la columna)
        if 'Edad' in df.columns:
            bins = [0, 39, 49, 59, 69, 79, 120]
            labels = ['< 40 años', '40 - 49 años', '50 - 59 años', '60 - 69 años', '70 - 79 años', '80+ años']
            df['Rango_Edad'] = pd.cut(df['Edad'], bins=bins, labels=labels, right=True)

        with st.expander("📋 Ver tabla completa de datos", expanded=False):
            st.dataframe(df, use_container_width=True)

        cols_numericas = df.select_dtypes(include=['number']).columns.tolist()

        # 3. Barra Lateral de Filtros
        st.sidebar.header("🔍 Filtros de Análisis")
        df_filtrado = df.copy()

        if 'Rango_Edad' in df.columns:
            rangos = ["Todos"] + list(df['Rango_Edad'].cat.categories)
            rango_sel = st.sidebar.selectbox("Filtrar por Rango de Edad:", rangos)
            if rango_sel != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Rango_Edad'] == rango_sel]

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

        # 4. Pestañas de Análisis
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Comparativa Pacientes", 
            "👥 Análisis por Grupo Etario", 
            "📈 Distribución de Riesgo", 
            "🗺️ Promedios Regionales"
        ])

        # PESTAÑA 1: Comparativa por Paciente
        with tab1:
            st.subheader("Análisis Individual / Muestra de Pacientes")
            tipo_grafico = st.radio("Tipo de visualización:", ["Dispersión (Puntos - Ideal para >50 pacientes)", "Barras (Ideal para muestra seleccionada)"], horizontal=True)
            
            metricas_sel = st.multiselect(
                "Métricas clínicas a visualizar:",
                options=cols_numericas,
                default=[m for m in ['PAS', 'PAD', 'FC', 'FEVI', 'LDL'] if m in cols_numericas]
            )

            if "Barras" in tipo_grafico:
                max_pacientes = st.slider("Número de pacientes a mostrar:", 5, min(100, max(5, len(df_filtrado))), 10)
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

        # PESTAÑA 2: Análisis por Grupo Etario (NUEVA)
        with tab2:
            st.subheader("Prevalencia y Comportamiento Clínico por Grupos de Edad")
            if 'Rango_Edad' in df_filtrado.columns:
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Conteo de pacientes por rango de edad
                    df_conteo = df_filtrado['Rango_Edad'].value_counts().reset_index()
                    df_conteo.columns = ['Rango_Edad', 'Cantidad_Pacientes']
                    fig_pie = px.pie(
                        df_conteo, 
                        names='Rango_Edad', 
                        values='Cantidad_Pacientes',
                        title="Distribución Porcentual de Pacientes por Edad",
                        template="plotly_dark",
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_b:
                    # Promedio de indicadores por grupo de edad
                    cols_med = [c for c in cols_numericas if c != 'Edad']
                    df_prom_edad = df_filtrado.groupby('Rango_Edad', observed=False)[cols_med].mean().reset_index()
                    
                    metrica_etaria = st.selectbox("Selecciona métrica para evaluar promedio por edad:", cols_med)
                    fig_bar_edad = px.bar(
                        df_prom_edad,
                        x='Rango_Edad',
                        y=metrica_etaria,
                        color=metrica_etaria,
                        title=f"Promedio de {metrica_etaria} por Grupo Etario",
                        template="plotly_dark",
                        color_continuous_scale="Viridis"
                    )
                    st.plotly_chart(fig_bar_edad, use_container_width=True)
            else:
                st.info("El archivo no cuenta con la columna 'Edad' para calcular los rangos.")

        # PESTAÑA 3: Distribución y Rangos
        with tab3:
            st.subheader("Análisis de Rangos y Valores Críticos")
            col1, col2 = st.columns(2)
            with col1:
                metrica_hist = st.selectbox("Selecciona métrica para su Histograma:", cols_numericas)
                fig_hist = px.histogram(
                    df_filtrado, x=metrica_hist, nbins=20, marginal="box",
                    title=f"Distribución General de {metrica_hist}",
                    color_discrete_sequence=['#00CC96'], template="plotly_dark"
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                if 'Edad' in cols_numericas and metrica_hist != 'Edad':
                    fig_scatter_corr = px.scatter(
                        df_filtrado, x='Edad', y=metrica_hist, trendline="ols",
                        title=f"Relación entre Edad y {metrica_hist}",
                        color_discrete_sequence=['#AB63FA'], template="plotly_dark"
                    )
                    st.plotly_chart(fig_scatter_corr, use_container_width=True)

        # PESTAÑA 4: Promedios Regionales
        with tab4:
            st.subheader("Comportamiento Regional de Indicadores")
            if 'Ciudad' in df.columns or 'Departamento' in df.columns:
                geo_col = 'Departamento' if 'Departamento' in df.columns else 'Ciudad'
                df_geo = df_filtrado.groupby(geo_col)[cols_numericas].mean().reset_index()
                metrica_geo = st.selectbox("Métrica para comparar por ubicación:", cols_numericas, index=0)
                fig_geo = px.bar(
                    df_geo, x=geo_col, y=metrica_geo, color=metrica_geo,
                    title=f"Promedio de {metrica_geo} por {geo_col}",
                    template="plotly_dark", color_continuous_scale="Reds"
                )
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.info("El archivo no incluye columnas de ubicación.")

    except Exception as e:
        st.error(f"Error procesando los datos: {e}")
else:
    st.info("Por favor, sube un archivo Excel o CSV para habilitar el panel clínico.")
