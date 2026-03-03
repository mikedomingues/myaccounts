import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registar Gastos")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💸 Registar Novo Gasto")

with st.form("form_gastos"):
    data = st.date_input("Data", datetime.now())
    descricao = st.text_input("Descrição (Ex: Pingo Doce, Prestação Carro)")
    
    categorias = [
        "Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco", 
        "Combustível", "Compras", "Almoço/Jantar Fora", "Outros"
    ]
    categoria = st.selectbox("Categoria", categorias)
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Guardar Gasto")

    if submit and descricao and valor > 0:
        tipo = "Fixo" if categoria in ["Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco"] else "Variável"
        
        try:
            df_existente = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
        except:
            df_existente = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])
        
        nova_linha = pd.DataFrame([{
            "Data": data.strftime("%d/%m/%Y"), 
            "Descrição": descricao, 
            "Categoria": categoria, 
            "Valor": valor, 
            "Tipo (Fixo/Variavel)": tipo
        }])
        
        updated_df = pd.concat([df_existente, nova_linha], ignore_index=True)
        conn.update(spreadsheet=URL_SHEET, worksheet="Folha1", data=updated_df)
        st.success("Gasto registado na Folha1!")
