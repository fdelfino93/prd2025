import pathlib
import streamlit as st
import pandas as pd
import plotly.express as px

from src.data import load_csv, preprocess, classify_risk
from src.map import load_geojson, build_map
from src.ui import filters_ui, apply_filters, sidebar_data_source

st.set_page_config(
    page_title="Mapa de Criminalidade - Curitiba",
    page_icon="🗺️",
    layout="wide",
)

DATA_PATH = pathlib.Path("data")
DEFAULT_CSV = DATA_PATH / "crimes.csv"
DEFAULT_GEOJSON = DATA_PATH / "bairros_curitiba.geojson"

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
