import pandas as pd
import pytest
from src.data import normalize_text, classify_risk, parse_dates

def test_normalize_text():
    assert normalize_text("São Paulo") == "SAO PAULO"
    assert normalize_text("  ç  ") == "C"
    assert normalize_text("áéíóú") == "AEIOU"
    assert normalize_text(123) == ""

def test_classify_risk():
    s = pd.Series([10, 20, 30, 40, 50])
    # Quantiles: 0.25=20, 0.5=30, 0.75=40
    # 10 <= 20 -> Baixo
    # 20 <= 20 -> Baixo
    # 30 <= 30 -> Medio
    # 40 <= 40 -> Alto
    # 50 > 40 -> Critico
    result = classify_risk(s)
    expected = ["Baixo", "Baixo", "Medio", "Alto", "Critico"]
    assert result.tolist() == expected

def test_classify_risk_empty():
    assert classify_risk(pd.Series([])).empty

def test_parse_dates_column():
    df = pd.DataFrame({"Data": ["2021-01-01", "invalid"]})
    df = parse_dates(df)
    assert df["Data"].iloc[0] == pd.Timestamp("2021-01-01")
    assert pd.isna(df["Data"].iloc[1])

def test_parse_dates_columns():
    df = pd.DataFrame({
        "Ano": [2021, 2021],
        "Mes": ["jan", "fev"],
        "Dia": [1, 2]
    })
    df = parse_dates(df)
    assert df["Data"].iloc[0] == pd.Timestamp("2021-01-01")
    assert df["Data"].iloc[1] == pd.Timestamp("2021-02-02")
