import streamlit as st
import pandas as pd
from utils.tablas import calcular_metricas_gestion, tabla_extremos
from utils.graficos import histograma_tiempos_comp

def inject_premium_styles():
    """
    Inyecta estilos CSS para cambiar la tipografía, mejorar el sidebar, 
    eliminar bordes innecesarios y aplicar una estética moderna y limpia.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Tipografía global */
        html, body, [class*="css"], .stWidgetLabel, .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Personalización de la barra lateral (Sidebar) */
        section[data-testid="stSidebar"] {
            background-color: #f8fafc !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        
        /* Optimización de espaciados de contenedores */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Clases de encabezados estéticos */
        .custom-title {
            font-weight: 700;
            color: #0f172a;
            font-size: 2.4rem;
            margin-bottom: 1.5rem;
            letter-spacing: -0.8px;
        }
        
        .custom-section-header {
            font-weight: 600;
            font-size: 1.5rem;
            color: #1e293b;
            border-left: 5px solid #2563eb;
            padding-left: 12px;
            margin-top: 2.2rem;
            margin-bottom: 1rem;
            letter-spacing: -0.4px;
        }
        
        .custom-subsection {
            font-weight: 500;
            font-size: 1.15rem;
            color: #475569;
            margin-top: 0.8rem;
            margin-bottom: 0.8rem;
            letter-spacing: -0.2px;
        }

        /* Contornos estéticos para contenedores de gráficos y tablas */
        div[data-testid="stVerticalBlockBorder"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 18px !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stVerticalBlockBorder"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1) !important;
            border-color: #cbd5e1 !important;
        }
        
        /* Forzar la misma altura exacta a todas las tarjetas dentro de las columnas */
        div[data-testid="column"] div[data-testid="stVerticalBlockBorder"] {
            height: 415px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, grad_start: str, grad_end: str, shadow_color: str):
    """
    Dibuja una tarjeta de KPI premium en HTML con un gradiente y micro-animaciones CSS.
    """
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, {grad_start} 0%, {grad_end} 100%);
        color: white;
        border-radius: 12px;
        padding: 16px 14px;
        box-shadow: 0 10px 18px {shadow_color};
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 10px;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 14px 25px {shadow_color}'" onmouseout="this.style.transform='none'; this.style.boxShadow='0 10px 18px {shadow_color}'">
        <div style="font-size: 0.8rem; font-weight: 400; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px;">{label}</div>
        <div style="font-size: 1.7rem; font-weight: 700; letter-spacing: -0.5px;">{value}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_comparativo_layout(
    df_a_filtered,
    df_b_filtered,
    columna_tiempo: str,
    columna_id: str,
    columnas_tabla: list,
    titulo_pagina: str = "📊 Comparativa de Distribuciones de Tiempos",
    label_a: str = "🔹 Distribución Actual (A)",
    label_b: str = "🔸 Distribución Comparación (B)",
    colores_a: tuple = ("#2E86C1", "#D6EAF8", "#1B4F72"),  # main, light, dark para gráfico
    colores_b: tuple = ("#16A085", "#E8F8F5", "#0E6251"),   # main, light, dark para gráfico
    colores_a_grad: tuple = ("#1b4f72", "#2e86c1", "rgba(46, 134, 193, 0.2)"),  # start, end, shadow para KPI
    colores_b_grad: tuple = ("#0e6251", "#16a085", "rgba(22, 160, 133, 0.2)")   # start, end, shadow para KPI
):
    """
    Función plantilla para renderizar el layout del dashboard de comparación de tiempos.
    Reutiliza los indicadores de KPIs, gráficos KDE y tablas extremas de forma parametrizada.
    """
    # -------------------------------------------------------------
    # --- 1. PRE-CÁLCULO DE ELEMENTOS GRÁFICOS Y TABLAS ---
    # -------------------------------------------------------------
    
    # 1.1 Pre-cálculo de KPIs
    metricas_a = calcular_metricas_gestion(df_a_filtered[columna_tiempo])
    metricas_b = calcular_metricas_gestion(df_b_filtered[columna_tiempo])

    # 1.2 Pre-cálculo de eje X común
    p97_vals = []
    if not df_a_filtered.empty and len(df_a_filtered[columna_tiempo].dropna()) > 0:
        p97_vals.append(df_a_filtered[columna_tiempo].quantile(0.97))
    if not df_b_filtered.empty and len(df_b_filtered[columna_tiempo].dropna()) > 0:
        p97_vals.append(df_b_filtered[columna_tiempo].quantile(0.97))

    max_val_x = max(p97_vals) if p97_vals else 100
    if pd.isna(max_val_x) or max_val_x <= 0:
        max_val_x = 100

    # 1.3 Pre-cálculo de Gráficos Plotly (KDE)
    fig_a = histograma_tiempos_comp(
        df_a_filtered[columna_tiempo], 
        f"Densidad de Tiempos - {label_a}", 
        colores_a[0], colores_a[1], colores_a[2], 
        max_val_x=max_val_x,
        height=370
    )
    
    fig_b = histograma_tiempos_comp(
        df_b_filtered[columna_tiempo], 
        f"Densidad de Tiempos - {label_b}", 
        colores_b[0], colores_b[1], colores_b[2], 
        max_val_x=max_val_x,
        height=370
    )

    # 1.4 Pre-cálculo de Dataframes de Extremos
    extremos_a = tabla_extremos(df_a_filtered, columnas_tabla, time_col=columna_tiempo, id_col=columna_id)
    extremos_b = tabla_extremos(df_b_filtered, columnas_tabla, time_col=columna_tiempo, id_col=columna_id)

    # -------------------------------------------------------------
    # --- 2. RENDERIZADO VISUAL DEL DASHBOARD ---
    # -------------------------------------------------------------
    inject_premium_styles()

    # Título principal estilizado
    st.markdown(f'<div class="custom-title">{titulo_pagina}</div>', unsafe_allow_html=True)

    # --- SECCIÓN 1: KPIs ---
    st.markdown('<div class="custom-section-header">📋 Comparación Descriptiva de los Indicadores</div>', unsafe_allow_html=True)

    # 1.1 Distribución A KPIs
    st.markdown(f'<div class="custom-subsection">{label_a}</div>', unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        render_kpi_card("Total Gestiones", metricas_a["cantidad"], *colores_a_grad)
    with kpi_col2:
        render_kpi_card("Tiempo Promedio", metricas_a["promedio"], *colores_a_grad)
    with kpi_col3:
        render_kpi_card("Mediana del Tiempo", metricas_a["mediana"], *colores_a_grad)
    with kpi_col4:
        render_kpi_card("Percentil 97", metricas_a["p97"], *colores_a_grad)

    # 1.2 Distribución B KPIs
    st.markdown(f'<div class="custom-subsection">{label_b}</div>', unsafe_allow_html=True)
    kpi_col1_b, kpi_col2_b, kpi_col3_b, kpi_col4_b = st.columns(4)
    with kpi_col1_b:
        render_kpi_card("Total Gestiones", metricas_b["cantidad"], *colores_b_grad)
    with kpi_col2_b:
        render_kpi_card("Tiempo Promedio", metricas_b["promedio"], *colores_b_grad)
    with kpi_col3_b:
        render_kpi_card("Mediana del Tiempo", metricas_b["mediana"], *colores_b_grad)
    with kpi_col4_b:
        render_kpi_card("Percentil 97", metricas_b["p97"], *colores_b_grad)

    st.divider()

    # --- SECCIÓN 2: KDE Y CASOS EXTREMOS ---
    st.markdown('<div class="custom-section-header">📈 Comparación de Densidad y Casos Extremos</div>', unsafe_allow_html=True)

    # Fila A (Distribución A)
    col_charts_a, col_tables_a = st.columns([1.2, 0.8])

    with col_charts_a:
        with st.container(border=True):
            st.plotly_chart(fig_a, use_container_width=True)

    with col_tables_a:
        with st.container(border=True):
            st.write(f"##### 🔹 Extremos - {label_a} (100 de mayor duración)")
            st.dataframe(
                extremos_a,
                height=300,
                width='stretch'
            )

    st.write("")  # Spacing

    # Fila B (Distribución B)
    col_charts_b, col_tables_b = st.columns([1.2, 0.8])

    with col_charts_b:
        with st.container(border=True):
            st.plotly_chart(fig_b, use_container_width=True)

    with col_tables_b:
        with st.container(border=True):
            st.write(f"##### 🔸 Extremos - {label_b} (100 de mayor duración)")
            st.dataframe(
                extremos_b,
                height=300,
                width='stretch'
            )
