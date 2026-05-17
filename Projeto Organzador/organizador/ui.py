"""Design system — identidade rosa (SaaS), Lucide, cards e micro-interações."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import streamlit as st

from organizador.lucide import inline_svg, sidebar_nav_icon_css

THEME_CSS = r"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700&display=swap');

  :root {
    --pink-50: #fff1f2;
    --pink-100: #ffe4e6;
    --pink-200: #fecdd3;
    --pink-300: #fda4af;
    --pink-400: #fb7185;
    --pink-500: #f43f5e;
    --pink-600: #e11d48;
    --pink-700: #be123c;

    --gray-900: #111827;
    --gray-500: #6b7280;

    --bg-main: #fff7f9;
    --bg-card: #ffffff;
    --bg-muted: #fff1f2;

    --text-primary: var(--gray-900);
    --text-secondary: var(--gray-500);

    --border: #ffe4e6;
    --border-strong: #fecdd3;

    --shadow-card: 0 4px 12px rgba(0, 0, 0, 0.05);
    --shadow-pink: 0 8px 24px rgba(244, 63, 94, 0.12);
    --shadow-card-hover: 0 6px 18px rgba(244, 63, 94, 0.15);

    --success: #047857;
    --danger: #b91c1c;

    --focus-ring: 0 0 0 2px rgba(225, 29, 72, 0.22);

    --radius-card: 16px;
    --radius-control: 14px;

    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --t-fast: 160ms;
    --t-med: 220ms;

    --ui-bg: var(--bg-main);
    --ui-surface: var(--bg-card);
    --ui-surface-2: var(--bg-muted);
    --ui-border: var(--border);
    --ui-text: var(--text-primary);
    --ui-muted: var(--text-secondary);
    --ui-accent: var(--pink-600);
    --ui-accent-hover: var(--pink-500);
    --ui-accent-weak: var(--pink-100);
    --ui-success: var(--success);
    --ui-danger: var(--danger);
    --ui-radius: var(--radius-card);
    --ui-radius-sm: var(--radius-control);
    --ui-shadow-sm: var(--shadow-card);
    --ui-shadow: var(--shadow-pink);
    --ui-grid: 8px;
  }

  html, body, [class*="css"] {
    font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: var(--text-primary);
  }

  .poppins, .page-header__title, .ui-card__title, .sb-brand__title {
    font-family: 'Poppins', 'Inter', system-ui, sans-serif !important;
  }

  [data-testid="stAppViewContainer"] {
    background: var(--bg-main) !important;
  }

  [data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.92) !important;
    border-bottom: 1px solid var(--pink-100);
    backdrop-filter: blur(8px);
  }

  .block-container,
  .stMainBlockContainer {
    max-width: 1040px !important;
    padding-top: 22px !important;
    padding-bottom: calc(var(--ui-grid) * 5) !important;
  }

  [data-testid="stSidebar"] {
    background: var(--pink-50) !important;
    border-right: 1px solid var(--pink-100) !important;
  }

  [data-testid="stSidebarNavLink"] {
    border-radius: var(--radius-control) !important;
    margin: 4px 10px !important;
    color: var(--text-secondary) !important;
    transition: background-color var(--t-fast) var(--ease), color var(--t-fast) var(--ease), box-shadow var(--t-med) var(--ease);
  }
  [data-testid="stSidebarNavLink"][aria-current="page"] {
    background: #ffffff !important;
    color: var(--pink-700) !important;
    font-weight: 600 !important;
    box-shadow: inset 3px 0 0 0 var(--pink-600);
    border: 1px solid var(--pink-100);
  }
  [data-testid="stSidebarNavLink"]:hover {
    background: rgba(255, 255, 255, 0.72) !important;
    color: var(--pink-700) !important;
  }

  .sb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 14px;
    margin: 8px 10px 14px 10px;
    border: 1px solid var(--pink-100);
    border-radius: var(--radius-card);
    background: #ffffff;
    box-shadow: var(--shadow-card);
    color: var(--text-primary);
  }
  .sb-brand__mark {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
  }
  .sb-brand__mark svg {
    display: block;
    color: var(--pink-600);
  }
  .sb-brand__title {
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: -0.01em;
    color: var(--pink-700);
  }
  .sb-brand__sub {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-top: 2px;
  }

  h1 { font-size: 1.45rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: var(--text-primary) !important; }
  h2, h3 { color: var(--text-primary) !important; font-weight: 600 !important; }
  .stCaption, [data-testid="stCaptionContainer"] { color: var(--text-secondary) !important; }

  .page-header {
    margin-bottom: calc(var(--ui-grid) * 3);
    padding-top: 6px;
    overflow: visible;
  }
  .page-header--surface {
    border-radius: var(--radius-card);
    padding: 18px 18px 16px 18px;
    margin-bottom: calc(var(--ui-grid) * 3);
    border: 1px solid var(--pink-100);
    background: linear-gradient(135deg, rgba(244, 63, 94, 0.12), rgba(251, 113, 133, 0.1));
    box-shadow: var(--shadow-card);
    overflow: visible;
  }
  .page-header__title-row {
    display: flex;
    align-items: center;
    gap: 14px;
    overflow: visible;
  }
  .page-header__mark {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    padding: 8px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid var(--pink-100);
    box-shadow: var(--shadow-card);
  }
  .page-header__mark svg {
    display: block;
    color: var(--pink-600);
  }
  .page-header__title {
    margin: 0;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--pink-700);
    letter-spacing: -0.03em;
    line-height: 1.15;
  }
  .page-header__sub {
    margin: 8px 0 0 0;
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.55;
    max-width: 720px;
    font-weight: 500;
  }

  .ui-card {
    background: var(--bg-card);
    border: 1px solid var(--pink-100);
    border-radius: 14px;
    box-shadow: var(--shadow-card);
    margin-bottom: calc(var(--ui-grid) * 2);
    overflow: visible;
    transition: box-shadow var(--t-med) var(--ease), transform var(--t-fast) var(--ease);
  }
  .ui-card:hover {
    box-shadow: var(--shadow-card-hover);
  }
  .ui-card__head {
    padding: calc(var(--ui-grid) * 2.5) calc(var(--ui-grid) * 3);
    border-bottom: 1px solid var(--pink-100);
    background: #ffffff;
  }
  .ui-card__head-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }
  .ui-card__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
    border-radius: 12px;
    background: var(--pink-50);
    border: 1px solid var(--pink-100);
    flex: 0 0 auto;
  }
  .ui-card__icon svg {
    display: block;
    color: var(--pink-600);
  }
  .ui-card__title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--pink-700);
    letter-spacing: -0.01em;
  }
  .ui-card__sub {
    margin: 6px 0 0 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.45;
    font-weight: 500;
  }
  .ui-card__body {
    padding: calc(var(--ui-grid) * 2.5) calc(var(--ui-grid) * 3);
  }

  .status-badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 6px;
  }
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid var(--pink-100);
    background: var(--pink-50);
    font-size: 0.8125rem;
    color: var(--text-primary);
  }
  .status-badge strong {
    font-weight: 600;
    color: var(--pink-700);
  }
  .status-badge__pill {
    font-weight: 700;
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 999px;
    background: #ffffff;
    border: 1px solid var(--pink-200);
    color: var(--pink-700);
  }
  .status-badge--no {
    background: #ffffff;
    border-color: var(--pink-100);
  }
  .status-badge--no .status-badge__pill {
    color: var(--text-secondary);
    border-color: #e5e7eb;
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px;
    margin-top: 4px;
  }
  .kpi-tile {
    background: var(--bg-card);
    border: 1px solid var(--pink-100);
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: var(--shadow-card);
    transition: box-shadow var(--t-med) var(--ease), transform var(--t-fast) var(--ease);
  }
  .kpi-tile:hover {
    box-shadow: var(--shadow-pink);
    transform: translateY(-1px);
  }
  .kpi-tile__label {
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-secondary);
  }
  .kpi-tile__value {
    margin-top: 6px;
    font-size: 1.35rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    color: var(--text-primary);
  }
  .kpi-tile--accent .kpi-tile__value { color: var(--pink-600); }
  .kpi-tile--pos .kpi-tile__value { color: var(--success); }
  .kpi-tile--neg .kpi-tile__value { color: var(--danger); }

  .ui-empty {
    border: 1px dashed var(--pink-200);
    border-radius: var(--radius-card);
    padding: calc(var(--ui-grid) * 3);
    text-align: center;
    background: #ffffff;
    color: var(--text-secondary);
  }
  .ui-empty__icon {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
    color: var(--pink-600);
  }
  .ui-empty__title {
    font-weight: 600;
    color: var(--pink-700);
    margin-bottom: 6px;
    font-size: 0.95rem;
  }
  .ui-empty__body {
    font-size: 0.875rem;
    line-height: 1.55;
  }

  .ui-table-wrap [data-testid="stDataFrame"],
  .ui-table-wrap [data-testid="stDataEditor"] {
    border: 1px solid var(--pink-100);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: box-shadow var(--t-med) var(--ease);
  }
  .ui-table-wrap [data-testid="stDataFrame"]:hover,
  .ui-table-wrap [data-testid="stDataEditor"]:hover {
    box-shadow: var(--shadow-pink);
  }
  .ui-table-wrap table tbody tr:nth-child(even) td {
    background: var(--pink-50) !important;
  }
  .ui-table-wrap table tbody tr:hover td {
    background: var(--pink-100) !important;
    transition: background-color var(--t-fast) var(--ease);
  }

  div[data-baseweb="input"] > div,
  div[data-baseweb="select"] > div,
  textarea,
  input[type="number"],
  input[type="text"] {
    border-radius: var(--radius-control) !important;
    border-color: var(--pink-100) !important;
  }
  div[data-baseweb="select"] > div {
    box-shadow: none !important;
  }
  input:focus-visible, textarea:focus-visible, div[data-baseweb="select"]:focus-within {
    box-shadow: var(--focus-ring) !important;
    border-color: var(--pink-600) !important;
    outline: none !important;
  }

  .stButton > button {
    border-radius: var(--radius-control) !important;
    height: 40px !important;
    padding: 0 16px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    transition: background-color var(--t-fast) var(--ease), box-shadow var(--t-med) var(--ease), filter var(--t-fast) var(--ease), border-color var(--t-fast) var(--ease) !important;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--pink-500), var(--pink-400)) !important;
    color: #ffffff !important;
    border: 1px solid transparent !important;
  }
  .stButton > button[kind="primary"]:hover {
    filter: brightness(1.03);
    box-shadow: var(--shadow-pink) !important;
  }
  .stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--pink-100) !important;
  }
  .stButton > button[kind="secondary"]:hover {
    background: var(--pink-50) !important;
  }
  .stButton > button[kind="tertiary"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
  }
  .stButton > button[kind="tertiary"]:hover {
    background: rgba(244, 63, 94, 0.08) !important;
    color: var(--pink-700) !important;
  }

  [data-testid="stDownloadButton"] button {
    border-radius: var(--radius-control) !important;
  }

  details[data-testid="stExpander"] {
    border: 1px solid var(--pink-100) !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    box-shadow: var(--shadow-card) !important;
  }
  details[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--pink-700) !important;
  }

  [data-testid="stMetricValue"] {
    color: var(--pink-600) !important;
    font-variant-numeric: tabular-nums !important;
    font-weight: 700 !important;
  }
  [data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
  }

  .stAlert { border-radius: var(--radius-card) !important; }

  .lucide-ic { vertical-align: middle; }

  /* === RESPONSIVIDADE MOBILE === */
  
  @media (max-width: 768px) {
    /* Container principal */
    .block-container,
    .stMainBlockContainer {
      max-width: 100% !important;
      padding-left: 12px !important;
      padding-right: 12px !important;
      padding-top: 12px !important;
      padding-bottom: 16px !important;
    }

    /* Header da página */
    .page-header--surface {
      padding: 14px 12px !important;
      margin-bottom: 16px !important;
    }
    
    .page-header__title-row {
      flex-direction: column;
      gap: 8px !important;
      align-items: flex-start !important;
    }
    
    .page-header__mark {
      padding: 6px !important;
    }
    
    .page-header__mark svg {
      width: 20px !important;
      height: 20px !important;
    }
    
    .page-header__title {
      font-size: 1.35rem !important;
      line-height: 1.2 !important;
    }
    
    .page-header__sub {
      font-size: 0.85rem !important;
      line-height: 1.4 !important;
      margin-top: 4px !important;
    }

    /* Cards */
    .ui-card {
      margin-bottom: 16px !important;
      border-radius: 12px !important;
    }
    
    .ui-card__head {
      padding: 14px 12px !important;
    }
    
    .ui-card__body {
      padding: 14px 12px !important;
    }
    
    .ui-card__head-row {
      gap: 8px !important;
    }
    
    .ui-card__icon {
      padding: 4px !important;
    }
    
    .ui-card__icon svg {
      width: 18px !important;
      height: 18px !important;
    }
    
    .ui-card__title {
      font-size: 0.9rem !important;
    }
    
    .ui-card__sub {
      font-size: 0.8rem !important;
      margin-top: 4px !important;
    }

    /* KPIs Grid - empilha em mobile */
    .kpi-grid {
      grid-template-columns: 1fr !important;
      gap: 8px !important;
    }
    
    .kpi-tile {
      padding: 10px 12px !important;
    }
    
    .kpi-tile__label {
      font-size: 0.65rem !important;
    }
    
    .kpi-tile__value {
      font-size: 1.15rem !important;
      margin-top: 4px !important;
    }

    /* Status badges */
    .status-badge-row {
      flex-direction: column;
      gap: 6px !important;
    }
    
    .status-badge {
      width: 100%;
      justify-content: space-between;
      padding: 6px 10px !important;
      font-size: 0.75rem !important;
    }
    
    .status-badge__pill {
      font-size: 0.7rem !important;
    }

    /* Sidebar */
    .sb-brand {
      padding: 12px 10px !important;
      margin: 8px 6px 12px 6px !important;
      gap: 8px !important;
    }
    
    .sb-brand__mark svg {
      width: 18px !important;
      height: 18px !important;
    }
    
    .sb-brand__title {
      font-size: 0.9rem !important;
    }
    
    .sb-brand__sub {
      font-size: 0.7rem !important;
    }

    /* Tabelas - scroll horizontal */
    .ui-table-wrap {
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch;
    }
    
    .ui-table-wrap [data-testid="stDataFrame"],
    .ui-table-wrap [data-testid="stDataEditor"] {
      min-width: 500px;
    }

    /* Formulários e inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea,
    input[type="number"],
    input[type="text"] {
      font-size: 16px !important; /* Previne zoom no iOS */
    }

    /* Botões */
    .stButton > button {
      width: 100% !important;
      height: 44px !important; /* Touch target maior */
      font-size: 0.9rem !important;
    }

    /* Colunas do Streamlit - empilha */
    [data-testid="column"] {
      width: 100% !important;
      min-width: 100% !important;
    }

    /* Empty state */
    .ui-empty {
      padding: 20px 12px !important;
    }
    
    .ui-empty__icon svg {
      width: 22px !important;
      height: 22px !important;
    }
    
    .ui-empty__title {
      font-size: 0.85rem !important;
    }
    
    .ui-empty__body {
      font-size: 0.8rem !important;
    }

    /* Expanders */
    details[data-testid="stExpander"] summary {
      font-size: 0.85rem !important;
      padding: 10px 12px !important;
    }

    /* Headers gerais */
    h1 {
      font-size: 1.25rem !important;
    }
    
    h2 {
      font-size: 1.1rem !important;
    }
    
    h3 {
      font-size: 1rem !important;
    }

    /* Caption e textos secundários */
    .stCaption,
    [data-testid="stCaptionContainer"] {
      font-size: 0.75rem !important;
    }
  }

  /* Tablets (768px - 1024px) */
  @media (min-width: 769px) and (max-width: 1024px) {
    .block-container,
    .stMainBlockContainer {
      max-width: 95% !important;
      padding-left: 16px !important;
      padding-right: 16px !important;
    }

    .kpi-grid {
      grid-template-columns: repeat(2, 1fr) !important;
      gap: 10px !important;
    }

    .page-header__title {
      font-size: 1.6rem !important;
    }

    .ui-card__head,
    .ui-card__body {
      padding: 16px !important;
    }
  }

  /* Landscape mobile */
  @media (max-width: 768px) and (orientation: landscape) {
    .page-header--surface {
      padding: 10px 12px !important;
    }
    
    .page-header__title {
      font-size: 1.2rem !important;
    }
    
    .ui-card__head {
      padding: 10px 12px !important;
    }
    
    .ui-card__body {
      padding: 10px 12px !important;
    }
  }
</style>
"""


