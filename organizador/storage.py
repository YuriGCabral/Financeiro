"""Persistência no navegador usando localStorage."""

from __future__ import annotations

import hashlib
import streamlit as st


def _generate_auth_token(username: str) -> str:
    """Gera token hash do username."""
    return hashlib.sha256(username.encode()).hexdigest()[:32]


def get_stored_auth() -> tuple[str | None, str | None]:
    """Tenta recuperar login salvo no navegador."""
    # Guarda dados do localStorage no session_state
    if "_stored_auth_loaded" not in st.session_state:
        st.session_state._stored_auth_loaded = True
        st.session_state._stored_username = None
        st.session_state._stored_token = None
    
    # Injeta JavaScript que lê localStorage e salva no session_state via query params APENAS UMA VEZ
    if st.session_state._stored_username is None:
        # Primeira carga - verifica query params
        username_from_params = st.query_params.get('_su')
        token_from_params = st.query_params.get('_st')
        
        if username_from_params and token_from_params:
            # Salva no session_state
            st.session_state._stored_username = username_from_params
            st.session_state._stored_token = token_from_params
            
            st.query_params.clear()
        else:
            # JavaScript roda só uma vez para ler localStorage
            st.markdown(
                """
                <script>
                    (function() {
                        // Evita múltiplas execuções
                        if (window._auth_check_done) return;
                        window._auth_check_done = true;
                        
                        // Lê do localStorage
                        const username = localStorage.getItem('clinica_auth_user');
                        const token = localStorage.getItem('clinica_auth_token');
                        
                        // Se tem dados E não tem query params ainda
                        const urlParams = new URLSearchParams(window.location.search);
                        if (username && token && !urlParams.has('_su')) {
                            // Adiciona aos query params e recarrega
                            const url = new URL(window.location);
                            url.searchParams.set('_su', username);
                            url.searchParams.set('_st', token);
                            window.location.replace(url.toString());
                        }
                    })();
                </script>
                """,
                unsafe_allow_html=True,
            )
    
    return st.session_state._stored_username, st.session_state._stored_token


def save_auth_to_storage(username: str) -> None:
    """Salva login no localStorage do navegador."""
    token = _generate_auth_token(username)
    
    # Escapa caracteres especiais
    username_escaped = (
        username.replace('\\', '\\\\')
        .replace("'", "\\'")
        .replace('"', '\\"')
        .replace('\n', '\\n')
        .replace('\r', '\\r')
    )
    
    st.markdown(
        f"""
        <script>
            localStorage.setItem('clinica_auth_token', '{token}');
            localStorage.setItem('clinica_auth_user', '{username_escaped}');
            console.log('✓ Autenticação salva');
        </script>
        """,
        unsafe_allow_html=True,
    )


def clear_auth_from_storage() -> None:
    """Remove login do localStorage."""
    st.markdown(
        """
        <script>
            localStorage.removeItem('clinica_auth_token');
            localStorage.removeItem('clinica_auth_user');
            console.log('✓ Autenticação removida');
        </script>
        """,
        unsafe_allow_html=True,
    )


def validate_auth_token(username: str, stored_token: str | None) -> bool:
    """Valida se o token bate com o username."""
    if not stored_token or not username:
        return False
    
    expected_token = _generate_auth_token(username)
    return stored_token == expected_token
