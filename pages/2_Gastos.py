import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registar Gastos", page_icon="💸")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💸 Novo Gasto")

# Carregar objetivos para a lista de seleção
try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
    lista_objetivos = df_obj["Nome"].tolist()
except:
    lista_objetivos = []

with st.form("form_gastos"):
    data = st.date_input("Data", datetime.now())
    
    # 1. Escolha da Categoria
    categoria = st.selectbox("Categoria", ["Créditos", "Levantamentos", "Renda", "Extras", "Combustível", "Compras", "Outros"])
    
    # 2. Lógica de Descrição Dinâmica
    # Se quiseres que Levantamentos também abatam na dívida, mantemos na lista. 
    # Se Levantamentos forem apenas dinheiro vivo, retira 'Levantamentos' da linha abaixo.
    if categoria in ["Créditos", "Levantamentos"] and lista_objetivos:
        descricao = st.selectbox("Selecione o Crédito/Objetivo para abater", lista_objetivos)
    else:
        descricao = st.text_input("Descrição do Gasto (Escrita livre)")
        
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Guardar Gasto e Atualizar Sistema")

    if submit:
        if descricao and valor > 0:
            # --- PARTE 1: Gravar na Folha1 ---
            tipo = "Fixo" if categoria in ["Créditos", "Renda"] else "Variável"
            
            try:
                df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
            except:
                df_gastos = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])
            
            nova_linha = pd.DataFrame([{
                "Data": data.strftime("%d/%m/%Y"), 
                "Descrição": descricao, 
                "Categoria": categoria, 
                "Valor": valor, 
                "Tipo (Fixo/Variavel)": tipo
            }])
            
            conn.update(spreadsheet=URL_SHEET, worksheet="Folha1", data=pd.concat([df_gastos, nova_linha], ignore_index=True))

            # --- PARTE 2: Abate Automático na Dívida ---
            # Só abate se o nome selecionado existir nos Objetivos
            if descricao in lista_objetivos:
                idx = df_obj[df_obj["Nome"] == descricao].index[0]
                # Somamos o valor pago ao que já tinha sido amortizado
                df_obj.at[idx, 'Valor_Atual'] = float(df_obj.at[idx, 'Valor_Atual']) + valor
                conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_obj)
                st.success(f"✅ Gasto de {valor}€ registado e dívida de '{descricao}' abatida!")
            else:
                st.success(f"✅ Gasto de '{descricao}' registado com sucesso!")
            
            st.rerun()
        else:
            st.error("Por favor, preenche a descrição/seleção e o valor.")
