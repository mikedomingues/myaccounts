import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registar Gastos", page_icon="💸")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💸 Novo Gasto")

with st.form("form_gastos"):
    data = st.date_input("Data", datetime.now())
    # A Descrição é essencial, especialmente para a categoria 'Extras'
    descricao = st.text_input("Descrição (Ex: Jantar fora, Concerto, Pingo Doce)")
    
    # Novas categorias simplificadas
    categorias = [
        "Créditos", 
        "Levantamentos", 
        "Renda", 
        "Extras", 
        "Combustível", 
        "Compras", 
        "Outros"
    ]
    categoria = st.selectbox("Categoria", categorias)
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    
    submit = st.form_submit_button("Guardar Gasto")

    if submit:
        if descricao and valor > 0:
            # Definimos o Tipo automaticamente para análise posterior
            tipo = "Fixo" if categoria in ["Créditos", "Renda"] else "Variável"
            
            df_old = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
            
            nova_linha = pd.DataFrame([{
                "Data": data.strftime("%d/%m/%Y"), 
                "Descrição": descricao, 
                "Categoria": categoria, 
                "Valor": valor, 
                "Tipo (Fixo/Variavel)": tipo
            }])
            
            updated_df = pd.concat([df_old, nova_linha], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Folha1", data=updated_df)
            st.success(f"Registado: {categoria} ({descricao})")
        else:
            st.warning("Preenche a descrição e o valor.")
