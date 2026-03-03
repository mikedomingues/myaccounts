import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Finanças Pro", layout="wide", page_icon="💰")

# --- LIGAÇÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Adicionamos um try/except para a app não crashar se a folha estiver vazia
    try:
        # Tenta ler a Folha1
        return conn.read(worksheet="Folha1", ttl="0s")
    except:
        # Se der erro, cria um DataFrame vazio com as tuas colunas
        return pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])

df = load_data()

# Se o DF vier com colunas vazias ou erro de leitura, garantimos os nomes certos
if df.empty:
    df = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])

# --- SIDEBAR (INPUT) ---
st.sidebar.header("📝 Registar Gasto")
with st.sidebar.form("entry_form"):
    data = st.date_input("Data", datetime.now())
    descricao = st.text_input("O que compraste?")
    categoria = st.selectbox("Categoria", [
        "Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco", 
        "Combustível", "Compras", "Almoço/Jantar Fora", "Outros"
    ])
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Guardar")

    if submit and descricao and valor > 0:
        tipo = "Fixo" if categoria in ["Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco"] else "Variável"
        
        # ATENÇÃO: Os nomes aqui têm de ser IGUAIS aos do teu Sheets (imagem)
        nova_linha = pd.DataFrame([{
            "Data": data.strftime("%d/%m/%Y"), 
            "Descrição": descricao, 
            "Categoria": categoria, 
            "Valor": valor, 
            "Tipo (Fixo/Variavel)": tipo
        }])
        
        updated_df = pd.concat([df, nova_linha], ignore_index=True)
        conn.update(worksheet="Folha1", data=updated_df)
        st.sidebar.success("Gravado!")
        st.rerun()
