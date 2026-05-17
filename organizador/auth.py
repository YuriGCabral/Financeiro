"""Sistema de autenticação com cookies (corrigido e estável)."""

from __future__ import annotations

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

VALID_USERNAME = "Carol Gomes"
VALID_PASSWORD = "Thalis2002@"


# =========================
# COOKIES (SINGLETON)
# =========================
def get_cookies():
    """Retorna singleton do gerenciador de cookies."""
    if "cookies" not in st.session_state:
        st.session_state.cookies = EncryptedCookieManager(
            prefix="clinica_financeira_",
            password="Thalis2002@_secret_key_2026"
        )
    return st.session_state.cookies


# =========================
# INIT AUTH STATE
# =========================
def init_auth_state() -> None:
    """Inicializa estado de autenticação SEM quebrar UI."""
    
    # NÃO resetar valores existentes
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if "login_error" not in st.session_state:
        st.session_state.login_error = None

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    cookies = get_cookies()

    # 🚨 NÃO usar st.stop() aqui
    # Apenas tenta restaurar se estiver pronto
    if cookies.ready():
        if (
            cookies.get("logado") == "true"
            and cookies.get("username") == VALID_USERNAME
        ):
            st.session_state.logado = True
            st.session_state.current_user = VALID_USERNAME


# =========================
# LOGIN
# =========================
def login(username: str, password: str) -> bool:
    """Faz login e salva no cookie."""
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        st.session_state.logado = True
        st.session_state.current_user = username
        st.session_state.login_error = None

        cookies = get_cookies()

        # Só salva se cookies estiver pronto
        if cookies.ready():
            cookies["logado"] = "true"
            cookies["username"] = username
            cookies.save()

        return True

    else:
        st.session_state.login_error = "Usuário ou senha incorretos"
        return False


# =========================
# LOGOUT
# =========================
def logout() -> None:
    """Faz logout e limpa cookie."""
    st.session_state.logado = False
    st.session_state.current_user = None
    st.session_state.login_error = None

    cookies = get_cookies()

    if cookies.ready():
        cookies["logado"] = "false"
        cookies["username"] = ""
        cookies.save()

    # Limpa dados das páginas
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
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


# =========================
# HELPERS
# =========================
def is_authenticated() -> bool:
    """Checa se está logado."""
    return st.session_state.get("logado", False)


def require_auth() -> bool:
    """Verifica autenticação nas páginas."""
    if not is_authenticated():
        st.warning("Você precisa fazer login primeiro.")
        st.stop()
    return True