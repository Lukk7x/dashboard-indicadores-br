# 📈 Dashboard de Indicadores Financeiros Brasileiros

Aplicação web interativa para visualização de indicadores do mercado financeiro brasileiro, construída com Python e Streamlit.

🔗 **[Acesse o app ao vivo aqui](URL_DO_APP)** ← vamos atualizar esse link após publicar

---

## 📊 Funcionalidades

### Página 1 — Indicadores Macroeconômicos
- CDI, SELIC Meta, SELIC Efetiva e IPCA com dados históricos desde 2010
- Fonte: API pública do Banco Central do Brasil (SGS/BCB)
- Filtro de período interativo
- Gráfico de linha ou barras
- Cards com último valor, média, máximo e mínimo do período
- Exportação dos dados em CSV

### Página 2 — Renda Variável
- Histórico de preços e volume de ações da B3
- Blue chips pré-selecionadas: Itaú (ITUB4), Petrobras (PETR4), Vale (VALE3), Bradesco (BBDC4), B3 (B3SA3)
- Campo livre para buscar qualquer ativo pelo ticker (ex: WEGE3, MGLU3)
- Fonte: Yahoo Finance via yfinance
- Variação percentual total do período selecionado

---

## 🛠️ Stack

| Tecnologia | Uso |
|---|---|
| Python 3.13 | Linguagem principal |
| Streamlit | Framework web e interface |
| Plotly | Visualizações interativas |
| pandas | Manipulação de dados |
| yfinance | Dados de ações via Yahoo Finance |
| API BCB (SGS) | Dados macroeconômicos oficiais |

---

## 🚀 Como rodar localmente

```bash
# Clone o repositório
git clone https://github.com/Lukk7x/dashboard-indicadores-br.git
cd dashboard-indicadores-br

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Rode o app
streamlit run app.py
```

---

## 📁 Estrutura do projeto

---

## 👤 Autor

**Lucas Abreu**  
[LinkedIn](https://linkedin.com/in/lucas-vieira7x) · [GitHub](https://github.com/Lukk7x)  
Engenheiro de Computação · Pós-graduando em Ciência de Dados para o Mercado Financeiro (XP Educação)