def inject_dashboard_theme() -> None:
    # Meta tags para mobile
    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown(sidebar_nav_icon_css(), unsafe_allow_html=True)


def inject_medical_pink_theme() -> None:
    inject_dashboard_theme()


def sidebar_brand(subtitle: str = "") -> None:
    mark = inline_svg("heart-pulse", 22)
    st.sidebar.markdown(
        f"""
<div class="sb-brand">
  <div class="sb-brand__mark">{mark}</div>
  <div>
    <div class="sb-brand__title poppins">Clínica Financeira</div>
    <div class="sb-brand__sub">{subtitle}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str | None = None, lucide: str | None = None) -> None:
    mark_html = ""
    if lucide:
        mark_html = f'<div class="page-header__mark" aria-hidden="true">{inline_svg(lucide, 26)}</div>'
    sub_html = f'<p class="page-header__sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
<header class="page-header page-header--surface">
  <div class="page-header__title-row">
    {mark_html}
    <div>
      <h1 class="page-header__title poppins">{title}</h1>
      {sub_html}
    </div>
  </div>
</header>
        """,
        unsafe_allow_html=True,
    )


def med_hero(title: str, subtitle: str, icon: str = "") -> None:
    page_header(title, subtitle, lucide=None)


def status_badges_row(plantoes_ok: bool, financas_ok: bool) -> None:
    def badge(label: str, ok: bool, ok_txt: str, no_txt: str) -> str:
        cls = "status-badge status-badge--ok" if ok else "status-badge status-badge--no"
        txt = ok_txt if ok else no_txt
        return f'<span class="{cls}"><strong>{label}</strong><span class="status-badge__pill">{txt}</span></span>'

    html = (
        '<div class="status-badge-row">'
        + badge("Modelo plantões", plantoes_ok, "Disponível", "Ausente")
        + badge("Planilha antiga", financas_ok, "Encontrada", "Não usada")
        + "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


@contextmanager
def ui_card(title: str, subtitle: str | None = None, lucide: str | None = None) -> Generator[None, None, None]:
    sub = f'<p class="ui-card__sub">{subtitle}</p>' if subtitle else ""
    if lucide:
        icon_html = f'<div class="ui-card__icon" aria-hidden="true">{inline_svg(lucide, 20)}</div>'
        head_inner = f'<div class="ui-card__head-row">{icon_html}<div><div class="ui-card__title poppins">{title}</div>{sub}</div></div>'
    else:
        head_inner = f'<div><div class="ui-card__title poppins">{title}</div>{sub}</div>'
    st.markdown(
        f'<div class="ui-card"><div class="ui-card__head">{head_inner}</div><div class="ui-card__body">',
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        st.markdown("</div></div>", unsafe_allow_html=True)


def empty_state(title: str, body: str, lucide: str | None = None) -> None:
    icon = f'<div class="ui-empty__icon">{inline_svg(lucide, 26)}</div>' if lucide else ""
    st.markdown(
        f"""
<div class="ui-empty">
  {icon}
  <div class="ui-empty__title">{title}</div>
  <div class="ui-empty__body">{body}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def kpi_grid_html(items: list[tuple[str, str, str]]) -> str:
    tiles = []
    for label, value, mod in items:
        cls = f"kpi-tile {mod}".strip()
        tiles.append(
            f'<div class="{cls}"><div class="kpi-tile__label">{label}</div><div class="kpi-tile__value">{value}</div></div>'
        )
    return f'<div class="kpi-grid">{"".join(tiles)}</div>'


def render_kpi_row(*items: tuple[str, str, str]) -> None:
    mod_map = {"": "", "accent": "kpi-tile--accent", "pos": "kpi-tile--pos", "neg": "kpi-tile--neg"}
    triples: list[tuple[str, str, str]] = []
    for label, value, variant in items:
        triples.append((label, value, mod_map.get(variant, "")))
    st.markdown(kpi_grid_html(triples), unsafe_allow_html=True)


def table_wrap_begin() -> None:
    st.markdown('<div class="ui-table-wrap">', unsafe_allow_html=True)


def table_wrap_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
