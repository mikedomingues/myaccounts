import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Finanças Pro", layout="wide", page_icon="💰")

# URL DIRETO DO TEU SHEETS
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"

# Estabelecer ligação usando os Secrets (JSON) que configuraste
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Lemos a Folha1. O ttl=0 garante que vemos os dados novos mal gravamos
        return conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
    except Exception as e:
        st.error(f"Erro ao ler o Sheets: {e}")
        return pd.DataFrame()

df = load_data()

# --- SIDEBAR: REGISTO DE GASTOS ---
st.sidebar.header("📝 Novo Registo")
with st.sidebar.form("form_gastos"):
    data_
