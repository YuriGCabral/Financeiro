from __future__ import annotations

import pandas as pd
import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.custos_fixos import (
    COL_ANO,
    COL_MES,
    COL_PARCELAS,
    LABEL_FIXO,
    LABEL_PARCELADO,
    automaticas_para_df,
    custos_fixos_records_to_df,
    df_to_custos_fixos_records,
    ensure_custos_fixos_editor_df,
    filter_custos_fixos_records,
    linhas_automaticas_mes,
)
from organizador.financas_table import (
    compute_totals_two,
    ensure_tipo_column,
    format_brl,
)
from organizador.store import DEFAULT_MONTHS_PT, financas_key
from organizador.ui import (
    empty_state,
    inject_dashboard_theme,
    page_header,
    render_kpi_row,
    sidebar_brand,
    table_wrap_begin,
    table_wrap_end,
    ui_card,
)
from services.financas_service import load_financas, insert_financa, update_financa, delete_financa
from services.custos_fixos_service import load_custos_fixos, insert_custo_fixo, update_custo_fixo, delete_custo_fixo

st.set_page_config(page_title="Finanças", layout="wide", page_icon=":material/account_balance_wallet:")

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
    if st.button("Sair", type="secondary", use_container_width=True, key="logout_financas"):
        logout()
        st.rerun()

page_header(
    "Finanças do mês",
    "Lançamentos manuais, recorrências automáticas e totais unificados.",
    lucide="wallet",
)

# Inicialização
if "financas_initialized" not in st.session_state:
    st.session_state.financas_initialized = True
    try:
        # Carrega finanças do Supabase e converte para formato esperado {key: [...]}
        df_financas = load_financas()
        financas_dict = {}
        if not df_financas.empty:
            for _, row in df_financas.iterrows():
                key = financas_key(int(row["ano"]), int(row["mes"]))
                if key not in financas_dict:
                    financas_dict[key] = []
                financas_dict[key].append({
                    "id": int(row["id"]),
                    "titulo": str(row["descricao"]),
                    "valor": float(row["valor"]),
                    "tipo": "Receita" if row["tipo"] == "receita" else "Despesa",
                    "resolvido": False
                })
        st.session_state.financas_data = financas_dict
        
        # Carrega custos fixos
        df_custos = load_custos_fixos()
        custos_list = []
        if not df_custos.empty:
            for _, row in df_custos.iterrows():
                custos_list.append({
                    "id": int(row["id"]),
                    "titulo": str(row["descricao"]),
                    "valor": float(row["valor"]),
                    "tipo_receita_despesa": "Receita" if row["tipo"] == "receita" else "Despesa",
                    "modo": LABEL_FIXO if row["tipo"] == "fixo" else LABEL_PARCELADO,
                    COL_MES: int(row.get("dia_vencimento", 1)),
                    COL_ANO: 2026,
                    COL_PARCELAS: int(row.get("total_parcelas", 0))
                })
        st.session_state.custos_fixos_data = custos_list
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.session_state.financas_data = {}
        st.session_state.custos_fixos_data = []
    
    st.session_state.selected_mes_idx = 4
    st.session_state.selected_ano = 2026

# Seleção de período
with ui_card("Período", "Mês e ano dos lançamentos manuais desta tela.", lucide="calendar"):
    c_mes, c_ano = st.columns([2, 1])
    with c_mes:
        mes_idx = st.selectbox(
            "Mês",
            options=list(range(12)),
            format_func=lambda i: DEFAULT_MONTHS_PT[i],
            index=st.session_state.selected_mes_idx,
        )
        if mes_idx != st.session_state.selected_mes_idx:
            st.session_state.selected_mes_idx = mes_idx
            st.rerun()
    
    with c_ano:
        ano = st.selectbox("Ano", options=list(range(2026, 2031)), index=st.session_state.selected_ano - 2026)
        if ano != st.session_state.selected_ano:
            st.session_state.selected_ano = ano
            st.rerun()

mes_num = int(st.session_state.selected_mes_idx) + 1
ano = int(st.session_state.selected_ano)
key = financas_key(ano, mes_num)
st.caption(f"Período ativo: **{DEFAULT_MONTHS_PT[mes_idx]} de {ano}**")

