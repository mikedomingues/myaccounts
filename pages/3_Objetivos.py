import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

st.set_page_config(page_title="Gestor de Créditos Dinâmico", layout="wide", page_icon="🎯")

URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARREGAR DADOS ---
df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
df_receitas = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")
saldo_mensal = df_receitas["Valor"].sum() - df_gastos["Valor"].sum()

try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
except:
    st.error("Cria a aba 'Objetivos' com as colunas certas.")
    st.stop()

st.title("🎯 Planeamento de Créditos Dinâmico")

# --- BLOCO DE EDIÇÃO RÁPIDA ---
with st.sidebar:
    st.header("⚙️ Ajustar Valores")
    if not df_obj.empty:
        obj_para_editar = st.selectbox("Selecionar Crédito para ajustar", df_obj["Nome"].tolist())
        idx = df_obj[df_obj["Nome"] == obj_para_editar].index[0]
        
        nova_divida = st.number_input("Dívida Atual Total (€)", value=float(df_obj.at[idx, 'Valor_Alvo']))
        nova_mensalidade = st.number_input("Nova Mensalidade (€)", value=float(df_obj.at[idx, 'Mensalidade']))
        
        if st.button("Atualizar Dados"):
            df_obj.at[idx, 'Valor_Alvo'] = nova_divida
            df_obj.at[idx, 'Mensalidade'] = nova_mensalidade
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_obj)
            st.success("Dados atualizados!")
            st.rerun()

# --- ANÁLISE E SUGESTÕES ---
if not df_obj.empty:
    for _, row in df_obj.iterrows():
        divida = row['Valor_Alvo'] - row['Valor_Atual']
        taxa_mensal = (row['Taxa_Juro'] / 100) / 12
        juro_mensal = divida * taxa_mensal
        
        st.subheader(f"📍 {row['Nome']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Dívida Real", f"{divida:.2f} €")
        c2.metric("Mensalidade Fixa", f"{row['Mensalidade']:.2f} €")
        
        # Cálculo de tempo real
        if row['Mensalidade'] > juro_mensal:
            n_meses = -math.log(1 - (taxa_mensal * divida) / row['Mensalidade']) / math.log(1 + taxa_mensal)
            c3.metric("Tempo para Fim", f"{int(n_meses)} meses")
            
            # --- ÁREA DE SUGESTÕES ---
            st.markdown("---")
            st.subheader("💡 Como acelerar este objetivo?")
            
            if saldo_mensal > 20: # Se houver pelo menos 20€ de folga
                amortizacao_extra = st.slider(f"Simular pagamento extra para {row['Nome']} (€)", 0, int(saldo_mensal), 50)
                nova_mensa_simulada = row['Mensalidade'] + amortizacao_extra
                novo_tempo = -math.log(1 - (taxa_mensal * divida) / nova_mensa_simulada) / math.log(1 + taxa_mensal)
                
                tempo_poupado = int(n_meses) - int(novo_tempo)
                
                st.success(f"🚀 Se pagares mais **{amortizacao_extra}€** este mês, ficas livre desta dívida **{tempo_poupado} meses mais cedo**!")
                st.write(f"Juros que deixas de pagar ao banco (estimativa): **{(juro_mensal * tempo_poupado):.2f} €**")
        else:
            st.error("A mensalidade atual não cobre os juros. A dívida está a crescer!")
        st.divider()
