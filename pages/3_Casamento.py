from __future__ import annotations

import pandas as pd
import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.financas_table import format_brl
from organizador.lucide import inline_svg
from organizador.store import load_store, save_store
from organizador.ui import (
    inject_dashboard_theme,
    page_header,
    render_kpi_row,
    sidebar_brand,
    table_wrap_begin,
    table_wrap_end,
    ui_card,
)

st.set_page_config(page_title="Meu Casamento", layout="wide", page_icon="💍")

inject_dashboard_theme()

# Autenticação
init_auth_state()
if not is_authenticated():
    st.warning("Você precisa fazer login primeiro.")
    st.info("Por favor, volte para a página inicial e faça login.")
    st.stop()

sidebar_brand()

# Logout
with st.sidebar:
    st.markdown("---")
    if st.button("Sair", type="secondary", use_container_width=True, key="logout_casamento"):
        logout()
        st.rerun()

page_header(
    "Meu Casamento",
    "Planejamento financeiro completo do casamento — orçamento, valores fechados e controle de pagamentos.",
    lucide="heart",
)

# Inicialização
if "casamento_initialized" not in st.session_state:
    st.session_state.casamento_initialized = True
    store = load_store()
    
    raw_casamento = store.get("casamento", [])
    if not isinstance(raw_casamento, list):
        raw_casamento = []
    
    # Só cria itens padrão na primeira vez
    casamento_user_initialized = store.get("casamento_user_initialized", False)
    
    if not raw_casamento and not casamento_user_initialized:
        # Cria dados iniciais
        st.session_state.casamento_data = [
            {
                "titulo": "Buffet",
                "categoria": "Alimentação",
                "orcamento": 15000.0,
                "valor_fechado": 0.0,
                "parcelas": 1,
                "pago": False,
            },
            {
                "titulo": "Decoração",
                "categoria": "Decoração",
                "orcamento": 8000.0,
                "valor_fechado": 0.0,
                "parcelas": 1,
                "pago": False,
            },
            {
                "titulo": "Fotografia",
                "categoria": "Foto/Vídeo",
                "orcamento": 5000.0,
                "valor_fechado": 0.0,
                "parcelas": 1,
                "pago": False,
            },
        ]
    else:
        # Garante que todos os registros têm categoria
        for item in raw_casamento:
            if "categoria" not in item:
                item["categoria"] = "Outros"
        st.session_state.casamento_data = raw_casamento.copy()

# Categorias disponíveis
CATEGORIAS = [
    "Alimentação",
    "Decoração",
    "Foto/Vídeo",
    "Local",
    "Música/DJ",
    "Convites",
    "Vestimenta",
    "Beleza",
    "Lua de Mel",
    "Documentação",
    "Outros",
]

# Prepara tabela
casamento_data = st.session_state.casamento_data
if casamento_data:
    rows = []
    for r in casamento_data:
        rows.append({
            "Fornecedor/Item": str(r.get("titulo", "")),
            "Categoria": str(r.get("categoria", "Outros")),
            "Orçamento (R$)": float(r.get("orcamento", 0.0)),
            "Valor Fechado (R$)": float(r.get("valor_fechado", 0.0)),
            "Parcelas": int(r.get("parcelas", 1)),
            "✓ Pago": bool(r.get("pago", False)),
        })
    df_casamento = pd.DataFrame(rows)
else:
    df_casamento = pd.DataFrame([{
        "Fornecedor/Item": "",
        "Categoria": "Outros",
        "Orçamento (R$)": 0.0,
        "Valor Fechado (R$)": 0.0,
        "Parcelas": 1,
        "✓ Pago": False,
    }])

# Garante tipos corretos
df_casamento["Orçamento (R$)"] = pd.to_numeric(df_casamento["Orçamento (R$)"], errors="coerce").fillna(0.0)
df_casamento["Valor Fechado (R$)"] = pd.to_numeric(df_casamento["Valor Fechado (R$)"], errors="coerce").fillna(0.0)
df_casamento["Parcelas"] = pd.to_numeric(df_casamento["Parcelas"], errors="coerce").fillna(1).astype(int).clip(1, 100)
df_casamento["✓ Pago"] = df_casamento["✓ Pago"].astype(bool)
df_casamento["Fornecedor/Item"] = df_casamento["Fornecedor/Item"].astype(str)
df_casamento["Categoria"] = df_casamento["Categoria"].astype(str)

