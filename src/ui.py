import streamlit as st
import pandas as pd

def filters_ui(df: pd.DataFrame):
    st.sidebar.header("Filtros")
    naturezas = sorted(df["Natureza"].unique()) if "Natureza" in df else []
    naturezas_sel = st.sidebar.multiselect("Tipo de crime", options=naturezas, default=naturezas)

    bairros = sorted(df["Bairro"].unique()) if "Bairro" in df else []
    bairro_sel = st.sidebar.multiselect("Bairros", options=bairros, default=bairros)

    if df["Data"].notna().any():
        min_date = df["Data"].min()
        max_date = df["Data"].max()
        start, end = st.sidebar.date_input(
            "Periodo",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    else:
        start = end = None

    return naturezas_sel, bairro_sel, start, end

def apply_filters(df: pd.DataFrame, naturezas, bairros, start, end):
    if naturezas:
        df = df[df["Natureza"].isin(naturezas)]
    if bairros:
        df = df[df["Bairro"].isin(bairros)]
    if start and end:
        df = df[(df["Data"] >= pd.to_datetime(start)) & (df["Data"] <= pd.to_datetime(end))]
    return df

def sidebar_data_source():
    st.sidebar.header("Dados")
    uploaded = st.sidebar.file_uploader("Suba um CSV", type=["csv"])
    source = "upload" if uploaded else "default"
    return uploaded, source
