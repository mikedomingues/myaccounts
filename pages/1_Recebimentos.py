import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registar Recebimentos")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💰 Registar Entrada de Dinheiro")

with st.form("form_recebimentos"):
    data = st.date_input("Data", datetime.now())
    origem = st.selectbox("Origem", ["Salário", "Subsídio", "Venda OLX", "Reembolso", "Outros"])
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Guardar Recebimento")

    if submit and valor > 0:
        # Tenta ler dados existentes na aba Recebimentos
        try:
            df_existente = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")
        except:
            df_existente = pd.DataFrame(columns=["Data", "Origem", "Valor"])
        
        nova_linha = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Origem": origem, "Valor": valor}])
        updated_df = pd.concat([df_existente, nova_linha], ignore_index=True)
        
        conn.update(spreadsheet=URL_SHEET, worksheet="Recebimentos", data=updated_df)
        st.success("Recebimento guardado com sucesso!")
