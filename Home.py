import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Finanças Pro", layout="wide", page_icon="🏠")

# URL do teu Sheets
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"

# --- SISTEMA DE LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Login - Gestor Financeiro")
    senha = st.text_input("Introduza a senha para aceder", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

# --- CONEXÃO E DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        # Gastos (Folha1)
        df_g = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
    except:
        df_g = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])
    
    try:
        # Recebimentos
        df_r = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")
    except:
        df_r = pd.DataFrame(columns=["Data", "Origem", "Valor"])
    
    return df_g, df_r

df_gastos, df_receitas = get_data()

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Resumo Financeiro")

# Cálculos Totais
t_gastos = df_gastos["Valor"].sum() if not df_gastos.empty else 0
t_receitas = df_receitas["Valor"].sum() if not df_receitas.empty else 0
saldo = t_receitas - t_gastos

# Métricas em colunas
c1, c2, c3 = st.columns(3)
c1.metric("Receitas (Entradas)", f"{t_receitas:.2f} €")
c2.metric("Despesas (Saídas)", f"-{t_gastos:.2f} €")
c3.metric("SALDO ATUAL", f"{saldo:.2f} €", delta="Disponível", delta_color="normal" if saldo >= 0 else "inverse")

st.divider()

# --- GRÁFICOS E ANÁLISE ---
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("Distribuição por Categoria")
    if not df_gastos.empty:
        fig = px.pie(df_gastos, values="Valor", names="Categoria", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ainda não existem gastos registados.")

with col_dir:
    st.subheader("💡 Sugestões de Poupança")
    if saldo < 0:
        st.error("🚨 Estás com saldo negativo! Revisa os teus gastos em 'Extras' e 'Outros'.")
    elif saldo > 0 and t_receitas > 0:
        st.success(f"🟢 Tens {saldo:.2f} € de saldo. Dica: Coloca uma parte no fundo de emergência.")
    
    # Alerta específico para Créditos
    total_creditos = df_gastos[df_gastos["Categoria"] == "Créditos"]["Valor"].sum()
    if total_creditos > 0:
        st.warning(f"💳 Este mês já pagaste {total_creditos:.2f} € em Créditos.")

# --- EXPLORAÇÃO DE "EXTRAS" (Onde foi gasto) ---
st.divider()
st.subheader("🔍 Detalhe da Categoria: Extras")

df_extras = df_gastos[df_gastos["Categoria"] == "Extras"]

if not df_extras.empty:
    st.write("Aqui podes ver exatamente em que foram gastos os teus Extras:")
    st.dataframe(df_extras[["Data", "Descrição", "Valor"]].sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Nenhum gasto registado como 'Extras' até ao momento.")

# --- HISTÓRICO GERAL ---
with st.expander("Ver todos os gastos registados"):
    st.dataframe(df_gastos, use_container_width=True)

# Botão para atualizar
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()
