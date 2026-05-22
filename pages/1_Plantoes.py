from __future__ import annotations

import pandas as pd
import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.financas_table import format_brl
from organizador.plantoes import dataframe_resumo
from organizador.ui import (
    inject_dashboard_theme,
    page_header,
    render_kpi_row,
    sidebar_brand,
    table_wrap_begin,
    table_wrap_end,
    ui_card,
)
from services.plantoes_service import load_plantoes, insert_plantao, update_plantao

st.set_page_config(page_title="Plantões", layout="wide", page_icon=":material/medical_services:")

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
    if st.button("Sair", type="secondary", use_container_width=True, key="logout_plantoes"):
        logout()
        st.rerun()

page_header(
    "Plantões e impostos",
    "656,40 por plantão · ISS 5% · INSS 11% (teto) · IRRF progressivo 2026.",
    lucide="stethoscope",
)

# Inicialização (só uma vez)
if "plantoes_initialized" not in st.session_state:
    st.session_state.plantoes_initialized = True
    try:
        df_plantoes = load_plantoes()
        # Converte DataFrame para estrutura esperada {ano: {meses: [...], quantidades: [...]}}
        plantoes_dict = {}
        if not df_plantoes.empty:
            for ano in df_plantoes["ano"].unique():
                df_ano = df_plantoes[df_plantoes["ano"] == ano].sort_values("mes")
                meses_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                quantidades_list = [0] * 12
                for _, row in df_ano.iterrows():
                    mes_idx = int(row["mes"]) - 1
                    quantidades_list[mes_idx] = int(row["quantidade"])
                plantoes_dict[int(ano)] = {"meses": meses_list, "quantidades": quantidades_list}
        else:
            plantoes_dict = {2026: {"meses": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                                   "quantidades": [0] * 12}}
        st.session_state.plantoes_data = plantoes_dict
        st.session_state.selected_year = sorted(plantoes_dict.keys(), reverse=True)[0]
    except Exception as e:
        st.error(f"Erro ao carregar plantões: {e}")
        st.session_state.plantoes_data = {2026: {"meses": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                                           "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                                                 "quantidades": [0] * 12}}
        st.session_state.selected_year = 2026

# Seleção de ano
years = sorted(st.session_state.plantoes_data.keys(), reverse=True)

with ui_card("Quantidades por mês", "Edite os plantões e clique em Salvar.", lucide="calendar"):
    y1, y2 = st.columns([1, 2])
    with y1:
        selected_year = st.selectbox("Ano", options=years, index=years.index(st.session_state.selected_year), label_visibility="visible")
        if selected_year != st.session_state.selected_year:
            st.session_state.selected_year = selected_year
            st.rerun()

    aba = st.session_state.selected_year
    block = st.session_state.plantoes_data[aba]
    meses = list(block["meses"])
    quantidades = [float(x or 0) for x in block["quantidades"]]
    df_pl = pd.DataFrame({"Mês": meses, "Plantões": quantidades})

    # Form com editor
    with st.form(key=f"form_plantoes_{aba}"):
        table_wrap_begin()
        df_edit = st.data_editor(
            df_pl,
            num_rows="fixed",
            width="stretch",
            column_config={
                "Mês": st.column_config.TextColumn("Mês", disabled=True),
                "Plantões": st.column_config.NumberColumn("Plantões", min_value=0, step=1, format="%d"),
            },
            key=f"editor_plantoes_{aba}",
        )
        table_wrap_end()
        
        submitted = st.form_submit_button("Salvar alterações", type="primary")
        
        if submitted:
            try:
                plantoes_list = [float(x or 0) for x in df_edit["Plantões"].tolist()]
                meses_list = df_edit["Mês"].astype(str).tolist()
                
                # Atualiza dados no session_state
                new_data = st.session_state.plantoes_data.copy()
                new_data[aba] = {
                    "meses": meses_list,
                    "quantidades": plantoes_list
                }
                st.session_state.plantoes_data = new_data
                
                # Persiste no Supabase (salva cada mês)
                for mes_idx, quantidade in enumerate(plantoes_list):
                    mes_num = mes_idx + 1
                    if quantidade > 0:
                        # Verifica se já existe
                        df_existing = load_plantoes(ano=aba)
                        existing_row = df_existing[(df_existing["ano"] == aba) & (df_existing["mes"] == mes_num)]
                        
                        # Calcula valores
                        valor_bruto = quantidade * 656.40
                        imposto = valor_bruto * 0.05
                        valor_liquido = valor_bruto - imposto
                        
                        plantao_data = {
                            "ano": aba,
                            "mes": mes_num,
                            "quantidade": int(quantidade),
                            "valor_bruto": valor_bruto,
                            "imposto": imposto,
                            "valor_liquido": valor_liquido,
                            "entrada": False
                        }
                        
                        if not existing_row.empty:
                            update_plantao(int(existing_row.iloc[0]["id"]), plantao_data)
                        else:
                            insert_plantao(plantao_data)
                
                st.success("✅ Plantões salvos com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

# === RENDERIZAÇÃO (leitura apenas) ===
block = st.session_state.plantoes_data[aba]
plantoes_list = [float(x or 0) for x in block["quantidades"]]
meses_list = list(block["meses"])

resumo = dataframe_resumo(plantoes_list, meses_list)
fmt = {
    "Plantões": "{:.0f}",
    "Valor bruto": "R$ {:,.2f}",
    "ISS": "R$ {:,.2f}",
    "INSS": "R$ {:,.2f}",
    "IRRF": "R$ {:,.2f}",
    "Líquido": "R$ {:,.2f}",
}

with ui_card("Resumo fiscal", "Visão consolidada por mês.", lucide="calculator"):
    table_wrap_begin()
    try:
        st.dataframe(resumo.style.format(fmt), width="stretch", height=min(520, 120 + 28 * len(resumo)))
    except Exception:
        st.dataframe(resumo, width="stretch", height=min(520, 120 + 28 * len(resumo)))
    table_wrap_end()

tot = resumo[["Valor bruto", "ISS", "INSS", "IRRF", "Líquido"]].sum()
render_kpi_row(
    ("Total líquido (soma dos meses)", format_brl(float(tot["Líquido"])), "accent"),
)
