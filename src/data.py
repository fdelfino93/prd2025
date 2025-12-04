from typing import Dict, List, Optional
import unicodedata
import pandas as pd
import pathlib
import streamlit as st

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
                if month_raw.isdigit():
                     month = int(month_raw)
                else:
                     month = MONTH_MAP.get(month_raw)

                if month is None:
                    return pd.NaT

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
