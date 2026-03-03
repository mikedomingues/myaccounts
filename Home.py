import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestor Financeiro", layout="wide")

st.title("💰 O Meu Gestor de Finanças")

# URL do teu Google Sheet (substitui pelo teu link real)
# Lembra-te: O Sheets deve estar "Partilhado com qualquer pessoa com o link"
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"

# Estabelecer ligação
conn = st.connection("gsheets", type=GSheetsConnection)

# Ler os dados existentes
try:
    df = conn.read(spreadsheet=URL_SHEET)
    st.success("Ligação à Base de Dados estabelecida!")
    
    # Mostrar um resumo rápido
    if not df.empty:
        st.subheader("Últimos Registos")
        st.dataframe(df.tail(10)) # Mostra os últimos 10 gastos
    else:
        st.info("A tua folha de cálculo ainda está vazia. Começa a preencher!")

except Exception as e:
    st.error(f"Erro ao ligar ao Google Sheets: {e}")

# --- Espaço para o Futuro Formulário ---
st.divider()
st.info("Próximo passo: Vamos criar o formulário para inserires os teus créditos (Wizink, Universo, etc.) e gastos diários.")
