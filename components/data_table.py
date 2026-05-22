"""Componente para renderizar tabelas de dados."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_data_table(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    format_dict: dict[str, str] | None = None,
    height: int = 400
) -> None:
    """Renderiza tabela de dados com formatação."""
    if df.empty:
        st.info("Nenhum dado para exibir.")
        return
    
    # Seleciona colunas se especificado
    if columns:
        df = df[columns]
    
    # Aplica formatação
    if format_dict:
        df_styled = df.style.format(format_dict)
        st.dataframe(df_styled, use_container_width=True, height=height)
    else:
        st.dataframe(df, use_container_width=True, height=height)


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage(value: float) -> str:
    """Formata valor como percentual."""
    return f"{value:.1f}%"
