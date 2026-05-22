"""Página de Plantões - Integrado com Supabase."""

from __future__ import annotations

from datetime import date
import pandas as pd
import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.ui import inject_dashboard_theme, page_header, sidebar_brand
from services.plantoes_service import (
    load_plantoes,
    insert_plantao,
    update_plantao,
    delete_plantao
)
from components.data_table import render_data_table, format_currency
from components.forms import form_number_input, form_select_mes, form_select_ano
from components.kpis import render_kpi_row

st.set_page_config(
    page_title="Plantões",
    layout="wide",
    page_icon=":material/medical_services:"
)

inject_dashboard_theme()

# Autenticação
init_auth_state()
if not is_authenticated():
    st.warning("Você precisa fazer login primeiro.")
    st.stop()

sidebar_brand()

# Logout
with st.sidebar:
    st.markdown("---")
    if st.button("Sair", type="secondary", use_container_width=True, key="logout_plantoes"):
        logout()
        st.rerun()

page_header("Plantões", "Gestão de plantões médicos mensais", lucide="stethoscope")

# ========== 1. CARREGAR DADOS ==========
ano_atual = date.today().year
anos_disponiveis = list(range(ano_atual - 2, ano_atual + 3))

# Filtro de ano
ano_selecionado = st.selectbox(
    "Filtrar por ano",
    anos_disponiveis,
    index=2,
    key="filtro_ano_plantoes"
)

# Carregar plantões do Supabase
df_plantoes = load_plantoes(ano=ano_selecionado)

# ========== 2. RENDERIZAR KPIs ==========
if not df_plantoes.empty:
    total_bruto = df_plantoes["valor_bruto"].sum()
    total_liquido = df_plantoes["valor_liquido"].sum()
    total_imposto = df_plantoes["imposto"].sum()
    total_quantidade = df_plantoes["quantidade"].sum()
    
    render_kpi_row([
        ("Total Bruto", format_currency(total_bruto), None),
        ("Total Líquido", format_currency(total_liquido), None),
        ("Total Impostos", format_currency(total_imposto), None),
        ("Quantidade", f"{int(total_quantidade)} plantões", None),
    ])

# ========== 3. RENDERIZAR TABELA ==========
st.markdown("### Plantões Cadastrados")

if not df_plantoes.empty:
    # Formatar para exibição
    df_display = df_plantoes[["mes", "quantidade", "valor_bruto", "imposto", "valor_liquido", "entrada"]].copy()
    df_display["valor_bruto"] = df_display["valor_bruto"].apply(format_currency)
    df_display["imposto"] = df_display["imposto"].apply(format_currency)
    df_display["valor_liquido"] = df_display["valor_liquido"].apply(format_currency)
    df_display["entrada"] = df_display["entrada"].map({True: "✓", False: ""})
    
    render_data_table(df_display, height=400)
else:
    st.info(f"Nenhum plantão cadastrado para {ano_selecionado}.")

# ========== 4. FORMULÁRIO DE INSERÇÃO ==========
st.markdown("### Novo Plantão")

with st.form("form_novo_plantao"):
    col1, col2 = st.columns(2)
    
    with col1:
        mes = form_select_mes()
        quantidade = st.number_input("Quantidade de plantões", min_value=0, step=1, value=0)
        valor_bruto = form_number_input("Valor Bruto", value=0.0)
    
    with col2:
        imposto = form_number_input("Imposto", value=0.0)
        valor_liquido = form_number_input("Valor Líquido", value=0.0)
        entrada = st.checkbox("É uma entrada? (receita)", value=True)
    
    submitted = st.form_submit_button("💾 Salvar Plantão", type="primary")
    
    if submitted:
        if quantidade <= 0:
            st.error("Quantidade deve ser maior que zero.")
        elif valor_bruto <= 0:
            st.error("Valor bruto deve ser maior que zero.")
        else:
            # Inserir no Supabase
            novo_plantao = {
                "ano": ano_selecionado,
                "mes": mes,
                "quantidade": quantidade,
                "valor_bruto": valor_bruto,
                "imposto": imposto,
                "valor_liquido": valor_liquido,
                "entrada": entrada
            }
            
            if insert_plantao(novo_plantao):
                st.success("Plantão salvo com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao salvar plantão.")

# ========== 5. EDIÇÃO/EXCLUSÃO ==========
if not df_plantoes.empty:
    st.markdown("### Editar/Excluir Plantão")
    
    # Seletor de plantão
    opcoes_plantoes = [f"Mês {row['mes']}" for _, row in df_plantoes.iterrows()]
    plantao_selecionado = st.selectbox("Selecione o plantão", opcoes_plantoes, key="select_plantao_edit")
    
    if plantao_selecionado:
        idx = opcoes_plantoes.index(plantao_selecionado)
        plantao_atual = df_plantoes.iloc[idx]
        
        col_edit, col_delete = st.columns([3, 1])
        
        with col_edit:
            with st.form("form_editar_plantao"):
                st.markdown(f"**Editando: Mês {plantao_atual['mes']}/{plantao_atual['ano']}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nova_quantidade = st.number_input(
                        "Quantidade",
                        min_value=0,
                        step=1,
                        value=int(plantao_atual["quantidade"])
                    )
                    novo_valor_bruto = form_number_input(
                        "Valor Bruto",
                        value=float(plantao_atual["valor_bruto"])
                    )
                
                with col2:
                    novo_imposto = form_number_input(
                        "Imposto",
                        value=float(plantao_atual["imposto"])
                    )
                    novo_valor_liquido = form_number_input(
                        "Valor Líquido",
                        value=float(plantao_atual["valor_liquido"])
                    )
                    nova_entrada = st.checkbox(
                        "É uma entrada?",
                        value=bool(plantao_atual["entrada"])
                    )
                
                submitted_edit = st.form_submit_button("Atualizar", type="primary")
                
                if submitted_edit:
                    dados_atualizados = {
                        "quantidade": nova_quantidade,
                        "valor_bruto": novo_valor_bruto,
                        "imposto": novo_imposto,
                        "valor_liquido": novo_valor_liquido,
                        "entrada": nova_entrada
                    }
                    
                    if update_plantao(plantao_atual["id"], dados_atualizados):
                        st.success("Plantão atualizado!")
                        st.rerun()
        
        with col_delete:
            st.markdown("**Excluir**")
            if st.button("Deletar Plantão", type="secondary", key="btn_delete_plantao"):
                if delete_plantao(plantao_atual["id"]):
                    st.success("Plantão excluído!")
                    st.rerun()
