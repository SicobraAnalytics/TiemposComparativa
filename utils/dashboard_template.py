import streamlit as st
import pandas as pd
from utils.tablas import calcular_metricas_gestion, tabla_extremos
from utils.graficos import histograma_tiempos_comp

def render_comparativo_layout(
    df_a_filtered,
    df_b_filtered,
    columna_tiempo: str,
    columna_id: str,
    columnas_tabla: list,
    titulo_pagina: str = "📊 Comparativa de Distribuciones de Tiempos",
    label_a: str = "🔹 Distribución Actual (A)",
    label_b: str = "🔸 Distribución Comparación (B)",
    colores_a: tuple = ("#2E86C1", "#D6EAF8", "#1B4F72"),  # main, light, dark (Azul)
    colores_b: tuple = ("#16A085", "#E8F8F5", "#0E6251")   # main, light, dark (Teal/Verde)
):
    """
    Función plantilla para renderizar el layout del dashboard de comparación de tiempos.
    Reutiliza los indicadores de KPIs, gráficos KDE y tablas extremas de forma parametrizada.
    """
    st.title(titulo_pagina)

    # --- SECCIÓN 1: KPIs ---
    st.markdown("## 📋 Comparación Descriptiva de los Indicadores")

    # 1.1 Distribución A KPIs
    st.markdown(f"### {label_a}")
    metricas_a = calcular_metricas_gestion(df_a_filtered[columna_tiempo])

    with st.container(border=True):
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric(label="Total Gestiones", value=metricas_a["cantidad"])
        with kpi_col2:
            st.metric(label="Tiempo Promedio", value=metricas_a["promedio"])
        with kpi_col3:
            st.metric(label="Mediana del Tiempo", value=metricas_a["mediana"])
        with kpi_col4:
            st.metric(label="Percentil 97", value=metricas_a["p97"])

    # 1.2 Distribución B KPIs
    st.markdown(f"### {label_b}")
    metricas_b = calcular_metricas_gestion(df_b_filtered[columna_tiempo])

    with st.container(border=True):
        kpi_col1_b, kpi_col2_b, kpi_col3_b, kpi_col4_b = st.columns(4)
        with kpi_col1_b:
            st.metric(label="Total Gestiones", value=metricas_b["cantidad"])
        with kpi_col2_b:
            st.metric(label="Tiempo Promedio", value=metricas_b["promedio"])
        with kpi_col3_b:
            st.metric(label="Mediana del Tiempo", value=metricas_b["mediana"])
        with kpi_col4_b:
            st.metric(label="Percentil 97", value=metricas_b["p97"])

    st.divider()

    # --- SECCIÓN 2: KDE Y CASOS EXTREMOS ---
    st.markdown("## 📈 Comparación de Densidad y Casos Extremos")

    # Compute common X range for charts to align axes
    p97_vals = []
    if not df_a_filtered.empty and len(df_a_filtered[columna_tiempo].dropna()) > 0:
        p97_vals.append(df_a_filtered[columna_tiempo].quantile(0.97))
    if not df_b_filtered.empty and len(df_b_filtered[columna_tiempo].dropna()) > 0:
        p97_vals.append(df_b_filtered[columna_tiempo].quantile(0.97))

    max_val_x = max(p97_vals) if p97_vals else 100
    if pd.isna(max_val_x) or max_val_x <= 0:
        max_val_x = 100

    # Fila A (Distribución A)
    col_charts_a, col_tables_a = st.columns([1.2, 0.8], vertical_alignment="center")

    with col_charts_a:
        fig_a = histograma_tiempos_comp(
            df_a_filtered[columna_tiempo], 
            f"Densidad de Tiempos - {label_a}", 
            colores_a[0], colores_a[1], colores_a[2], 
            max_val_x=max_val_x
        )
        st.plotly_chart(fig_a, use_container_width=True)

    with col_tables_a:
        st.write(f"##### 🔹 Extremos - {label_a} (100 de mayor duración)")
        extremos_a = tabla_extremos(df_a_filtered, columnas_tabla, time_col=columna_tiempo, id_col=columna_id)
        st.dataframe(
            extremos_a,
            height=320,
            width='stretch'
        )

    st.write("")  # Spacing

    # Fila B (Distribución B)
    col_charts_b, col_tables_b = st.columns([1.2, 0.8], vertical_alignment="center")

    with col_charts_b:
        fig_b = histograma_tiempos_comp(
            df_b_filtered[columna_tiempo], 
            f"Densidad de Tiempos - {label_b}", 
            colores_b[0], colores_b[1], colores_b[2], 
            max_val_x=max_val_x
        )
        st.plotly_chart(fig_b, use_container_width=True)

    with col_tables_b:
        st.write(f"##### 🔸 Extremos - {label_b} (100 de mayor duración)")
        extremos_b = tabla_extremos(df_b_filtered, columnas_tabla, time_col=columna_tiempo, id_col=columna_id)
        st.dataframe(
            extremos_b,
            height=320,
            width='stretch'
        )
