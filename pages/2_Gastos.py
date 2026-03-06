import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registar Gastos", page_icon="💸")

# Ligação ao Sheets
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💸 Registar Novo Gasto")

# Carregar os nomes dos créditos que tens na aba Objetivos
try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
    lista_creditos = df_obj[df_obj["Tipo"] == "Crédito"]["Nome"].tolist()
except:
    lista_creditos = []

# --- INTERFACE DINÂMICA ---

data = st.date_input("Data", datetime.now())

# 1. Seleção da Categoria (Fora de form para atualizar a página na hora)
categoria = st.selectbox(
    "Categoria", 
    ["Compras", "Extras", "Créditos", "Levantamentos", "Renda", "Combustível", "Outros"]
)

# 2. Lógica Condicional da Descrição
if categoria == "Créditos":
    # Se for Crédito, mostra a lista de nomes que estão nos Objetivos
    if lista_creditos:
        descricao = st.selectbox("Qual é o crédito a abater?", lista_creditos)
    else:
        st.warning("⚠️ Não encontrámos créditos criados na página de Objetivos.")
        descricao = st.text_input("Descrição (Escrita livre)")
else:
    # Para todas as outras categorias, aparece a caixa de texto normal
    descricao = st.text_input("Descrição (Escrita livre)", placeholder="Ex: Pingo Doce, Jantar fora...")

valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")

# --- BOTÃO DE GUARDAR ---
if st.button("Confirmar e Guardar Gasto"):
    if descricao and valor > 0:
        # A. Gravar na Folha1 (Histórico Geral)
        tipo_fixo_var = "Fixo" if categoria in ["Créditos", "Renda"] else "Variável"
        
        try:
            df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
        except:
            df_gastos = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])
        
        nova_linha = pd.DataFrame([{
            "Data": data.strftime("%d/%m/%Y"), 
            "Descrição": descricao, 
            "Categoria": categoria, 
            "Valor": valor, 
            "Tipo (Fixo/Variavel)": tipo_fixo_var
        }])
        
        conn.update(spreadsheet=URL_SHEET, worksheet="Folha1", data=pd.concat([df_gastos, nova_linha], ignore_index=True))

        # B. Abate Automático nos Objetivos (Só se for Categoria Crédito e o nome bater certo)
        if categoria == "Créditos" and descricao in lista_creditos:
            idx = df_obj[df_obj["Nome"] == descricao].index[0]
            # Atualiza o valor acumulado pago no Sheets
            df_obj.at[idx, 'Valor_Atual'] = float(df_obj.at[idx, 'Valor_Atual']) + valor
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_obj)
            st.success(f"✅ Dívida de {descricao} abatida em {valor}€!")
        else:
            st.success(f"✅ Gasto registado com sucesso!")
        
        st.rerun()
    else:
        st.error("Por favor, preenche o valor e a descrição.")
