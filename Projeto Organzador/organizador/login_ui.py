"""Tela de login."""

from __future__ import annotations

import streamlit as st

from organizador.auth import init_auth_state, login
from organizador.lucide import inline_svg


def render_login_page() -> None:
    """Mostra tela de login."""
    
    init_auth_state()
    
    # Se já restaurou do localStorage, nem mostra a tela
    if st.session_state.get("authenticated", False):
        return
    
    # CSS customizado
    st.markdown(
        """
        <style>
        /* Esconde sidebar e header */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Centraliza */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            padding-top: 2rem !important;
        }
        
        /* Estilo do card de login */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
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
            background: linear-gradient(135deg, rgba(244, 63, 94, 0.12), rgba(251, 113, 133, 0.1));
            border: 1px solid var(--pink-100);
            border-radius: 20px;
            box-shadow: var(--shadow-card);
        }
        
        .login-title {
            font-family: 'Poppins', sans-serif !important;
            font-size: 2rem;
            font-weight: 700;
            color: var(--pink-700);
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
            text-align: center;
        }
        
        .login-subtitle {
            font-size: 1rem;
            color: var(--text-secondary);
            margin: 0 0 2rem 0;
            font-weight: 500;
            text-align: center;
        }
        
        .login-footer {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--pink-100);
            text-align: center;
        }
        
        .login-footer-text {
            font-size: 0.875rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        
        /* Estiliza inputs */
        .stTextInput input {
            border-radius: var(--radius-control) !important;
            border: 1px solid var(--pink-100) !important;
            font-size: 1rem !important;
        }
        
        .stTextInput input:focus {
            border-color: var(--pink-600) !important;
            box-shadow: var(--focus-ring) !important;
        }
        
        /* Estiliza botão de login */
        .stButton > button[kind="primary"] {
            width: 100% !important;
            height: 48px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            border-radius: var(--radius-control) !important;
            background: linear-gradient(135deg, var(--pink-500), var(--pink-400)) !important;
            border: none !important;
        }
        
        /* Container do formulário */
        div[data-testid="stForm"] {
            background: var(--bg-card);
            border: 1px solid var(--pink-100);
            border-radius: var(--radius-card);
            box-shadow: var(--shadow-pink);
            padding: 3rem 2.5rem;
            max-width: 420px;
            margin: 0 auto;
        }
        
        /* Remove mensagens do form */
        .stForm [data-testid="InputInstructions"] {
            display: none !important;
        }
        
        .stForm [data-testid="stFormSubmitButton"] + div {
            display: none !important;
        }
        
        .stForm > div > div:last-child > div:last-child {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Layout centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
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
        
        # Erro se houver
        if st.session_state.get("login_error"):
            st.error(st.session_state.login_error)
        
        # Form de login
        with st.form(key="login_form"):
            username = st.text_input(
                "Usuário",
                placeholder="Digite seu nome de usuário",
                key="login_username",
            )
            
            password = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha",
                key="login_password",
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.session_state.login_error = "Preencha usuário e senha"
                    st.rerun()
                else:
                    success = login(username, password)
                    if success:
                        st.session_state.login_error = None
                        st.rerun()
                    else:
                        st.rerun()
        
        # Footer
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
