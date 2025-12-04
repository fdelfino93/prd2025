PRD – Plataforma de Análise de Criminalidade por Bairros de Curitiba
1. Visão Geral do Projeto

Criar um sistema em Python com visualização em Streamlit para analisar dados oficiais de criminalidade da cidade de Curitiba – PR, usando um arquivo CSV público do governo.
O sistema vai tratar os dados com Pandas, cruzar com dados geográficos via GeoPandas e exibir um mapa interativo por bairro, destacando o perfil de risco criminal de cada região.

Ou seja: transformar planilha feia em mapa bonito que até diretor entende.

2. Objetivo do Projeto

Entregar uma ferramenta visual que permita:

Entender quais bairros são mais perigosos

Ver a concentração de crimes no mapa

Analisar tipos de crime por região

Apoiar estudos, reportagens, decisões públicas e análises acadêmicas

Sem achismo, só dado.

3. Público-Alvo

Estudantes

Pesquisadores

Jornalistas

Analistas de dados

Gestores públicos

Curiosos que gostam de ver o caos organizado em gráficos

4. Fonte de Dados

Arquivo CSV oficial disponibilizado no site do governo

Dados típicos esperados:

Tipo de crime

Data

Bairro

Latitude/Longitude (se houver)

Delegacia ou região

Natureza da ocorrência

5. Stack Tecnológica

Python 3.x

Pandas → Tratamento dos dados

GeoPandas → Geoprocessamento e mapas

Streamlit → Front-end web interativo

Matplotlib / Plotly / Folium → Visualizações

Arquivos GeoJSON/Shapefile → Mapa dos bairros de Curitiba

Nada de frescura com framework pesado. Leve, rápido e direto.

6. Funcionalidades Principais
6.1 Upload e Leitura de Dados

Upload do arquivo .csv

Validação automática de colunas obrigatórias

Aviso se o arquivo estiver errado (porque vai estar)

6.2 Tratamento e Limpeza dos Dados

Remoção de valores nulos

Padronização de nomes de bairros

Conversão de datas

Agrupamento por:

Bairro

Tipo de crime

Período

6.3 Integração com Mapa

Carregar o mapa oficial dos bairros de Curitiba

Cruzar os dados do CSV com o GeoJSON

Gerar camadas por:

Quantidade de crimes

Tipo de crime

Período

6.4 Visualização no Streamlit

Mapa interativo por bairro

Filtro por:

Tipo de crime

Data / Período

Bairro específico

Gráficos:

Crimes por bairro

Crimes por tipo

Evolução temporal

Tabela dinâmica dos dados tratados

6.5 Perfil de Risco por Bairro

Cada bairro receberá:

Classificação: Baixo, Médio, Alto, Crítico

Baseado em:

Quantidade de ocorrências

Frequência

Tipos de crime

Basicamente: um “termômetro do caos”.

7. Requisitos Funcionais

O sistema deve aceitar arquivos .csv

O sistema deve tratar dados automaticamente

O sistema deve exibir mapa interativo

O sistema deve permitir filtros por bairro, período e tipo de crime

O sistema deve gerar gráficos estatísticos

O sistema deve classificar o risco de cada bairro

8. Requisitos Não Funcionais

Interface simples (sem frufru)

Execução rápida

Código documentado

Possibilidade de rodar localmente

Fácil atualização quando sair novo CSV

9. Arquitetura Resumida

Usuário faz upload do CSV

Pandas trata os dados

GeoPandas cruza com o mapa dos bairros

Streamlit exibe:

Mapa

Gráficos

Tabelas

Sistema gera o perfil de risco automaticamente

Fluxo simples, igual receita de miojo.

10. Indicadores de Sucesso

Dados exibidos corretamente no mapa

Filtros funcionando sem quebrar

Classificação de risco gerada automaticamente

Visualização clara e interpretável

Possibilidade de atualização com novos dados

11. Riscos do Projeto

CSV vir todo cagado (alta probabilidade)

Bairros com nomes divergentes

Falta de latitude/longitude

Dados incompletos do governo (surpresa zero)

12. Entregáveis

Script Python completo

Aplicação Streamlit funcional

Documentação de uso

Mapa interativo por bairros

Dashboard com gráficos

Classificação de risco por bairro

13. Evoluções Futuras (quando alguém liberar verba)

Histórico comparativo entre anos

Previsão de criminalidade por bairro (ML)

API pública para consumo dos dados

Hospedagem online

Integração com dados meteorológicos ou socioeconômicos