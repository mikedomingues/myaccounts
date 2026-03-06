import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registar Gastos", page_icon="💸")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💸 Novo Gasto")

# Carregar objetivos para garantir que a descrição coincide
try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
    lista_objetivos = df_obj["Nome"].tolist()
except:
    lista_objetivos = []

with st.form("form_gastos"):
    data = st.date_input("Data", datetime.now())
    
    # Se for crédito, sugerimos os nomes dos objetivos existentes
    categoria = st.selectbox("Categoria", ["Créditos", "Levantamentos", "Renda", "Extras", "Combustível", "Compras", "Outros"])
    
    if categoria == "Créditos" and lista_objetivos:
        descricao = st.selectbox("Selecione o Crédito (Descrição)", lista_objetivos)
    else:
        descricao = st.text_input("Descrição (Ex: Jantar, Pingo Doce)")
        
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Guardar Gasto e Atualizar Dívida")

    if submit and descricao and valor > 0:
        # 1. REGISTAR O GASTO NA FOLHA1
        tipo = "Fixo" if categoria in ["Créditos", "Renda"] else "Variável"
        df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
        nova_linha = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Descrição": descricao, "Categoria": categoria, "Valor": valor, "Tipo (Fixo/Variavel)": tipo}])
        conn.update(spreadsheet=URL_SHEET, worksheet="Folha1", data=pd.concat([df_gastos, nova_linha], ignore_index=True))

        # 2. ATUALIZAR O VALOR_ATUAL NO OBJETIVO (A MAGIA ACONTECE AQUI)
        if categoria == "Créditos" and descricao in lista_objetivos:
            idx = df_obj[df_obj["Nome"] == descricao].index[0]
            df_obj.at[idx, 'Valor_Atual'] += valor
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_obj)
            st.success(f"✅ Gasto registado e dívida de {descricao} abatida em {valor}€!")
        else:
            st.success("✅ Gasto registado com sucesso!")
        
        st.rerun()
