import numpy as np
import pandas as pd

def format_time(segundos):
    """
    Formatea segundos a un formato dinámico: 'Xh Ymin Zseg'
    Elimina las unidades que sean cero.
    """
    if segundos is None or pd.isna(segundos) or segundos <= 0:
        return "0seg"
    
    # Cálculos matemáticos
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    
    # Construcción de la cadena dinámica
    partes = []
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}min")
    if segs > 0 or not partes:
        partes.append(f"{segs}seg")
    
    return " ".join(partes)

def calcular_metricas_gestion(s: pd.Series):
    """
    Calcula métricas clave para una serie de tiempos de gestión.
    """
    s = s.dropna()
    cantidad = len(s)
    
    if cantidad == 0:
        return {
            "cantidad": "0",
            "promedio": "0seg",
            "mediana": "0seg",
            "p97": "0seg"
        }
        
    promedio = s.mean()
    mediana = s.median()
    
    # Percentil 97 de esta serie
    p97 = s.quantile(0.97)

    return {
        "cantidad": f"{cantidad:,}",
        "promedio": format_time(promedio),
        "mediana": format_time(mediana),
        "p97": format_time(p97)
    }

def tabla_extremos(df, cols, time_col="DuracionAudio", id_col="IdGestion", head=100):
    """
    Retorna las 100 gestiones más extremas (mayores al percentil 97 de la columna de tiempo)
    """
    if df.empty:
        return pd.DataFrame(columns=[c for c in cols if c != id_col])
        
    cota_extremo = df[time_col].quantile(.97)
    extremos = (
        df.loc[df[time_col] > cota_extremo, cols]
        .sort_values(time_col, ascending=False)
        .head(head)
    )
    if id_col in extremos.columns:
        extremos = extremos.set_index(id_col)
    return extremos
