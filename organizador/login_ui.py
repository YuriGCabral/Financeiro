"""Tela de login."""

from __future__ import annotations

import streamlit as st

from organizador.auth import init_auth_state, login
from organizador.lucide import inline_svg


def render_login_page() -> None:
    """Mostra tela de login."""
    
    init_auth_state()
    
    if st.session_state.get("logado", False):
        return
    
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }

        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            padding-top: 2rem !important;
        }

        .login-header { text-align: center; margin-bottom: 2rem; }

        .login-icon-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }

        .login-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, rgba(244,63,94,0.12), rgba(251,113,133,0.1));
            border: 1px solid var(--pink-100);
            border-radius: 20px;
        }

        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--pink-700);
            text-align: center;
        }

        .login-subtitle {
            font-size: 1rem;
            color: var(--text-secondary);
            text-align: center;
            margin-bottom: 2rem;
        }

        .stTextInput input {
            border-radius: var(--radius-control) !important;
            border: 1px solid var(--pink-100) !important;
        }

        .stTextInput input:focus {
            border-color: var(--pink-600) !important;
            box-shadow: var(--focus-ring) !important;
        }

        button[kind="primary"] {
            width: 100% !important;
            height: 52px !important;
            font-size: 1.1rem !important;
            border-radius: var(--radius-control) !important;
            background: linear-gradient(135deg, var(--pink-600), var(--pink-500)) !important;
            border: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Header
    st.markdown(
        f"""
        <div class="login-header">
            <div class="login-icon-container">
                <div class="login-icon">
                    {inline_svg("heart-pulse", 32)}
                </div>
            </div>
            <h1 class="login-title">Clínica Financeira</h1>
            <p class="login-subtitle">Acesse sua conta para continuar</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)
    
    # 🔥 SEM FORM (acabou o problema)
    usuario = st.text_input("Usuário", placeholder="Digite seu nome de usuário")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

    if st.button("Entrar", type="primary", use_container_width=True):
        if not usuario or not senha:
            st.session_state.login_error = "Preencha usuário e senha"
        else:
            login(usuario, senha)
        st.rerun()
    
    st.markdown(
        f"""
        <div class="login-footer">
            <div class="login-footer-text">
                {inline_svg("info", 16)}
                <span>Acesso restrito a usuários autorizados</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )