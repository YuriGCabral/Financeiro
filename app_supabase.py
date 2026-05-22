"""
Clínica Financeira - Reestruturado com Supabase
Rode: streamlit run app_supabase.py
"""

from __future__ import annotations

import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.login_ui import render_login_page
from organizador.ui import inject_dashboard_theme, page_header, sidebar_brand

st.set_page_config(
    page_title="Clínica Financeira",
    layout="wide",
    page_icon=":material/health_and_safety:"
)

inject_dashboard_theme()

# Autenticação
init_auth_state()

if not is_authenticated():
    render_login_page()
    st.stop()

# Se logado, mostra o app
sidebar_brand()

# Logout
with st.sidebar:
    st.markdown("---")
    if st.button("Sair", type="secondary", use_container_width=True):
        logout()
        st.rerun()

page_header(
    "Clínica Financeira",
    "Sistema integrado com Supabase para gestão completa.",
    lucide="house",
)

# Dashboard principal
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Módulos Disponíveis")
    st.markdown("""
    - **Plantões** — Registros mensais, impostos e valores líquidos
    - **Finanças** — Receitas, despesas e custos fixos automatizados
    - **Meu Casamento** — Orçamento completo e controle de pagamentos
    """)

st.info("Use a barra lateral para navegar entre os módulos.")
