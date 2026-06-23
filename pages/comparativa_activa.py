import streamlit as st
import pandas as pd

from utils.dashboard_template import render_comparativo_layout

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df_a = pd.read_parquet("Data/gestiones_dashboard_activa.parquet")
    df_b = pd.read_parquet("Data/gestiones_comparacion_activa.parquet")
    
    # Remove unused categories for both datasets
    for col in df_a.select_dtypes("category").columns:
        df_a[col] = df_a[col].cat.remove_unused_categories()
    for col in df_b.select_dtypes("category").columns:
        df_b[col] = df_b[col].cat.remove_unused_categories()
        
    return df_a, df_b

df_a, df_b = load_data()

# --- SIDEBAR: Filters ---
with st.sidebar:
    st.title(":material/filter_alt: Filtros")

    # Canal filter using st.pills
    selected_channels = st.pills(
        "Canal", 
        options=df_a["CodigoCanal"].cat.categories,
        selection_mode="multi",
        key="CanalFilter"
    )

    # Producto filter using st.multiselect
    selected_products = st.multiselect(
        "Producto",
        options=df_a["Producto"].cat.categories,
        default=[],
        key="ProductoFilter"
    )

    # Etapa de Cobranza filter using st.multiselect
    selected_stages = st.multiselect(
        "Etapa de Cobranza",
        options=df_a["RangoMoraInicio"].cat.categories,
        default=[],
        key="EtapaFilter"
    )

    # Respuesta filter using st.multiselect
    selected_responses = st.multiselect(
        "Respuesta",
        options=df_a["NombreRespuesta"].cat.categories,
        default=[],
        key="RespuestaFilter"
    )

# --- FILTERING LOGIC ---
def apply_filters(df, channels, products, stages, responses):
    filtered = df.copy()
    if channels:
        filtered = filtered[filtered["CodigoCanal"].isin(channels)]
    if products:
        filtered = filtered[filtered["Producto"].isin(products)]
    if stages:
        filtered = filtered[filtered["RangoMoraInicio"].isin(stages)]
    if responses:
        filtered = filtered[filtered["NombreRespuesta"].isin(responses)]
    return filtered

df_a_filtered = apply_filters(
    df_a, 
    selected_channels, 
    selected_products, 
    selected_stages, 
    selected_responses
)

df_b_filtered = apply_filters(
    df_b, 
    selected_channels, 
    selected_products, 
    selected_stages, 
    selected_responses
)

# --- RENDER COMPARATIVE LAYOUT ---
cols_to_show = ["IdGestion", "UserNameGestion", "FechaHoraGestion", "TipoContacto", "DuracionAudio", "NumeroOperacion", "Producto", "RangoMoraInicio"]

render_comparativo_layout(
    df_a_filtered=df_a_filtered,
    df_b_filtered=df_b_filtered,
    columna_tiempo="DuracionAudio",
    columna_id="IdGestion",
    columnas_tabla=cols_to_show,
    titulo_pagina="📊 Comparativa de Distribuciones de Tiempos",
    label_a="Distribución Actual (A)",
    label_b="Distribución Comparación (B)"
)