# Custos fixos e parcelados
with st.expander("Custos fixos e parcelados (todos os meses)", expanded=False):
    st.caption(
        ""
    )
    
    cf_raw = st.session_state.custos_fixos_data
    if not isinstance(cf_raw, list):
        cf_raw = []
    
    df_cf = ensure_custos_fixos_editor_df(custos_fixos_records_to_df(cf_raw))
    
    with st.form(key="form_custos_fixos"):
        table_wrap_begin()
        cf_edited = st.data_editor(
            df_cf,
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            key="cf_editor_v5",
            column_config={
                "Título": st.column_config.TextColumn("Título", width="large"),
                "Valor (R$)": st.column_config.NumberColumn("Valor (R$)", min_value=0.0, format="%.2f", step=0.01),
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=["Receita", "Despesa"],
                    required=True,
                    default="Despesa",
                ),
                "Modo": st.column_config.SelectboxColumn(
                    "Modo",
                    options=[LABEL_FIXO, LABEL_PARCELADO],
                    required=True,
                    default=LABEL_FIXO,
                ),
                COL_MES: st.column_config.SelectboxColumn(
                    "Mês",
                    options=list(range(1, 13)),
                    format_func=lambda m: DEFAULT_MONTHS_PT[m - 1],
                    required=True,
                    help="Mês de início da cobrança (parcelado).",
                ),
                COL_ANO: st.column_config.NumberColumn(
                    "Ano",
                    min_value=2000,
                    max_value=2100,
                    step=1,
                    help="Ano de início da cobrança (parcelado).",
                ),
                COL_PARCELAS: st.column_config.NumberColumn(
                    "Parcelas",
                    min_value=0,
                    max_value=20,
                    step=1,
                    help="Quantidade de meses com cobrança (1–20). Em fixo, deixe 0.",
                ),
            },
        )
        table_wrap_end()
        
        submitted_cf = st.form_submit_button("Salvar alterações", type="primary")
        
        if submitted_cf:
            try:
                cf_edited = ensure_custos_fixos_editor_df(cf_edited)
                cf_recs = filter_custos_fixos_records(df_to_custos_fixos_records(cf_edited))
                
                # Atualiza session_state
                st.session_state.custos_fixos_data = cf_recs.copy()
                
                # Persiste no Supabase
                # Primeiro deleta todos os existentes (simplificação)
                df_existing = load_custos_fixos()
                for _, row in df_existing.iterrows():
                    delete_custo_fixo(int(row["id"]))
                
                # Insere os novos
                for rec in cf_recs:
                    custo_data = {
                        "descricao": rec["titulo"],
                        "tipo": "fixo" if rec.get("modo") == "fixo" else "parcelado",
                        "valor": float(rec["valor"]),
                        "entrada": False,
                        "dia_vencimento": int(rec.get(COL_MES, 1)),
                        "parcela_atual": 1,
                        "total_parcelas": int(rec.get(COL_PARCELAS, 0)),
                        "ativo": True
                    }
                    insert_custo_fixo(custo_data)
                
                st.success("✅ Custos fixos salvos!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

# === RECORRÊNCIAS DESTE MÊS (somente leitura) ===
cf_recs = st.session_state.custos_fixos_data
linhas_auto = linhas_automaticas_mes(cf_recs, int(ano), int(mes_num))
auto_df = automaticas_para_df(linhas_auto)

with ui_card("Recorrências neste mês", "Geradas a partir de custos fixos ou parcelados.", lucide="receipt"):
    if linhas_auto:
        table_wrap_begin()
        st.dataframe(auto_df, width="stretch", hide_index=True, height=min(360, 80 + 32 * len(auto_df)))
        table_wrap_end()
    else:
        empty_state(
            "Nada recorrente neste mês",
            'Nenhum custo fixo ou parcela entra neste período. Ajuste o cadastro em "Custos fixos e parcelados".',
            lucide="receipt",
        )

# === LANÇAMENTOS DO MÊS ===
raw_lancamentos = st.session_state.financas_data.get(key, [])
if not isinstance(raw_lancamentos, list):
    raw_lancamentos = []

# Prepara DataFrame
if raw_lancamentos:
    rows = []
    for r in raw_lancamentos:
        rows.append({
            "Título": str(r.get("titulo", "")),
            "Valor (R$)": float(r.get("valor", 0.0)),
            "Tipo": r.get("tipo", "Despesa") if r.get("tipo") in ("Receita", "Despesa") else "Despesa",
            "Resolvido": bool(r.get("resolvido", False)),
        })
    df_lancamentos = pd.DataFrame(rows)
else:
    df_lancamentos = pd.DataFrame([{
        "Título": "",
        "Valor (R$)": 0.0,
        "Tipo": "Despesa",
        "Resolvido": False,
    }])

# Garante tipos
df_lancamentos["Valor (R$)"] = pd.to_numeric(df_lancamentos["Valor (R$)"], errors="coerce").fillna(0.0)
df_lancamentos["Resolvido"] = df_lancamentos["Resolvido"].astype(bool)
df_lancamentos["Tipo"] = df_lancamentos["Tipo"].astype(str)

with ui_card("Lançamentos do mês", "Adicione receitas e despesas e clique em Salvar.", lucide="dollar-sign"):
    st.caption("💡 Use Tab ou Enter para confirmar e passar para próxima célula")
    
    with st.form(key=f"form_lancamentos_{key}"):
        table_wrap_begin()
        
        edited_lancamentos = st.data_editor(
            df_lancamentos,
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            column_config={
                "Título": st.column_config.TextColumn(
                    "Título",
                    width="large",
                    required=False,
                ),
                "Valor (R$)": st.column_config.NumberColumn(
                    "Valor (R$)",
                    min_value=0.0,
                    max_value=1000000.0,
                    format="%.2f",
                    step=0.01,
                    required=True,
                ),
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=["Receita", "Despesa"],
                    required=True,
                ),
                "Resolvido": st.column_config.CheckboxColumn(
                    "Resolvido",
                    help="Marque quando a despesa foi paga ou receita recebida",
                ),
            },
            key=f"lancamentos_editor_{key}",
        )
        
        table_wrap_end()
        
        submitted_lanc = st.form_submit_button("Salvar alterações", type="primary")
        
        if submitted_lanc:
            try:
                # Garante tipo correto
                edited_lancamentos = ensure_tipo_column(edited_lancamentos)
                
                # Converte para records
                records_para_salvar = []
                for idx, row in edited_lancamentos.iterrows():
                    records_para_salvar.append({
                        "titulo": str(row.get("Título", "")).strip(),
                        "valor": float(row.get("Valor (R$)", 0.0)),
                        "tipo": str(row.get("Tipo", "Despesa")),
                        "resolvido": bool(row.get("Resolvido", False)),
                    })
                
                # Atualiza session_state
                new_financas = st.session_state.financas_data.copy()
                new_financas[key] = records_para_salvar
                st.session_state.financas_data = new_financas
                
                # Persiste no Supabase
                # Deleta lançamentos antigos deste mês
                df_existing = load_financas(ano=ano, mes=mes_num)
                for _, row in df_existing.iterrows():
                    delete_financa(int(row["id"]))
                
                # Insere novos lançamentos
                for rec in records_para_salvar:
                    if rec["titulo"].strip():  # Só salva se tiver título
                        financa_data = {
                            "ano": ano,
                            "mes": mes_num,
                            "data": f"{ano}-{mes_num:02d}-01",
                            "descricao": rec["titulo"],
                            "tipo": "receita" if rec["tipo"] == "Receita" else "despesa",
                            "valor": float(rec["valor"]),
                            "entrada": False,
                            "categoria": "Manual"
                        }
                        insert_financa(financa_data)
                
                st.success("✅ Lançamentos salvos!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

# === TOTAIS (somente leitura) ===
# Recarrega os dados salvos para exibição
display_lancamentos = st.session_state.financas_data.get(key, [])
if display_lancamentos:
    display_rows = []
    for r in display_lancamentos:
        display_rows.append({
            "Título": str(r.get("titulo", "")),
            "Valor (R$)": float(r.get("valor", 0.0)),
            "Tipo": r.get("tipo", "Despesa") if r.get("tipo") in ("Receita", "Despesa") else "Despesa",
            "Resolvido": bool(r.get("resolvido", False)),
        })
    df_display = pd.DataFrame(display_rows)
    df_display = ensure_tipo_column(df_display)
else:
    df_display = pd.DataFrame([{
        "Título": "",
        "Valor (R$)": 0.0,
        "Tipo": "Despesa",
        "Resolvido": False,
    }])
    df_display = ensure_tipo_column(df_display)

rec_t, des_t, saldo = compute_totals_two(df_display, auto_df)

with ui_card("Totais", "Receitas e despesas incluem lançamentos manuais + recorrências.", lucide="trending-up"):
    saldo_variant = "pos" if saldo >= 0 else "neg"
    render_kpi_row(
        ("Receitas", format_brl(rec_t), ""),
        ("Despesas", format_brl(des_t), ""),
        ("Saldo (R − D)", format_brl(saldo), saldo_variant),
    )

pend = 0.0
for _, row in df_display.iterrows():
    if not bool(row.get("Resolvido", False)):
        pend += float(row.get("Valor (R$)", 0.0))
st.caption(
    f'Pendente manual (sem "Resolvido"): **{format_brl(pend)}** — não inclui recorrências automáticas.'
)
