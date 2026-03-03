import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanças Pro", layout="wide", page_icon="🏠")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"

# Login
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Login")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# Carregar Dados
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df_g = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
    except:
        df_g = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])
    try:
        df_r = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")
    except:
        df_r = pd.DataFrame(columns=["Data", "Origem", "Valor"])
    return df_g, df_r

df_gastos, df_receitas = get_data()

# Dashboard
st.title("📊 Resumo Financeiro")
t_gastos = df_gastos["Valor"].sum() if not df_gastos.empty else 0
t_receitas = df_receitas["Valor"].sum() if not df_receitas.empty else 0
saldo = t_receitas - t_gastos

c1, c2, c3 = st.columns(3)
c1.metric("Receitas", f"{t_receitas:.2f} €")
c2.metric("Despesas", f"-{t_gastos:.2f} €")
c3.metric("SALDO", f"{saldo:.2f} €")

if not df_gastos.empty:
    fig = px.pie(df_gastos, values="Valor", names="Categoria", title="Gastos por Categoria")
    st.plotly_chart(fig, use_container_width=True)