with ui_card("Orçamento do Casamento", "Gerencie fornecedores, valores e pagamentos.", lucide="clipboard-list"):
    help_html = f'<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;"><span style="color: var(--text-secondary); font-size: 0.875rem;">{inline_svg("info", 16)} <strong>Orçamento</strong> = valor estimado | <strong>Valor Fechado</strong> = contrato assinado | <strong>Parcelas</strong> = quantidade de pagamentos</span></div>'
    st.markdown(help_html, unsafe_allow_html=True)
    
    with st.form(key="form_casamento"):
        table_wrap_begin()
        edited_casamento = st.data_editor(
            df_casamento,
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            column_config={
                "Fornecedor/Item": st.column_config.TextColumn(
                    "Fornecedor/Item",
                    width="medium",
                    required=True,
                    help="Nome do fornecedor ou item (ex: Buffet Dom Bosco, Fotógrafo João)",
                ),
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=CATEGORIAS,
                    required=True,
                    default="Outros",
                    help="Categoria da despesa",
                    width="small",
                ),
                "Orçamento (R$)": st.column_config.NumberColumn(
                    "Orçamento (R$)",
                    min_value=0.0,
                    max_value=1000000.0,
                    format="%.2f",
                    step=100.0,
                    required=True,
                    help="Valor inicial orçado/estimado",
                    width="small",
                ),
                "Valor Fechado (R$)": st.column_config.NumberColumn(
                    "Valor Fechado (R$)",
                    min_value=0.0,
                    max_value=1000000.0,
                    format="%.2f",
                    step=100.0,
                    required=True,
                    help="Valor real do contrato assinado (0 = ainda não fechou)",
                    width="small",
                ),
                "Parcelas": st.column_config.NumberColumn(
                    "Parcelas",
                    min_value=1,
                    max_value=100,
                    step=1,
                    format="%d",
                    help="Quantidade de parcelas do pagamento",
                    width="small",
                ),
                "✓ Pago": st.column_config.CheckboxColumn(
                    "✓ Pago",
                    help="Marque quando o pagamento estiver completo",
                    default=False,
                    width="small",
                ),
            },
            key="casamento_editor_v3",
        )
        table_wrap_end()
        
        submitted = st.form_submit_button("Salvar alterações", type="primary", use_container_width=False)
        
        if submitted:
            # Converte para records
            records_casamento = []
            for idx, row in edited_casamento.iterrows():
                categoria = str(row.get("Categoria", "Outros"))
                if categoria not in CATEGORIAS:
                    categoria = "Outros"
                
                records_casamento.append({
                    "titulo": str(row.get("Fornecedor/Item", "")).strip(),
                    "categoria": categoria,
                    "orcamento": float(row.get("Orçamento (R$)", 0.0)),
                    "valor_fechado": float(row.get("Valor Fechado (R$)", 0.0)),
                    "parcelas": int(row.get("Parcelas", 1)),
                    "pago": bool(row.get("✓ Pago", False)),
                })
            
            # Cria nova estrutura
            new_casamento = records_casamento.copy()
            
            # Substitui no session_state
            st.session_state.casamento_data = new_casamento
            
            # Persiste
            store = load_store()
            store["casamento"] = new_casamento
            store["casamento_user_initialized"] = True  # Marca que usuário já salvou dados
            save_store(store)
            
            st.success("Orçamento do casamento salvo com sucesso!")
            st.rerun()

# === CÁLCULOS E TOTAIS (somente leitura dos dados salvos) ===
display_data = st.session_state.casamento_data
if display_data:
    display_rows = []
    for r in display_data:
        display_rows.append({
            "Fornecedor/Item": str(r.get("titulo", "")),
            "Categoria": str(r.get("categoria", "Outros")),
            "Orçamento (R$)": float(r.get("orcamento", 0.0)),
            "Valor Fechado (R$)": float(r.get("valor_fechado", 0.0)),
            "Parcelas": int(r.get("parcelas", 1)),
            "✓ Pago": bool(r.get("pago", False)),
        })
    df_display = pd.DataFrame(display_rows)
else:
    df_display = pd.DataFrame([{
        "Fornecedor/Item": "",
        "Categoria": "Outros",
        "Orçamento (R$)": 0.0,
        "Valor Fechado (R$)": 0.0,
        "Parcelas": 1,
        "✓ Pago": False,
    }])

# Total orçado
total_orcamento = df_display["Orçamento (R$)"].sum()

# Total fechado (contratos assinados)
total_fechado = df_display["Valor Fechado (R$)"].sum()

