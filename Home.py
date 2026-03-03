import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Finanças Pro", layout="wide", page_icon="💰")

# URL DIRETO DO TEU SHEETS (Confirmado)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"

# Ligação à base de dados
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Lemos a Folha1. ttl=0 força a atualização a cada refresh
        return conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
    except Exception as e:
        # Se a folha estiver vazia, cria a estrutura base
        return pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])

df = load_data()

# Se por algum motivo o DF vier mal formatado, corrigimos os nomes
if df.empty or "Valor" not in df.columns:
    df = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("📝 Novo Registo")
with st.sidebar.form("form_gastos"):
    data_input = st.date_input("Data", datetime.now())
    desc_input = st.text_input("Descrição")
    
    lista_categorias = [
        "Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco", 
        "Combustível", "Compras", "Almoço/Jantar Fora", "Outros"
    ]
    cat_input = st.selectbox("Categoria", lista_categorias)
    valor_input = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    
    submit = st.form_submit_button("Guardar no Sheets")

    if submit:
        if desc_input and valor_input > 0:
            # Lógica de Tipo
            tipo_input = "Fixo" if cat_input in ["Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco"] else "Variável"
            
            # Criar nova linha com nomes EXATOS das colunas da tua imagem
            nova_linha = pd.DataFrame([{
                "Data": data_input.strftime("%d/%m/%Y"),
                "Descrição": desc_input,
                "Categoria": cat_input,
                "Valor": valor_input,
                "Tipo (Fixo/Variavel)": tipo_input
            }])
            
            # Atualizar
            updated_df = pd.concat([df, nova_linha], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Folha1", data=updated_df)
            
            st.sidebar.success("✅ Guardado!")
            st.rerun()
        else:
            st.sidebar.warning("Preenche a descrição e o valor.")

# --- DASHBOARD ---
st.title("📊 Painel Financeiro")

if not df.empty:
    # Métricas principais
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Gasto", f"{df['Valor'].sum():.2f} €")
    with col2:
        fixos = df[df["Tipo (Fixo/Variavel)"] == "Fixo"]["Valor"].sum()
        st.metric("Custos Fixos", f"{fixos:.2f} €")

    st.divider()

    # Gráficos
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Gastos por Categoria")
        fig_pie = px.pie(df, values="Valor", names="Categoria", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.subheader("Histórico Recente")
        st.dataframe(df.tail(10), use_container_width=True)
else:
    st.info("Ainda não existem dados na Folha1. Faz o teu primeiro registo à esquerda!")
