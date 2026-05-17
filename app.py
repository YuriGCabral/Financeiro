"""
Clínica Financeira
Rode: streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from organizador.auth import init_auth_state, is_authenticated, logout
from organizador.login_ui import render_login_page
from organizador.store import STORE_PATH
from organizador.ui import (
    inject_dashboard_theme,
    page_header,
    sidebar_brand,
    ui_card,
)

st.set_page_config(page_title="Clínica Financeira", layout="wide", page_icon=":material/health_and_safety:")

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
    "Plantões, finanças e planejamento do casamento.",
    lucide="house",
)

with ui_card("Módulos", "Navegue pela barra lateral.", lucide="activity"):
    st.markdown(
        """
- **Plantões** — quantidades mensais, impostos e líquido
- **Finanças** — lançamentos do mês e custos fixos
- **Meu Casamento** — planejamento financeiro completo
        """
    )
