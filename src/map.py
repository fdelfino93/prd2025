import json
import pathlib
from typing import Optional
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from .data import normalize_text

@st.cache_data(show_spinner=False)
def load_geojson(path: pathlib.Path) -> Optional[gpd.GeoDataFrame]:
    if not path.exists():
        return None
    return gpd.read_file(path)

def infer_bairro_column(gdf: gpd.GeoDataFrame) -> str:
    candidates = [c for c in gdf.columns if "bairro" in c.lower() or "nome" in c.lower()]
    return candidates[0] if candidates else gdf.columns[0]

def build_map(gdf: gpd.GeoDataFrame, resumo: pd.DataFrame):
    bairro_col = infer_bairro_column(gdf)
    gdf = gdf.copy()
    gdf["Bairro_norm"] = gdf[bairro_col].apply(normalize_text)
    merged = gdf.merge(resumo, on="Bairro_norm", how="left")
    merged["total_crimes"] = merged["total_crimes"].fillna(0)
    merged["risco"] = merged["risco"].fillna("Sem dados")

    geojson = json.loads(merged.to_json())
    fig = px.choropleth_mapbox(
        merged,
        geojson=geojson,
        locations=merged.index,
        color="risco",
        hover_name=bairro_col,
        hover_data={"total_crimes": True, "risco": True},
        mapbox_style="carto-positron",
        center={"lat": -25.4284, "lon": -49.2733},
        zoom=10,
        opacity=0.7,
        color_discrete_map={
            "Baixo": "#6abf69",
            "Medio": "#f7d154",
            "Alto": "#f28e2c",
            "Critico": "#d7263d",
            "Sem dados": "#cccccc",
        },
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig
