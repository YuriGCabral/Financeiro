"""Tela de login premium."""

from __future__ import annotations

import streamlit as st

from organizador.auth import init_auth_state, login
from organizador.lucide import inline_svg


def render_login_page() -> None:
    init_auth_state()

    if st.session_state.get("logado", False):
        return

    st.markdown(
        """
        <style>
        /* RESET */
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }

        /* CENTRALIZAÇÃO */
        .main .block-container {
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 0 !important;
        }

        /* CARD */
        .login-card {
            width: 100%;
            max-width: 420px;
            padding: 2.5rem 2.2rem;
            border-radius: 18px;
            background: var(--bg-card);
            border: 1px solid var(--pink-100);
            box-shadow: var(--shadow-pink);
            transition: all 0.25s ease;
        }

        .login-card:hover {
            transform: translateY(-2px);
        }

        /* HEADER */
        .login-header {
            text-align: center;
            margin-bottom: 2.2rem;
        }

        .login-icon {
            display: flex;
            justify-content: center;
            margin-bottom: 1.2rem;
        }

        .login-icon div {
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(244,63,94,0.12), rgba(251,113,133,0.1));
            border: 1px solid var(--pink-100);
            transition: all 0.25s ease;
        }

        .login-icon div:hover {
            transform: scale(1.05);
        }

        .login-title {
            font-size: 1.9rem;
            font-weight: 700;
            color: var(--pink-700);
            letter-spacing: -0.02em;
        }

        .login-subtitle {
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-top: 6px;
        }

        /* INPUT CONTAINER */
        div[data-baseweb="input"] {
            border-radius: 12px !important;
            border: 1px solid var(--pink-100) !important;
            background: white !important;
            height: 52px !important;
            display: flex !important;
            align-items: center !important;
            padding: 0 14px !important;
            transition: all 0.2s ease !important;
        }

        /* INPUT TEXTO */
        div[data-baseweb="input"] input {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            height: 100% !important;
            font-size: 1rem !important;
            background: transparent !important;
        }

        /* FOCO ANIMADO */
        div[data-baseweb="input"]:focus-within {
            border-color: var(--pink-500) !important;
            box-shadow: 0 0 0 3px rgba(244,63,94,0.15) !important;
            transform: scale(1.01);
        }

        /* HOVER SUAVE */
        div[data-baseweb="input"]:hover {
            border-color: var(--pink-300) !important;
        }

        /* ÍCONE SENHA */
        div[data-baseweb="input"] button {
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            opacity: 0.7;
            transition: opacity 0.2s ease;
        }

        div[data-baseweb="input"] button:hover {
            opacity: 1;
        }

        /* ESPAÇAMENTO */
        .stTextInput {
            margin-bottom: 1.2rem;
        }

        /* BOTÃO */
        button[kind="primary"] {
            width: 100% !important;
            height: 52px !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            background: linear-gradient(135deg, var(--pink-600), var(--pink-500)) !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(244,63,94,0.25) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(244,63,94,0.35) !important;
        }

        button[kind="primary"]:active {
            transform: translateY(0);
            box-shadow: 0 3px 10px rgba(244,63,94,0.2) !important;
        }

        /* FOOTER */
        .login-footer {
            margin-top: 1.6rem;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-secondary);
            opacity: 0.8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="login-header">
            <div class="login-icon">
                <div>{inline_svg("heart-pulse", 28)}</div>
            </div>
            <div class="login-title">Clínica Financeira</div>
            <div class="login-subtitle">Acesse sua conta</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)

    usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

    if st.button("Entrar", type="primary"):
        if not usuario or not senha:
            st.session_state.login_error = "Preencha usuário e senha"
        else:
            login(usuario, senha)
        st.rerun()

    st.markdown(
        f"""
        <div class="login-footer">
            {inline_svg("info", 14)} Acesso restrito
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)