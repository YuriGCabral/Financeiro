"""Página de Casamento - Integrado com Supabase."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.ui import inject_dashboard_theme, page_header, sidebar_brand
from services.casamento_service import (
    load_casamento,
    insert_gasto_casamento,
    update_gasto_casamento,
    delete_gasto_casamento
)
from components.data_table import render_data_table, format_currency
from components.forms import form_number_input
from components.kpis import render_kpi_row

st.set_page_config(
    page_title="Meu Casamento",
    layout="wide",
    page_icon="💍"
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
    if st.button("Sair", type="secondary", use_container_width=True, key="logout_casamento"):
        logout()
        st.rerun()

page_header("Meu Casamento", "Planejamento financeiro completo do casamento", lucide="heart")

# ========== 1. CARREGAR DADOS ==========
df_casamento = load_casamento()

# ========== 2. RENDERIZAR KPIs ==========
if not df_casamento.empty:
    total_orcamento = df_casamento["orcamento"].sum()
    total_pago = df_casamento["valor_pago"].sum()
    total_restante = total_orcamento - total_pago
    percentual_gasto = (total_pago / total_orcamento * 100) if total_orcamento > 0 else 0
    
    render_kpi_row([
        ("💰 Orçamento Total", format_currency(total_orcamento), None),
        ("💳 Total Pago", format_currency(total_pago), None),
        ("⏳ Restante", format_currency(total_restante), None),
        ("📊 % Gasto", f"{percentual_gasto:.1f}%", None),
    ])

# ========== 3. RENDERIZAR TABELA ==========
st.markdown("### 📋 Gastos do Casamento")

if not df_casamento.empty:
    # Preparar dados para exibição
    df_display = df_casamento[[
        "categoria", "item", "orcamento", "valor_pago", 
        "entrada", "valor_restante", "status"
    ]].copy()
    
    df_display["orcamento"] = df_display["orcamento"].apply(format_currency)
    df_display["valor_pago"] = df_display["valor_pago"].apply(format_currency)
    df_display["valor_restante"] = df_display["valor_restante"].apply(format_currency)
    df_display["entrada"] = df_display["entrada"].map({True: "✓", False: ""})
    df_display["status"] = df_display["status"].map({
        "pendente": "⏳ Pendente",
        "parcial": "🔶 Parcial",
        "pago": "✅ Pago"
    })
    
    render_data_table(df_display, height=400)
else:
    st.info("Nenhum gasto cadastrado ainda.")

# ========== 4. FORMULÁRIO DE INSERÇÃO ==========
st.markdown("### ➕ Novo Gasto")

with st.form("form_novo_gasto"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categoria = st.text_input("Categoria", placeholder="Ex: Buffet, Decoração, etc")
        item = st.text_input("Item/Fornecedor", placeholder="Ex: Empresa XYZ")
    
    with col2:
        orcamento = form_number_input("Orçamento", value=0.0)
        valor_pago = form_number_input("Valor Pago", value=0.0)
    
    with col3:
        entrada = st.checkbox("É uma entrada? (presente/valor recebido)", value=False)
        status = st.selectbox("Status", ["pendente", "parcial", "pago"])
        observacoes = st.text_area("Observações", height=80)
    
    submitted = st.form_submit_button("💾 Salvar Gasto", type="primary")
    
    if submitted:
        if not categoria:
            st.error("Categoria é obrigatória.")
        elif not item:
            st.error("Item/Fornecedor é obrigatório.")
        elif orcamento < 0:
            st.error("Orçamento não pode ser negativo.")
        elif valor_pago < 0:
            st.error("Valor pago não pode ser negativo.")
        else:
            try:
                novo_gasto = {
                    "categoria": categoria,
                    "item": item,
                    "orcamento": orcamento,
                    "valor_pago": valor_pago,
                    "entrada": entrada,
                    "status": status,
                    "observacoes": observacoes
                }
                
                insert_gasto_casamento(novo_gasto)
                st.success("✅ Gasto salvo com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {str(e)}")

# ========== 5. EDIÇÃO/EXCLUSÃO ==========
if not df_casamento.empty:
    st.markdown("### ✏️ Editar/Excluir Gasto")
    
    # Seletor de gasto
    opcoes_gastos = [
        f"{row['categoria']} - {row['item']} ({format_currency(row['orcamento'])})"
        for _, row in df_casamento.iterrows()
    ]
    gasto_selecionado = st.selectbox("Selecione o gasto", opcoes_gastos, key="select_gasto_edit")
    
    if gasto_selecionado:
        idx = opcoes_gastos.index(gasto_selecionado)
        gasto_atual = df_casamento.iloc[idx]
        
        col_edit, col_delete = st.columns([3, 1])
        
        with col_edit:
            with st.form("form_editar_gasto"):
                st.markdown(f"**Editando: {gasto_atual['item']}**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    nova_categoria = st.text_input("Categoria", value=gasto_atual["categoria"])
                    novo_item = st.text_input("Item", value=gasto_atual["item"])
                
                with col2:
                    novo_orcamento = form_number_input(
                        "Orçamento",
                        value=float(gasto_atual["orcamento"])
                    )
                    novo_valor_pago = form_number_input(
                        "Valor Pago",
                        value=float(gasto_atual["valor_pago"])
                    )
                
                with col3:
                    nova_entrada = st.checkbox(
                        "É uma entrada?",
                        value=bool(gasto_atual["entrada"])
                    )
                    novo_status = st.selectbox(
                        "Status",
                        ["pendente", "parcial", "pago"],
                        index=["pendente", "parcial", "pago"].index(gasto_atual["status"])
                    )
                    novas_observacoes = st.text_area(
                        "Observações",
                        value=gasto_atual.get("observacoes", ""),
                        height=80
                    )
                
                submitted_edit = st.form_submit_button("💾 Atualizar", type="primary")
                
                if submitted_edit:
                    try:
                        dados_atualizados = {
                            "categoria": nova_categoria,
                            "item": novo_item,
                            "orcamento": novo_orcamento,
                            "valor_pago": novo_valor_pago,
                            "entrada": nova_entrada,
                            "status": novo_status,
                            "observacoes": novas_observacoes
                        }
                        
                        update_gasto_casamento(gasto_atual["id"], dados_atualizados)
                        st.success("✅ Gasto atualizado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
        
        with col_delete:
            st.markdown("**Excluir**")
            if st.button("🗑️ Deletar Gasto", type="secondary", key="btn_delete_gasto"):
                try:
                    delete_gasto_casamento(gasto_atual["id"])
                    st.success("✅ Gasto excluído!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")

# ========== 6. VISÃO POR CATEGORIA ==========
if not df_casamento.empty:
    st.markdown("### 📊 Gastos por Categoria")
    
    # Agrupar por categoria
    df_por_categoria = df_casamento.groupby("categoria").agg({
        "orcamento": "sum",
        "valor_pago": "sum"
    }).reset_index()
    
    df_por_categoria["restante"] = df_por_categoria["orcamento"] - df_por_categoria["valor_pago"]
    df_por_categoria["% gasto"] = (
        df_por_categoria["valor_pago"] / df_por_categoria["orcamento"] * 100
    ).round(1)
    
    # Formatar para exibição
    df_cat_display = df_por_categoria.copy()
    df_cat_display["orcamento"] = df_cat_display["orcamento"].apply(format_currency)
    df_cat_display["valor_pago"] = df_cat_display["valor_pago"].apply(format_currency)
    df_cat_display["restante"] = df_cat_display["restante"].apply(format_currency)
    df_cat_display["% gasto"] = df_cat_display["% gasto"].apply(lambda x: f"{x}%")
    
    st.dataframe(df_cat_display, use_container_width=True, height=300)
