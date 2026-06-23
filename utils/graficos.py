import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from utils.tablas import format_time

def histograma_tiempos_comp(s: pd.Series, title_text: str, color_main: str, color_light: str, color_dark: str, max_val_x: float = None, height: int = 355):
    """
    Genera un histograma + curva de densidad (KDE) interactivo.
    Acepta un max_val_x para alinear los ejes en comparaciones.
    """
    s = s.dropna()
    
    if len(s) < 2:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': title_text,
                'y': 0.95,
                'x': 0.05,
                'xanchor': 'left',
                'yanchor': 'top',
                'font': dict(size=20, color=color_dark)
            },
            template="plotly_white",
            annotations=[{
                "text": "Sin datos suficientes para calcular densidad",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16, "color": "#7F8C8D"}
            }]
        )
        return fig

    # Determinar el valor de corte del eje X
    if max_val_x is None:
        max_val = s.quantile(.97)
        if pd.isna(max_val) or max_val <= 0:
            max_val = s.max() if s.max() > 0 else 100
    else:
        max_val = max_val_x

    n_sample = min(len(s), 10_000)
    sample = s.sample(n_sample, random_state=42)

    try:
        kde = gaussian_kde(sample)
        # Rango de densidad concentrado en el área visible y extendido para el acumulado
        x_range = np.concatenate([
            np.linspace(0, max_val, 500), 
            np.linspace(max_val, sample.max(), 11)[1:]
        ])
        y_density = kde(x_range)
        
        # Calcular Población Acumulada usando la población entera (s)
        s_sorted = np.sort(s.values)
        y_cumulative = np.searchsorted(s_sorted, x_range, side='right') / len(s_sorted) * 100
    except Exception:
        # Fallback si KDE falla (e.g. varianza cero)
        x_range = np.linspace(0, max_val, 500)
        y_density = np.zeros_like(x_range)
        
        # Calcular Población Acumulada usando la población entera (s)
        s_sorted = np.sort(s.values)
        y_cumulative = np.searchsorted(s_sorted, x_range, side='right') / len(s_sorted) * 100

    tiempo_formateado = [format_time(seg) for seg in x_range]
    datos_hover = np.stack((y_cumulative, tiempo_formateado), axis=-1)

    fig = go.Figure()

    # Histograma (representación de probabilidad acumulada)
    fig.add_trace(go.Histogram(
        x=sample,
        name="Histograma",
        histnorm='probability density',
        xbins=dict(
            start=0,
            end=1.5 * max_val,
            size=max(int(max_val / 60), 1)
        ),
        marker_color=color_main,
        marker_line=dict(color=color_light, width=.6),
        opacity=0.35,
        hoverinfo="skip"
    ))

    # Curva de Densidad KDE
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_density,
        mode='lines',
        line=dict(color=color_main, width=2.5),
        name="Curva de Densidad",
        customdata=datos_hover, 
        hovertemplate=(
            "<b>Tiempo de Gestión:</b> %{customdata[1]}<br>" +
            "<b>Población Acumulada:</b> %{customdata[0]:.1f}%" +
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title={
            'text': title_text,
            'y': 0.95,
            'x': 0.02,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(size=22, color=color_dark)
        },
        template="plotly_white",
        bargap=0.05,
        showlegend=True,
        legend=dict(
            yanchor="top", 
            y=0.98,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.6)",
            bordercolor=color_light,
            borderwidth=.5,
            font=dict(size=14, color=color_dark)
        ),
        margin=dict(l=55, r=30, t=65, b=28),
        height=height,
        
        xaxis=dict(
            title=dict(text="Tiempo de Gestión (segundos)", font=dict(color='#566573', size=15), standoff=4),
            tickfont=dict(color='#566573', size=13),
            showgrid=True,
            zeroline=True,
            range=[0, max_val],
        ),

        yaxis=dict(
            title=dict(text="Densidad", font=dict(color='#566573', size=15), standoff=6),
            tickfont=dict(color='#566573', size=13),
            showgrid=True,
            gridcolor='#EBEDEF',
            zeroline=True
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=13, 
            font_color=color_dark,
            bordercolor=color_main, 
            namelength=0
        ),
    )

    return fig
