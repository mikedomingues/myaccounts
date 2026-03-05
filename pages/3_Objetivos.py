import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

st.set_page_config(page_title="Objetivos Reais", layout="wide", page_icon="🎯")

# URL do teu Sheets (já confirmado)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARREGAR DADOS ---
try:
    # Lendo a aba Objetivos que criaste
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
except:
    st.error("Certifica-te de que a aba se chama 'Objetivos' no Google Sheets.")
    st.stop()

st.title("🎯 Planeamento de Créditos e Poupanças")

# --- FORMULÁRIO DE REGISTO ---
with st.expander("➕ Adicionar Novo Crédito ou Meta"):
    with st.form("novo_obj"):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome (ex: Wizink)")
        alvo = c2.number_input("Valor Total em Dívida / Alvo", min_value=0.0)
        atual = c3.number_input("Já Amortizado / Poupado", min_value=0.0)
        
        c4, c5, c6 = st.columns(3)
        mensalidade = c4.number_input("Mensalidade que pagas hoje (€)", min_value=0.0)
        taxa = c5.number_input("Taxa de Juro Anual (%)", min_value=0.0, help="TANU do teu cartão/crédito")
        tipo = c6.selectbox("Tipo", ["Crédito", "Poupança"])
        
        if st.form_submit_button("Guardar Objetivo"):
            nova_linha = pd.DataFrame([{
                "Nome": nome, "Valor_Alvo": alvo, "Valor_Atual": atual, 
                "Mensalidade": mensalidade, "Taxa_Juro": taxa, "Tipo": tipo
            }])
            updated_df = pd.concat([df_obj, nova_linha], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=updated_df)
            st.success("Objetivo guardado!")
            st.rerun()

# --- ANÁLISE COM MATEMÁTICA REAL ---
if not df_obj.empty:
    for _, row in df_obj.iterrows():
        divida_restante = row['Valor_Alvo'] - row['Valor_Atual']
        st.subheader(f"📍 {row['Nome']}")
        
        # Se for crédito com juros
        if row['Tipo'] == "Crédito" and row['Taxa_Juro'] > 0:
            taxa_mensal = (row['Taxa_Juro'] / 100) / 12
            juro_mensal_euro = divida_restante * taxa_mensal
            amortizacao_real = row['Mensalidade'] - juro_mensal_euro
            
            # Cálculo de meses reais usando a fórmula de amortização
            if amortizacao_real > 0:
                try:
                    n_meses = -math.log(1 - (taxa_mensal * divida_restante) / row['Mensalidade']) / math.log(1 + taxa_mensal)
                    
                    st.progress(min(row['Valor_Atual']/row['Valor_Alvo'], 1.0))
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Dívida Real", f"{divida_restante:.2f} €")
                    m2.metric("Juro Mensal (Dinheiro 'Perdido')", f"{juro_mensal_euro:.2f} €", delta_color="inverse")
                    m3.metric("Tempo para Fim", f"{int(n_meses)} meses")
                    
                    st.info(f"💡 Desta mensalidade, apenas **{amortizacao_real:.2f}€** estão a reduzir a tua dívida.")
                except:
                    st.error("Erro no cálculo: Verifica se a mensalidade é suficiente para os juros.")
            else:
                st.error(f"🛑 Atenção: A tua mensalidade ({row['Mensalidade']}€) não cobre sequer os juros atuais ({juro_mensal_euro:.2f}€)!")
        
        # Se for poupança simples
