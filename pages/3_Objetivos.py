import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

st.set_page_config(page_title="Gestor de Objetivos", layout="wide", page_icon="🎯")

# URL do teu Sheets
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARREGAR DADOS ---
df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
df_receitas = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")
saldo_mensal = df_receitas["Valor"].sum() - df_gastos["Valor"].sum()

try:
    df_obj = conn.read(spreadsheet=URL_SHEET, worksheet="Objetivos", ttl="0s")
except:
    df_obj = pd.DataFrame(columns=["Nome", "Valor_Alvo", "Valor_Atual", "Mensalidade", "Taxa_Juro", "Tipo"])

st.title("🎯 Planeamento e Amortização Real")

# --- BARRA LATERAL: CRIAR OU ALTERAR ---
st.sidebar.header("🛠️ Gestão de Objetivos")
modo = st.sidebar.radio("Ação:", ["Criar Novo", "Alterar Existente"])

if modo == "Criar Novo":
    with st.sidebar.form("form_criar"):
        nome_n = st.text_input("Nome (ex: Wizink)")
        alvo_n = st.number_input("Dívida Total / Alvo (€)", min_value=0.0)
        atual_n = st.number_input("Já pago / poupado (€)", min_value=0.0)
        mensa_n = st.number_input("Mensalidade atual (€)", min_value=0.0)
        taxa_n = st.number_input("Taxa Juro Anual TANU (%)", min_value=0.0)
        tipo_n = st.selectbox("Tipo", ["Crédito", "Poupança"])
        
        if st.form_submit_button("Guardar Novo"):
            nova_l = pd.DataFrame([{"Nome": nome_n, "Valor_Alvo": alvo_n, "Valor_Atual": atual_n, "Mensalidade": mensa_n, "Taxa_Juro": taxa_n, "Tipo": tipo_n}])
            df_atualizado = pd.concat([df_obj, nova_l], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_atualizado)
            st.success("Criado com sucesso!")
            st.rerun()

else: # MODO ALTERAR
    if not df_obj.empty:
        obj_sel = st.sidebar.selectbox("Selecionar para Alterar:", df_obj["Nome"].tolist())
        idx = df_obj[df_obj["Nome"] == obj_sel].index[0]
        
        with st.sidebar.form("form_alterar"):
            # Campos preenchidos com os valores que já estão no Sheets
            alvo_alt = st.number_input("Dívida Total (€)", value=float(df_obj.at[idx, 'Valor_Alvo']))
            atual_alt = st.number_input("Já pago (€)", value=float(df_obj.at[idx, 'Valor_Atual']))
            mensa_alt = st.number_input("Mensalidade (€)", value=float(df_obj.at[idx, 'Mensalidade']))
            taxa_alt = st.number_input("Taxa (%)", value=float(df_obj.at[idx, 'Taxa_Juro']))
            
            if st.form_submit_button("Atualizar Dados"):
                df_obj.at[idx, 'Valor_Alvo'] = alvo_alt
                df_obj.at[idx, 'Valor_Atual'] = atual_alt
                df_obj.at[idx, 'Mensalidade'] = mensa_alt
                df_obj.at[idx, 'Taxa_Juro'] = taxa_alt
                conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_obj)
                st.success("Dados atualizados!")
                st.rerun()
        
        if st.sidebar.button("🗑️ Eliminar Objetivo"):
            df_obj = df_obj.drop(idx)
            conn.update(spreadsheet=URL_SHEET, worksheet="Objetivos", data=df_obj)
            st.rerun()
    else:
        st.sidebar.info("Nada para alterar.")

# --- PAINEL PRINCIPAL: ANÁLISE ---
if not df_obj.empty:
    for _, row in df_obj.iterrows():
        falta = row['Valor_Alvo'] - row['Valor_Atual']
        st.subheader(f"📍 {row['Nome']} ({row['Tipo']})")
        
        if row['Tipo'] == "Crédito" and row['Taxa_Juro'] > 0:
            taxa_m = (row['Taxa_Juro'] / 100) / 12
            juro_m = falta * taxa_m
            
            if row['Mensalidade'] > juro_m:
                # Cálculo de tempo real considerando juros
                n_meses = -math.log(1 - (taxa_m * falta) / row['Mensalidade']) / math.log(1 + taxa_m)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Dívida Restante", f"{falta:.2f} €")
                c2.metric("Juros Mensais", f"{juro_m:.2f} €", delta_color="inverse")
                c3.metric("Tempo para Fim", f"{int(n_meses)} meses")
                
                # Simulador de Amortização
                if saldo_mensal > 10:
                    st.markdown(f"**💡 Simulador de Aceleração para {row['Nome']}:**")
                    extra = st.slider(f"Quanto queres pagar a mais este mês? (Saldo disp: {saldo_mensal:.2f}€)", 0, int(max(0, saldo_mensal)), 50, key=row['Nome'])
                    
                    nova_mensa = row['Mensalidade'] + extra
                    n_meses_novo = -math.log(1 - (taxa_m * falta) / nova_mensa) / math.log(1 + taxa_m)
                    poupanca_tempo = int(n_meses) - int(n_meses_novo)
                    
                    if poupanca_tempo > 0:
                        st.success(f"🚀 Ao pagares +{extra}€, ficas livre desta dívida **{poupanca_tempo} meses mais cedo!**")
            else:
                st.error(f"🛑 Mensalidade ({row['Mensalidade']}€) não cobre os juros ({juro_m:.2f}€)!")
        
        else: # Poupança
            st.progress(min(row['Valor_Atual']/row['Valor_Alvo'], 1.0) if row['Valor_Alvo'] > 0 else 0)
            st.metric("Falta para o objetivo", f"{falta:.2f} €")
        
        st.divider()
else:
    st.info("Utiliza a barra lateral para criar o teu primeiro crédito ou objetivo de poupança.")