# Total pago (itens marcados como pagos)
df_pagos = df_display[df_display["✓ Pago"] == True]
total_pago = df_pagos["Valor Fechado (R$)"].sum()

# A pagar (fechados mas não pagos)
df_a_pagar = df_display[(df_display["Valor Fechado (R$)"] > 0) & (df_display["✓ Pago"] == False)]
total_a_pagar = df_a_pagar["Valor Fechado (R$)"].sum()

# Diferença orçamento vs fechado
diferenca = total_fechado - total_orcamento

# Itens não fechados ainda
itens_nao_fechados = len(df_display[df_display["Valor Fechado (R$)"] == 0])
itens_totais = len(df_display)
itens_fechados = itens_totais - itens_nao_fechados

with ui_card("Resumo Financeiro", "Visão geral do investimento no casamento.", lucide="bar-chart-3"):
    render_kpi_row(
        ("Orçamento Total", format_brl(total_orcamento), ""),
        ("Total Fechado", format_brl(total_fechado), "accent" if total_fechado > 0 else ""),
        ("Total Pago", format_brl(total_pago), "pos" if total_pago > 0 else ""),
    )
    
    render_kpi_row(
        ("A Pagar", format_brl(total_a_pagar), "neg" if total_a_pagar > 0 else ""),
        ("Variação", format_brl(diferenca), "pos" if diferenca <= 0 else "neg"),
        ("Contratos", f"{itens_fechados}/{itens_totais}", "accent"),
    )

# Resumo por categoria
with ui_card("Resumo por Categoria", "Distribuição de gastos por categoria.", lucide="folder-open"):
    if len(df_display) > 0 and df_display["Valor Fechado (R$)"].sum() > 0:
        # Agrupa por categoria
        cat_summary = df_display.groupby("Categoria").agg({
            "Orçamento (R$)": "sum",
            "Valor Fechado (R$)": "sum",
        }).reset_index()
        
        # Remove categorias sem valores
        cat_summary = cat_summary[(cat_summary["Orçamento (R$)"] > 0) | (cat_summary["Valor Fechado (R$)"] > 0)]
        
        # Ordena por valor fechado (decrescente)
        cat_summary = cat_summary.sort_values("Valor Fechado (R$)", ascending=False)
        
        # Formata valores
        cat_summary["Orçamento (R$)"] = cat_summary["Orçamento (R$)"].apply(lambda x: format_brl(x))
        cat_summary["Valor Fechado (R$)"] = cat_summary["Valor Fechado (R$)"].apply(lambda x: format_brl(x))
        
        table_wrap_begin()
        st.dataframe(
            cat_summary,
            width="stretch",
            hide_index=True,
            height=min(400, 80 + 32 * len(cat_summary)),
        )
        table_wrap_end()
    else:
        info_html = f'<div style="display: flex; align-items: center; gap: 8px; padding: 12px; background: var(--pink-50); border: 1px solid var(--pink-200); border-radius: 8px;"><span>{inline_svg("info", 18)}</span><span style="color: var(--text-secondary);">Adicione itens com valores fechados para ver o resumo por categoria.</span></div>'
        st.markdown(info_html, unsafe_allow_html=True)

# Detalhes adicionais
with ui_card("Análise Detalhada", "Status e métricas do planejamento.", lucide="info"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;"><span>{inline_svg("clipboard-list", 20)}</span><span style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary);">Status dos Itens</span></div>', unsafe_allow_html=True)
        
        if itens_nao_fechados > 0:
            st.warning(f"**{itens_nao_fechados} itens** ainda sem contrato fechado")
        else:
            st.success("Todos os contratos fechados!")
        
        if total_a_pagar > 0:
            st.info(f"**{len(df_a_pagar)} fornecedores** aguardando pagamento")
        else:
            st.success("Todos os pagamentos em dia!")
    
    with col2:
        st.markdown(f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;"><span>{inline_svg("calculator", 20)}</span><span style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary);">Análise de Gastos</span></div>', unsafe_allow_html=True)
        
        if total_fechado > 0:
            percentual_pago = (total_pago / total_fechado) * 100
            st.metric(
                "Progresso de Pagamento",
                f"{percentual_pago:.1f}%",
                delta=None,
            )
        
        if total_orcamento > 0 and total_fechado > 0:
            percentual_variacao = ((total_fechado - total_orcamento) / total_orcamento) * 100
            delta_txt = f"{percentual_variacao:+.1f}% do orçamento"
            st.metric(
                "Variação do Orçamento",
                format_brl(diferenca),
                delta=delta_txt,
                delta_color="inverse",
            )
