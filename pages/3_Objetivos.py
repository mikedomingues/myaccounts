import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Objetivos e Poupança", layout="wide", page_icon="🎯")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. CARREGAR DADOS PARA ANÁLISE
df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
df_receitas = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")

try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
except:
    df_obj = pd.DataFrame(columns=["Nome", "Valor_Alvo", "Valor_Atual", "Tipo"])

# CÁLCULO DE CAPACIDADE MENSAL (Média de saldo)
total_g = df_gastos["Valor"].sum()
total_r = df_receitas["Valor"].sum()
saldo_real = total_r - total_g

st.title("🎯 Gestão de Objetivos")

# --- BLOCO 1: CRIAR NOVO OBJETIVO ---
with st.expander("➕ Criar Novo Objetivo / Dívida para Liquidar"):
    with st.form("novo_obj"):
        nome = st.text_input("Nome (ex: Liquidar Wizink, Fundo Emergência)")
        tipo = st.selectbox("Tipo", ["Crédito", "Poupança"])
        alvo = st.number_input("Valor Total (O que deves ou o que queres ter)", min_value=0.0)
        atual = st.number_input("Valor já pago/poupado", min_value=0.0)
        if st.form_submit_button("Criar Objetivo"):
            novo_df = pd.DataFrame([{"Nome": nome, "Valor_Alvo": alvo, "Valor_Atual": atual, "Tipo": tipo}])
            updated = pd.concat([df_obj, novo_df], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=updated)
            st.success("Objetivo criado!")
            st.rerun()

# --- BLOCO 2: ANÁLISE DE PROGRESSO ---
if not df_obj.empty:
    for index, row in df_obj.iterrows():
        st.subheader(f"📍 {row['Nome']}")
        progresso = row['Valor_Atual'] / row['Valor_Alvo']
        st.progress(min(progresso, 1.0))
        
        c1, c2, c3 = st.columns(3)
        falta = row['Valor_Alvo'] - row['Valor_Atual']
        c1.write(f"**Faltam:** {falta:.2f} €")
        
        # ANÁLISE INTELIGENTE
        if saldo_real > 0:
            meses_faltam = falta / saldo_real if saldo_real > 0 else 0
            c2.write(f"**Tempo Estimado:** {meses_faltam:.1f} meses")
            c3.write(f"**Esforço:** Usando 100% do teu saldo atual")
            
            # SUGESTÃO DE CORTE
            st.info(f"💡 Se cortares 20% nos teus 'Extras' e 'Compras', ganhas mais {(total_g * 0.05):.2f}€/mês para este objetivo.")
        else:
            st.error("⚠️ Não tens saldo disponível para este objetivo. Revisa os teus gastos mensais.")
        st.divider()

else:
    st.info("Cria o teu primeiro objetivo acima!")
