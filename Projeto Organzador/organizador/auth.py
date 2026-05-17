"""Sistema de autenticação."""

from __future__ import annotations

import streamlit as st

from organizador.storage import (
    clear_auth_from_storage,
    get_stored_auth,
    save_auth_to_storage,
    validate_auth_token,
)

VALID_USERNAME = "Carol Gomes"
VALID_PASSWORD = "Thalis2002@"


def init_auth_state() -> None:
    """Inicializa autenticação e tenta restaurar sessão salva."""
    if "auth_initialized" not in st.session_state:
        st.session_state.auth_initialized = True
        st.session_state.authenticated = False
        st.session_state.login_error = None
        
        # Tenta recuperar autenticação salva
        stored_username, stored_token = get_stored_auth()
        
        # Se encontrou dados salvos, valida e restaura sessão
        if stored_username and stored_token:
            if validate_auth_token(stored_username, stored_token) and stored_username == VALID_USERNAME:
                st.session_state.authenticated = True
                st.session_state.current_user = stored_username


def authenticate(username: str, password: str) -> bool:
    """Valida usuário e senha."""
    return username == VALID_USERNAME and password == VALID_PASSWORD


def login(username: str, password: str) -> bool:
    """Faz login e salva sessão no navegador."""
    if authenticate(username, password):
        st.session_state.authenticated = True
        st.session_state.current_user = username
        st.session_state.login_error = None
        
        # Salva no localStorage para persistência
        save_auth_to_storage(username)
        
        return True
    else:
        st.session_state.authenticated = False
        st.session_state.login_error = "Usuário ou senha incorretos"
        return False


def logout() -> None:
    """Faz logout e limpa todos os dados da sessão."""
    st.session_state.authenticated = False
    st.session_state.login_error = None
    
    if "current_user" in st.session_state:
        del st.session_state.current_user
    
    clear_auth_from_storage()
    
    # Limpa tudo para forçar reload no próximo login
    keys_to_clear = [
        "plantoes_initialized",
        "plantoes_data",
        "selected_year",
        "financas_initialized",
        "financas_data",
        "custos_fixos_data",
        "selected_mes_idx",
        "selected_ano",
        "casamento_initialized",
        "casamento_data",
        "auth_initialized",
        "_stored_auth_loaded",
        "_stored_username",
        "_stored_token",
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def is_authenticated() -> bool:
    """Checa se está logado."""
    return st.session_state.get("authenticated", False)


def require_auth() -> bool:
    """Verifica autenticação (para usar nas páginas)."""
    if not is_authenticated():
        st.warning("Você precisa fazer login primeiro.")
        st.stop()
    return True
