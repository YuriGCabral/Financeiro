"""Componentes de formulários reutilizáveis."""

from __future__ import annotations

from datetime import date
import streamlit as st


def form_number_input(
    label: str,
    value: float = 0.0,
    min_value: float = 0.0,
    step: float = 0.01,
    key: str | None = None
) -> float:
    """Input numérico padronizado."""
    return st.number_input(
        label,
        value=value,
        min_value=min_value,
        step=step,
        format="%.2f",
        key=key
    )


def form_select_mes() -> int:
    """Seletor de mês padronizado."""
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    mes_selecionado = st.selectbox("Mês", meses)
    return meses.index(mes_selecionado) + 1


def form_select_ano(anos_opcoes: list[int] | None = None) -> int:
    """Seletor de ano padronizado."""
    if not anos_opcoes:
        ano_atual = date.today().year
        anos_opcoes = list(range(ano_atual - 2, ano_atual + 3))
    
    return st.selectbox("Ano", anos_opcoes, index=2)


def form_checkbox(label: str, value: bool = False, key: str | None = None) -> bool:
    """Checkbox padronizado."""
    return st.checkbox(label, value=value, key=key)
