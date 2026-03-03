import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Finanças Pro", layout="wide", page_icon="💰")

# --- LIGAÇÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(worksheet="Folha1", ttl="0s") # ttl=0 para atualizar na hora

df = load_data()

# --- SIDEBAR (INPUT) ---
st.sidebar.header("📝 Registar Gasto")
with st.sidebar.form("entry_form"):
    data = st.date_input("Data", datetime.now())
    descricao = st.text_input("O que compraste?")
    categoria = st.selectbox("Categoria", [
        "Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco", 
        "Combustível", "Compras", "Almoço/Jantar Fora", "Outros"
    ])
    valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Guardar")

    if submit and descricao and valor > 0:
        tipo = "Fixo" if categoria in ["Renda", "Prestação Carro", "Wizink", "Universo", "Activo Banco"] else "Variável"
        nova_linha = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Descricao": descricao, "Categoria": categoria, "Valor": valor, "Tipo": tipo}])
        updated_df = pd.concat([df, nova_linha], ignore_index=True)
        conn.update(worksheet="Folha1", data=updated_df)
        st.sidebar.success("Gravado!")
        st.rerun()

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Painel de Controlo Financeiro")

if not df.empty:
    # 1. Métricas Rápidas
    total_gasto = df["Valor"].sum()
    gastos_fixos = df[df["Tipo"] == "Fixo"]["Valor"].sum()
    gastos_var = df[df["Tipo"] == "Variável"]["Valor"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Gasto", f"{total_gasto:.2f} €")
    col2.metric("Custos Fixos", f"{gastos_fixos:.2f} €")
    col3.metric("Custos Variáveis", f"{gastos_var:.2f} €")

    st.divider()

    # 2. Gráficos Interativos
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Distribuição por Categoria")
        fig_pie = px.pie(df, values="Valor", names="Categoria", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("Evolução dos Gastos")
        # Pequeno ajuste para garantir que a data está em ordem
        df['Data_dt'] = pd.to_datetime(df['Data'], dayfirst=True)
        df_sorted = df.sort_values("Data_dt")
        fig_line = px.line(df_sorted, x="Data_dt", y="Valor", markers=True, title="Gastos ao Longo do Tempo")
        st.plotly_chart(fig_line, use_container_width=True)

    # 3. MÓDULO DE SUGESTÕES (O teu consultor financeiro IA)
    st.divider()
    st.subheader("💡 Sugestões de Poupança")
    
    # Exemplo de lógica para Créditos (Wizink/Universo)
    gastos_credito = df[df["Categoria"].isin(["Wizink", "Universo"])]["Valor"].sum()
    
    if gastos_credito > 0:
        st.warning(f"⚠️ Estás a pagar **{gastos_credito:.2f} €** em créditos de alto juro este mês. "
                   "Tenta canalizar qualquer poupança extra para amortizar primeiro o **Wizink**.")
    
    if gastos_var > gastos_fixos:
        st.info("ℹ️ Os teos gastos variáveis superaram os fixos. Verifica a categoria 'Almoço/Jantar Fora' para cortes rápidos.")
        
    if "Combustível" in df["Categoria"].values:
        total_gasol = df[df["Categoria"] == "Combustível"]["Valor"].sum()
        if total_gasol > 150:
            st.write("⛽ O gasto em combustível está elevado. Já verificaste se compensa usar apps de desconto ou transportes?")

else:
    st.info("Aguardando os primeiros dados para gerar análises...")
