"""Página de Finanças - Integrado com Supabase."""

from __future__ import annotations

from datetime import date
import pandas as pd
import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.ui import inject_dashboard_theme, page_header, sidebar_brand
from services.financas_service import (
    load_financas,
    insert_financa,
    update_financa,
    delete_financa
)
from services.custos_fixos_service import (
    load_custos_fixos,
    insert_custo_fixo,
    update_custo_fixo,
    delete_custo_fixo,
    gerar_lancamentos_automaticos
)
from components.data_table import render_data_table, format_currency
from components.forms import form_number_input, form_select_mes, form_select_ano
from components.kpis import render_kpi_row

st.set_page_config(
    page_title="Finanças",
    layout="wide",
    page_icon=":material/account_balance_wallet:"
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
    if st.button("Sair", type="secondary", use_container_width=True, key="logout_financas"):
        logout()
        st.rerun()

page_header("Finanças", "Gestão de receitas, despesas e custos fixos", lucide="wallet")

# ========== TABS: LANÇAMENTOS | CUSTOS FIXOS ==========
tab_lancamentos, tab_custos = st.tabs(["Lançamentos Mensais", "Custos Fixos"])

# ========================================
# TAB 1: LANÇAMENTOS MENSAIS
# ========================================
with tab_lancamentos:
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 2, 3])
    
    with col_filtro1:
        mes_selecionado = form_select_mes()
    
    with col_filtro2:
        ano_selecionado = form_select_ano()
    
    with col_filtro3:
        if st.button("Gerar Lançamentos Automáticos", type="secondary"):
            if gerar_lancamentos_automaticos(ano_selecionado, mes_selecionado):
                st.success("Lançamentos automáticos gerados!")
                st.rerun()
            else:
                st.error("Erro ao gerar lançamentos.")
    
    # Carregar finanças
    df_financas = load_financas(ano=ano_selecionado, mes=mes_selecionado)
    
    # KPIs
    if not df_financas.empty:
        receitas = df_financas[df_financas["tipo"] == "receita"]["valor"].sum()
        despesas = df_financas[df_financas["tipo"] == "despesa"]["valor"].sum()
        saldo = receitas - despesas
        
        render_kpi_row([
            ("Receitas", format_currency(receitas), None),
            ("Despesas", format_currency(despesas), None),
            ("Saldo", format_currency(saldo), f"{saldo:.0f}"),
        ])
    
    # Tabela
    st.markdown("### Lançamentos")
    
    if not df_financas.empty:
        df_display = df_financas[["data", "descricao", "tipo", "valor", "entrada", "categoria"]].copy()
        df_display["valor"] = df_display["valor"].apply(format_currency)
        df_display["entrada"] = df_display["entrada"].map({True: "✓", False: ""})
        
        render_data_table(df_display, height=350)
    else:
        st.info("Nenhum lançamento para este mês.")
    
    # Formulário de novo lançamento
    st.markdown("### Novo Lançamento")
    
    with st.form("form_novo_lancamento"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            data_lancamento = st.date_input("Data", value=date.today())
            descricao = st.text_input("Descrição")
        
        with col2:
            tipo = st.selectbox("Tipo", ["receita", "despesa"])
            valor = form_number_input("Valor", value=0.0)
        
        with col3:
            categoria = st.text_input("Categoria", value="Geral")
            entrada = st.checkbox("É uma entrada?", value=(tipo == "receita"))
        
        submitted = st.form_submit_button("💾 Salvar Lançamento", type="primary")
        
        if submitted:
            if not descricao:
                st.error("Descrição é obrigatória.")
            elif valor <= 0:
                st.error("Valor deve ser maior que zero.")
            else:
                novo_lancamento = {
                    "ano": data_lancamento.year,
                    "mes": data_lancamento.month,
                    "data": str(data_lancamento),
                    "descricao": descricao,
                    "tipo": tipo,
                    "valor": valor,
                    "entrada": entrada,
                    "categoria": categoria
                }
                
                if insert_financa(novo_lancamento):
                    st.success("Lançamento salvo!")
                    st.rerun()
    
    # Edição/Exclusão
    if not df_financas.empty:
        st.markdown("### Editar/Excluir Lançamento")
        
        opcoes_lancamentos = [
            f"{row['data']} - {row['descricao']} - {format_currency(row['valor'])}"
            for _, row in df_financas.iterrows()
        ]
        lancamento_selecionado = st.selectbox("Selecione o lançamento", opcoes_lancamentos)
        
        if lancamento_selecionado:
            idx = opcoes_lancamentos.index(lancamento_selecionado)
            lancamento_atual = df_financas.iloc[idx]
            
            col_edit, col_delete = st.columns([3, 1])
            
            with col_edit:
                with st.form("form_editar_lancamento"):
                    st.markdown(f"**Editando: {lancamento_atual['descricao']}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nova_descricao = st.text_input("Descrição", value=lancamento_atual["descricao"])
                        novo_tipo = st.selectbox(
                            "Tipo",
                            ["receita", "despesa"],
                            index=0 if lancamento_atual["tipo"] == "receita" else 1
                        )
                    
                    with col2:
                        novo_valor = form_number_input("Valor", value=float(lancamento_atual["valor"]))
                        nova_entrada = st.checkbox(
                            "É uma entrada?",
                            value=bool(lancamento_atual["entrada"])
                        )
                    
                    submitted_edit = st.form_submit_button("💾 Atualizar")
                    
                    if submitted_edit:
                        dados_atualizados = {
                            "descricao": nova_descricao,
                            "tipo": novo_tipo,
                            "valor": novo_valor,
                            "entrada": nova_entrada
                        }
                        
                        if update_financa(lancamento_atual["id"], dados_atualizados):
                            st.success("Lançamento atualizado!")
                            st.rerun()
            
            with col_delete:
                st.markdown("**Excluir**")
                if st.button("Deletar", type="secondary", key="btn_delete_lancamento"):
                    if delete_financa(lancamento_atual["id"]):
                        st.success("Lançamento excluído!")
                        st.rerun()

# ========================================
# TAB 2: CUSTOS FIXOS
# ========================================
with tab_custos:
    st.markdown("### Custos Fixos e Recorrências")
    st.info("Os custos fixos ativos geram lançamentos automáticos todos os meses.")
    
    # Carregar custos fixos
    df_custos = load_custos_fixos()
    
    # Tabela
    if not df_custos.empty:
        df_display_custos = df_custos[[
            "descricao", "tipo", "valor", "entrada", "dia_vencimento",
            "parcela_atual", "total_parcelas", "ativo"
        ]].copy()
        df_display_custos["valor"] = df_display_custos["valor"].apply(format_currency)
        df_display_custos["entrada"] = df_display_custos["entrada"].map({True: "✓", False: ""})
        df_display_custos["ativo"] = df_display_custos["ativo"].map({True: "✅ Ativo", False: "❌ Inativo"})
        
        render_data_table(df_display_custos, height=300)
    else:
        st.info("Nenhum custo fixo cadastrado.")
    
    # Formulário de novo custo fixo
    st.markdown("### Novo Custo Fixo")
    
    with st.form("form_novo_custo_fixo"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            descricao_custo = st.text_input("Descrição")
            tipo_custo = st.selectbox("Tipo", ["fixo", "parcelado"])
        
        with col2:
            valor_custo = form_number_input("Valor", value=0.0)
            dia_vencimento = st.number_input("Dia do Vencimento", min_value=1, max_value=31, value=10)
            entrada_custo = st.checkbox("É uma entrada?", value=False)
        
        with col3:
            if tipo_custo == "parcelado":
                total_parcelas = st.number_input("Total de Parcelas", min_value=1, value=12)
            else:
                total_parcelas = 1
            
            ativo = st.checkbox("Ativo", value=True)
        
        submitted_custo = st.form_submit_button("salvar Custo Fixo", type="primary")
        
        if submitted_custo:
            if not descricao_custo:
                st.error("Descrição é obrigatória.")
            elif valor_custo <= 0:
                st.error("Valor deve ser maior que zero.")
            else:
                novo_custo = {
                    "descricao": descricao_custo,
                    "tipo": tipo_custo,
                    "valor": valor_custo,
                    "entrada": entrada_custo,
                    "dia_vencimento": dia_vencimento,
                    "parcela_atual": 1,
                    "total_parcelas": total_parcelas,
                    "ativo": ativo
                }
                
                if insert_custo_fixo(novo_custo):
                    st.success("Custo fixo salvo!")
                    st.rerun()
    
    # Edição de custos fixos
    if not df_custos.empty:
        st.markdown("### Gerenciar Custos Fixos")
        
        opcoes_custos = [row["descricao"] for _, row in df_custos.iterrows()]
        custo_selecionado = st.selectbox("Selecione o custo fixo", opcoes_custos, key="select_custo")
        
        if custo_selecionado:
            idx_custo = opcoes_custos.index(custo_selecionado)
            custo_atual = df_custos.iloc[idx_custo]
            
            col_edit_custo, col_delete_custo = st.columns([3, 1])
            
            with col_edit_custo:
                with st.form("form_editar_custo"):
                    st.markdown(f"**Editando: {custo_atual['descricao']}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        novo_valor_custo = form_number_input("Valor", value=float(custo_atual["valor"]))
                        novo_ativo = st.checkbox("Ativo", value=bool(custo_atual["ativo"]))
                    
                    with col2:
                        nova_parcela_atual = st.number_input(
                            "Parcela Atual",
                            min_value=1,
                            value=int(custo_atual["parcela_atual"])
                        )
                        nova_entrada_custo = st.checkbox(
                            "É uma entrada?",
                            value=bool(custo_atual["entrada"])
                        )
                    
                    submitted_edit_custo = st.form_submit_button("Atualizar")
                    
                    if submitted_edit_custo:
                        dados_custo_atualizados = {
                            "valor": novo_valor_custo,
                            "ativo": novo_ativo,
                            "parcela_atual": nova_parcela_atual,
                            "entrada": nova_entrada_custo
                        }
                        
                        if update_custo_fixo(custo_atual["id"], dados_custo_atualizados):
                            st.success("Custo fixo atualizado!")
                            st.rerun()
            
            with col_delete_custo:
                st.markdown("**Excluir**")
                if st.button("Deletar", type="secondary", key="btn_delete_custo"):
                    if delete_custo_fixo(custo_atual["id"]):
                        st.success("Custo fixo excluído!")
                        st.rerun()
