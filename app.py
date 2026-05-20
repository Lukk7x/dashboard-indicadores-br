import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import yfinance as yf

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Indicadores Macro BR",
    page_icon="📈",
    layout="wide"
)

# ── Título principal ────────────────────────────────────────────────────────
st.title("📈 Indicadores Macroeconômicos Brasileiros")
st.caption("Fontes: Banco Central do Brasil (SGS/BCB) · ANBIMA · B3 via Yahoo Finance")

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filtros")

    grupo = st.radio("Grupo de indicador", ["Juros & Inflação (BCB)", "Mercado"])

    if grupo == "Juros & Inflação (BCB)":
        indicadores_bcb = {
            "CDI (% a.a.)": 4389,
            "SELIC Meta (% a.a.)": 432,
            "IPCA (% a.m.)": 433,
            "SELIC Efetiva (% a.a.)": 1178,
        }
        indicador_escolhido = st.selectbox("Indicador", list(indicadores_bcb.keys()))

    else:
        indicadores_mercado = {
            "Ibovespa": "^BVSP",
            "IMA-B (via ETF IMAB11)": "IMAB11.SA",
        }
        indicador_escolhido = st.selectbox("Indicador", list(indicadores_mercado.keys()))

    ano_inicio, ano_fim = st.slider(
        "Período", min_value=2010, max_value=2025, value=(2015, 2025)
    )

    tipo_grafico = st.radio("Tipo de gráfico", ["Linha", "Barras"])

# ── Funções de coleta ────────────────────────────────────────────────────────

@st.cache_data
def buscar_dados_bcb(codigo_serie: int, ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    blocos = []
    ano_atual = ano_inicio

    while ano_atual <= ano_fim:
        ano_bloco_fim = min(ano_atual + 2, ano_fim)
        url = (
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"
            f"?formato=json&dataInicial=01/01/{ano_atual}&dataFinal=31/12/{ano_bloco_fim}"
        )
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()

        if isinstance(dados, list) and len(dados) > 0:
            blocos.append(pd.DataFrame(dados))

        ano_atual += 3

    if not blocos:
        st.error("Não foi possível obter dados para esse indicador e período.")
        st.stop()

    df = pd.concat(blocos, ignore_index=True)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna().drop_duplicates(subset="data").sort_values("data")
    return df


@st.cache_data
def buscar_dados_mercado(ticker: str, ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    dados = yf.download(
        ticker,
        start=f"{ano_inicio}-01-01",
        end=f"{ano_fim}-12-31",
        progress=False
    )

    if dados.empty:
        st.error("Não foi possível obter dados para esse indicador e período.")
        st.stop()

    df = dados[["Close"]].reset_index()
    df.columns = ["data", "valor"]
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna()
    return df

# ── Busca os dados conforme o grupo selecionado ──────────────────────────────
with st.spinner("Buscando dados..."):
    if grupo == "Juros & Inflação (BCB)":
        codigo = indicadores_bcb[indicador_escolhido]
        df = buscar_dados_bcb(codigo, ano_inicio, ano_fim)
        unidade = "%"
    else:
        ticker = indicadores_mercado[indicador_escolhido]
        df = buscar_dados_mercado(ticker, ano_inicio, ano_fim)
        unidade = "pts" if indicador_escolhido == "Ibovespa" else "R$"

# ── Cards de métricas ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Último valor", f"{df['valor'].iloc[-1]:,.2f} {unidade}")
col2.metric("Média do período", f"{df['valor'].mean():,.2f} {unidade}")
col3.metric("Máximo", f"{df['valor'].max():,.2f} {unidade}")
col4.metric("Mínimo", f"{df['valor'].min():,.2f} {unidade}")

st.divider()

# ── Gráfico principal ────────────────────────────────────────────────────────
if tipo_grafico == "Linha":
    fig = px.line(df, x="data", y="valor", title=indicador_escolhido)
else:
    fig = px.bar(df, x="data", y="valor", title=indicador_escolhido)

fig.update_layout(xaxis_title="Data", yaxis_title=f"Valor ({unidade})")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Tabela e exportação ──────────────────────────────────────────────────────
st.subheader("📋 Dados brutos")
st.dataframe(df, use_container_width=True)
st.download_button(
    label="⬇️ Baixar CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"{indicador_escolhido.replace(' ', '_')}.csv",
    mime="text/csv",
)