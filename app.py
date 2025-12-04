import json
import pathlib
import unicodedata
from typing import Dict, Optional

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Mapa de Criminalidade - Curitiba",
    page_icon="🗺️",
    layout="wide",
)

DATA_PATH = pathlib.Path("data")
DEFAULT_CSV = DATA_PATH / "crimes.csv"
DEFAULT_GEOJSON = DATA_PATH / "bairros_curitiba.geojson"
MONTH_MAP = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}


def normalize_text(value: str) -> str:
    """Remove acentos, normaliza espacos e caixa."""
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ASCII", "ignore").decode("ASCII")
    return " ".join(ascii_only.upper().strip().split())


@st.cache_data(show_spinner=False)
def load_csv(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer, sep=";", dtype=str, encoding_errors="ignore")
    df.columns = [col.strip() for col in df.columns]
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping: Dict[str, str] = {
        "Ano": "Ano",
        "AISP": "AISP",
        "Municipio": "Municipio",
        "Munic¡pio": "Municipio",
        "MUNICIPIO": "Municipio",
        "Bairro": "Bairro",
        "BAIRRO": "Bairro",
        "Natureza": "Natureza",
        "NATUREZA": "Natureza",
        "Mês": "Mes",
        "Mes": "Mes",
        "Mˆs": "Mes",
        "Dia": "Dia",
        "Dia da Semana": "DiaSemana",
        "Hora": "Hora",
        "Data": "Data",
    }
    renamed = {}
    for col in df.columns:
        renamed[col] = mapping.get(col, col)
    return df.rename(columns=renamed)


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        return df

    if {"Ano", "Mes", "Dia"}.issubset(df.columns):
        def _parse_row(row):
            ano = row.get("Ano")
            mes = row.get("Mes")
            dia = row.get("Dia")
            if pd.isna(ano) or pd.isna(mes) or pd.isna(dia):
                return pd.NaT
            try:
                month_raw = str(mes).strip().lower()[:3]
                month = MONTH_MAP.get(month_raw, int(month_raw))
                return pd.to_datetime(f"{int(ano)}-{int(month):02d}-{int(dia):02d}")
            except Exception:
                return pd.NaT

        df["Data"] = df.apply(_parse_row, axis=1)
    else:
        df["Data"] = pd.NaT
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = rename_columns(df)
    df = parse_dates(df)
    for col in ["Bairro", "Natureza", "Municipio", "DiaSemana", "Hora"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
    df["Bairro_norm"] = df.get("Bairro", "").apply(normalize_text)
    df = df[df["Bairro_norm"] != ""]
    return df


@st.cache_data(show_spinner=False)
def load_geojson(path: pathlib.Path) -> Optional[gpd.GeoDataFrame]:
    if not path.exists():
        return None
    return gpd.read_file(path)


def infer_bairro_column(gdf: gpd.GeoDataFrame) -> str:
    candidates = [c for c in gdf.columns if "bairro" in c.lower() or "nome" in c.lower()]
    return candidates[0] if candidates else gdf.columns[0]


def classify_risk(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype=str)
    quantiles = series.quantile([0.25, 0.5, 0.75]).to_dict()

    def label(value: float) -> str:
        if value <= quantiles.get(0.25, value):
            return "Baixo"
        if value <= quantiles.get(0.5, value):
            return "Medio"
        if value <= quantiles.get(0.75, value):
            return "Alto"
        return "Critico"

    return series.apply(label)


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


def main():
    st.title("Mapa de Criminalidade por Bairro - Curitiba")
    st.caption("CSV oficial + GeoJSON de bairros = mapa rapido e filtravel")

    uploaded, source = sidebar_data_source()
    if uploaded:
        raw_df = load_csv(uploaded)
    elif DEFAULT_CSV.exists():
        raw_df = load_csv(DEFAULT_CSV)
    else:
        st.warning("Nenhum CSV encontrado. Envie um arquivo para começar.")
        return

    df = preprocess(raw_df)
    if df.empty:
        st.warning("Dados vazios apos limpeza. Confira colunas Bairro/Natureza/ano.")
        return

    naturezas_sel, bairros_sel, start, end = filters_ui(df)
    filtered = apply_filters(df, naturezas_sel, bairros_sel, start, end)

    total = int(filtered.shape[0])
    bairros_count = filtered["Bairro_norm"].nunique()
    period_label = "Dados sem data" if filtered["Data"].isna().all() else f"{filtered['Data'].min().date()} a {filtered['Data'].max().date()}"

    col1, col2, col3 = st.columns(3)
    col1.metric("Ocorrencias", f"{total:,}".replace(",", "."))
    col2.metric("Bairros", bairros_count)
    col3.metric("Periodo", period_label)

    resumo = (
        filtered.groupby(["Bairro_norm", "Bairro"])
        .agg(total_crimes=("Natureza", "size"), tipos=("Natureza", "nunique"))
        .reset_index()
    )
    resumo["risco"] = classify_risk(resumo["total_crimes"])

    gdf = load_geojson(DEFAULT_GEOJSON)
    if gdf is not None:
        try:
            fig = build_map(gdf, resumo)
            st.subheader("Mapa por risco")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.error(f"Erro ao gerar mapa: {exc}")
            st.info("Verifique se o GeoJSON tem o nome do bairro em alguma coluna (ex: nome, bairro).")
    else:
        st.info("GeoJSON de bairros nao encontrado em data/bairros_curitiba.geojson. Mapa desabilitado.")

    st.subheader("Crimes por bairro")
    if not resumo.empty:
        top_bairros = resumo.sort_values("total_crimes", ascending=False).head(15)
        fig_bar = px.bar(top_bairros, x="Bairro", y="total_crimes", color="risco", title="Top 15 bairros")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("Sem dados para agrupar.")

    st.subheader("Crimes por tipo")
    tipos = (
        filtered.groupby("Natureza")
        .size()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
    )
    if not tipos.empty:
        fig_tipo = px.bar(tipos.head(20), x="Natureza", y="total")
        st.plotly_chart(fig_tipo, use_container_width=True)
    else:
        st.write("Sem dados para tipos.")

    st.subheader("Evolucao temporal")
    if filtered["Data"].notna().any():
        timeline = filtered.copy()
        timeline["MesAno"] = timeline["Data"].dt.to_period("M").dt.to_timestamp()
        serie = timeline.groupby("MesAno").size().reset_index(name="total")
        fig_time = px.line(serie, x="MesAno", y="total")
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.write("Sem datas parsadas para mostrar linha do tempo.")

    st.subheader("Tabela filtrada")
    st.dataframe(filtered)

    csv_buffer = filtered.to_csv(index=False, sep=";")
    st.download_button(
        "Baixar CSV tratado",
        data=csv_buffer,
        file_name="crimes_tratado.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
