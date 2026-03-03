import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Finanças Pro - Dashboard", layout="wide", page_icon="🏠")

# URL do teu Sheets (Confirmado)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1tq1LJczuy_j_ioabUj3ZPwegqm7QqMW__dLAaSw-p8Q/edit?usp=sharing"

# --- SISTEMA DE LOGIN SIMPLES ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Acesso ao Gestor Financeiro")
    with st.container():
        senha = st.text_input("Introduza a sua senha secreta", type="password")
        if st.button("Desbloquear Dashboard"):
            if senha == "1234": # <--- Podes alterar esta senha para o que quiseres
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    st.stop() # Interrompe o código aqui se não estiver logado

# --- SE ESTIVER LOGADO, CARREGA O DASHBOARD ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    # Lemos a Folha1 (Gastos)
    try:
        df_g = conn.read(spreadsheet=URL_SHEET, worksheet="Folha1", ttl="0s")
    except:
        df_g = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo (Fixo/Variavel)"])
    
    # Lemos a aba Recebimentos (Receitas)
    try:
        df_r = conn.read(spreadsheet=URL_SHEET, worksheet="Recebimentos", ttl="0s")
    except:
        df_r = pd.DataFrame(columns=["Data", "Origem", "Valor"])
        
    return df_g, df_r

df_gastos, df_receitas = load_all_data()

st.title("📊 Painel de Controlo Financeiro")

# --- CÁLCULOS DE SALDO ---
total_gastos = df_gastos["Valor"].sum() if not df_gastos.empty else 0
total_receitas = df_receitas["Valor"].sum() if not df_receitas.empty else 0
saldo_atual = total_receitas - total_gastos

# --- MÉTRICAS NO TOPO ---
c1, c2, c3 = st.columns(3)
c1.metric("Receitas (Entradas)", f"{total_receitas:.2f} €", delta_color="normal")
c2.metric("Despesas (Saídas)", f"-{total_gastos:.2f} €", delta_color="inverse")
c3.metric("SALDO DISPONÍVEL", f"{saldo_atual:.2f} €", 
          delta="Positivo" if saldo_atual >= 0 else "Negativo",
          delta_color="normal" if saldo_atual >= 0 else "inverse")

st.divider()

# --- ANÁLISE VISUAL ---
col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.subheader("Onde está o dinheiro?")
    if not df_gastos.empty:
        fig_pie = px.pie(df_gastos, values="Valor", names="Categoria", hole=0.4,
                         title="Distribuição de Gastos",
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Sem dados de gastos para mostrar o gráfico.")

with col_dir:
    st.subheader("💡 Sugestões e Alertas")
    
    # Lógica de Sugestões baseada nos teus Créditos
    creditos_lista = ["Wizink", "Universo", "Activo Banco"]
    total_creditos = df_gastos[df_gastos["Categoria"].isin(creditos_lista)]["Valor"].sum()
    
    if total_creditos > 0:
        st.warning(f"⚠️ Estás a pagar **{total_creditos:.2f} €** em créditos este mês.")
        st.write("👉 *Dica:* Se tiveres saldo extra, prioriza amortizar o Wizink ou Universo devido aos juros.")

    if saldo_atual < 0:
        st.error("🚨 Orçamento em Alerta! Gastaste mais do que recebeste. Verifica os gastos 'Variáveis'.")
    elif saldo_atual > 0 and total_receitas > 0:
        poupanca_sugerida = saldo_atual * 0.2
        st.success(f"✅ Saldo Positivo! Sugerimos colocar **{poupanca_sugerida:.2f} €** (20%) numa conta poupança.")

# --- TABELA DE RESUMO ---
st.divider()
st.subheader("📝 Últimas Movimentações (Gastos)")
st.dataframe(df_gastos.tail(10), use_container_width=True)

# Botão para limpar cache se houver problemas
if st.sidebar.button("Limpar Cache / Atualizar"):
    st.cache_data.clear()
    st.rerun()
