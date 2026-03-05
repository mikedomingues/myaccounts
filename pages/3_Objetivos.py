import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy_financial as npf # Biblioteca para cálculos financeiros

st.set_page_config(page_title="Objetivos Reais", layout="wide", page_icon="🎯")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARREGA DADOS ---
try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
except:
    df_obj = pd.DataFrame(columns=["Nome", "Valor_Alvo", "Valor_Atual", "Mensalidade", "Tipo", "Taxa_Juro"])

st.title("🎯 Planeamento com Juros Reais")

# --- FORMULÁRIO COM TAXA DE JURO ---
with st.expander("➕ Adicionar Crédito (com Juros)"):
    with st.form("novo_obj_juros"):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome do Crédito")
        alvo = c2.number_input("Dívida Total Atual (€)", min_value=0.0)
        atual = c3.number_input("Já amortizado (opcional)", min_value=0.0)
        
        c4, c5, c6 = st.columns(3)
        mensalidade = c4.number_input("Mensalidade que pagas (€)", min_value=0.0)
        taxa = c5.number_input("Taxa de Juro Anual - TANU (%)", min_value=0.0, format="%.2f")
        tipo = c6.selectbox("Tipo", ["Crédito", "Poupança"])
        
        if st.form_submit_button("Guardar"):
            novo_df = pd.DataFrame([{"Nome": nome, "Valor_Alvo": alvo, "Valor_Atual": atual, "Mensalidade": mensalidade, "Tipo": tipo, "Taxa_Juro": taxa}])
            updated = pd.concat([df_obj, novo_df], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=updated)
            st.rerun()

# --- ANÁLISE REALISTA ---
if not df_obj.empty:
    for _, row in df_obj.iterrows():
        divida_real = row['Valor_Alvo'] - row['Valor_Atual']
        taxa_mensal = (row['Taxa_Juro'] / 100) / 12
        
        st.subheader(f"📍 {row['Nome']}")
        
        if taxa_mensal > 0 and row['Tipo'] == "Crédito":
            juro_mensal_euro = divida_real * taxa_mensal
            amortizacao_real = row['Mensalidade'] - juro_mensal_euro
            
            if amortizacao_real <= 0:
                st.error(f"🛑 Atenção! A tua mensalidade de {row['Mensalidade']}€ nem sequer cobre os juros ({juro_mensal_euro:.2f}€). A dívida nunca vai acabar!")
            else:
                # Cálculo de meses reais usando logaritmos para juros compostos
                import math
                try:
                    # Fórmula para tempo de quitação de empréstimo
                    n_meses = -math.log(1 - (taxa_mensal * divida_real) / row['Mensalidade']) / math.log(1 + taxa_mensal)
                    
                    st.progress(min(row['Valor_Atual']/row['Valor_Alvo'], 1.0))
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Dívida Real", f"{divida_real:.2f} €")
                    m2.metric("Juros Mensais (Perdidos)", f"{juro_mensal_euro:.2f} €", delta_color="inverse")
                    m3.metric("Tempo Real", f"{int(n_meses)} meses")
                    
                    st.warning(f"💡 Sabias? Dos teus {row['Mensalidade']}€, apenas **{amortizacao_real:.2f}€** estão realmente a abater a dívida.")
                except:
                    st.info("Cálculo impossível com os valores atuais.")
        else:
            st.info("Esta é uma conta de poupança (sem juros de dívida) ou taxa zero.")
        st.divider()
