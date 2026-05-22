"""Componentes de KPIs e métricas."""

from __future__ import annotations

import streamlit as st


def render_kpi(label: str, value: str | float, delta: str | None = None) -> None:
    """Renderiza um KPI."""
    st.metric(label=label, value=value, delta=delta)


def render_kpi_row(kpis: list[tuple[str, str | float, str | None]]) -> None:
    """Renderiza uma linha de KPIs."""
    cols = st.columns(len(kpis))
    
    for i, (label, value, delta) in enumerate(kpis):
        with cols[i]:
            render_kpi(label, value, delta)
