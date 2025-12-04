# Plataforma de Analise de Criminalidade - Curitiba

Aplicacao Streamlit que transforma o CSV oficial de criminalidade em visualizacoes por bairro de Curitiba.

## Requisitos

- Python 3.10+
- Bibliotecas em `requirements.txt`

Instale dependencias:

```bash
pip install -r requirements.txt
```

## Dados necessarios

- `data/crimes.csv`: CSV de entrada (sep `;`). Ja deixei uma copia do arquivo atual.
- `data/bairros_curitiba.geojson`: mapa oficial dos bairros de Curitiba. Baixe o GeoJSON do site do IBGE/PMC e coloque aqui.

## Como rodar

```bash
streamlit run app.py
```

Abra o link local que o Streamlit mostrar.

## Uso

1. Suba um novo CSV ou use o `data/crimes.csv` padrao.
2. Aplique filtros (tipo, bairros, periodo) na barra lateral.
3. Veja o mapa de risco por bairro, graficos de distribuicao e a tabela filtrada.
4. Baixe o CSV tratado pelo botao de download.

## Observacoes

- Se o GeoJSON nao estiver presente, o app segue sem o mapa.
- Se os nomes dos bairros divergirem, ajuste o GeoJSON ou padronize o CSV (o app normaliza acentos/espacos/caixa).
- Classificacao de risco usa quantis (Baixo/Medio/Alto/Critico) baseada no volume de ocorrencias filtrado.
