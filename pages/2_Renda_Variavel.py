import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

# ── Configuração ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Renda Variável BR",
    page_icon="💹",
    layout="wide"
)

st.title("💹 Análise de Ações — Renda Variável")
st.caption("Dados históricos via Yahoo Finance · Bolsa brasileira (B3)")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filtros")

    # Oferecemos blue chips pré-definidas mas também permitimos que o usuário
    # digite qualquer ticker. Isso torna o app muito mais versátil — qualquer
    # ação da B3 pode ser analisada, não só as que listamos aqui.
    blue_chips = {
        "Itaú Unibanco (ITUB4)": "ITUB4.SA",
        "Petrobras (PETR4)": "PETR4.SA",
        "Vale (VALE3)": "VALE3.SA",
        "Bradesco (BBDC4)": "BBDC4.SA",
        "B3 (B3SA3)": "B3SA3.SA",
        "Nubank (ROXO34 BDR)": "ROXO34.SA",
        "XP Inc (XPBR31 BDR)": "XPBR31.SA",
        "Outro (digitar ticker)": "custom",
    }

    ativo_selecionado = st.selectbox("Ativo", list(blue_chips.keys()))

    # Se o usuário escolher "Outro", aparece um campo de texto livre
    if blue_chips[ativo_selecionado] == "custom":
        ticker_custom = st.text_input(
            "Digite o ticker",
            placeholder="Ex: WEGE3 ou WEGE3.SA"
        ).upper().strip()

        # Adiciona .SA automaticamente se o usuário não incluir
        if ticker_custom and not ticker_custom.endswith(".SA"):
            ticker = ticker_custom + ".SA"
        else:
            ticker = ticker_custom

        if ticker:
            st.caption(f"Buscando dados para: `{ticker}`")
    else:
        ticker = blue_chips[ativo_selecionado]

    ano_inicio, ano_fim = st.slider(
        "Período", min_value=2010, max_value=2025, value=(2018, 2025)
    )

# ── Coleta de dados ──────────────────────────────────────────────────────────
@st.cache_data
def buscar_acao(ticker: str, ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    dados = yf.download(
        ticker,
        start=f"{ano_inicio}-01-01",
        end=f"{ano_fim}-12-31",
        progress=False
    )

    if dados.empty:
        return pd.DataFrame()

    # Trazemos Close e Volume juntos. O volume é importante em análise
    # técnica — ele confirma (ou questiona) a força de um movimento de preço.
    df = dados[["Close", "Volume"]].reset_index()
    df.columns = ["data", "preco", "volume"]
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    df = df.dropna()
    return df

# Só tenta buscar se houver um ticker definido
if not ticker:
    st.info("Selecione um ativo ou digite um ticker na barra lateral para começar.")
    st.stop()

with st.spinner(f"Buscando dados de {ticker}..."):
    df = buscar_acao(ticker, ano_inicio, ano_fim)

if df.empty:
    st.error(f"Nenhum dado encontrado para o ticker '{ticker}'. Verifique se está correto.")
    st.stop()

# ── Cards de métricas ────────────────────────────────────────────────────────
preco_atual = df["preco"].iloc[-1]
preco_inicio = df["preco"].iloc[0]

# Calculamos a variação percentual total do período — muito mais informativo
# do que apenas mostrar o preço atual, porque contextualiza a performance.
variacao_total = ((preco_atual - preco_inicio) / preco_inicio) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Preço atual", f"R$ {preco_atual:,.2f}")
col2.metric("Variação no período", f"{variacao_total:+.2f}%")
col3.metric("Máximo histórico", f"R$ {df['preco'].max():,.2f}")
col4.metric("Mínimo histórico", f"R$ {df['preco'].min():,.2f}")

st.divider()

# ── Gráfico de preço + volume ────────────────────────────────────────────────
# Usamos make_subplots para empilhar dois gráficos no mesmo espaço:
# o preço em cima e o volume embaixo. Isso é padrão em plataformas
# financeiras como o TradingView — o recrutador vai reconhecer esse padrão.
fig = go.Figure()

fig = go.Figure(go.Scatter(
    x=df["data"],
    y=df["preco"],
    mode="lines",
    name="Preço (R$)",
    line=dict(color="#00b4d8", width=1.5)
))

fig.update_layout(
    title=f"Histórico de Preço — {ticker}",
    xaxis_title="Data",
    yaxis_title="Preço (R$)",
    hovermode="x unified"  # mostra todos os valores ao passar o mouse numa data
)

st.plotly_chart(fig, use_container_width=True)

# Gráfico de volume separado, logo abaixo do de preço
fig_volume = px.bar(
    df, x="data", y="volume",
    title="Volume Negociado",
    color_discrete_sequence=["#48cae4"]
)
fig_volume.update_layout(xaxis_title="Data", yaxis_title="Volume")
st.plotly_chart(fig_volume, use_container_width=True)

st.divider()

# ── Tabela e exportação ──────────────────────────────────────────────────────
st.subheader("📋 Dados brutos")
st.dataframe(df, use_container_width=True)
st.download_button(
    label="⬇️ Baixar CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"{ticker}_{ano_inicio}_{ano_fim}.csv",
    mime="text/csv",
)