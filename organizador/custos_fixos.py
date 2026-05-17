"""Custos fixos mensais e parcelados (1–20 vezes)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from organizador.financas_table import _to_float

MODO_FIXO = "fixo"
MODO_PARCELADO = "parcelado"

LABEL_FIXO = "Fixo todo mês"
LABEL_PARCELADO = "Parcelado (N meses)"

# Editor: mês/ano em que a parcela começa + quantidade (sem colunas de “primeira/última” em data)
COL_MES = "Mês"
COL_ANO = "Ano"
COL_PARCELAS = "Parcelas"

# Legado (planilhas / versões antigas)
LEG_MES_INICIO = "Mês início"
LEG_ANO_INICIO = "Ano início"
LEG_VEZES = "Vezes (meses)"
LEG_DATA_INICIO = "Início (1ª parcela)"
LEG_DATA_FIM = "Última parcela"
LEG_VAI_ATE = "Vai até"


def month_ord(ano: int, mes: int) -> int:
    return int(ano) * 12 + int(mes) - 1


def _norm_tipo(v: Any) -> str:
    if v in ("Receita", "Despesa"):
        return v
    return "Despesa"


def _norm_modo_label(v: Any) -> str:
    s = str(v or "").strip().lower()
    if s in (MODO_FIXO, LABEL_FIXO.lower(), "fixo todo mês"):
        return LABEL_FIXO
    if s in (MODO_PARCELADO, "parcelado", LABEL_PARCELADO.lower()):
        return LABEL_PARCELADO
    return LABEL_FIXO


def modo_storage_from_label(label: str) -> str:
    return MODO_PARCELADO if label == LABEL_PARCELADO else MODO_FIXO


def label_from_storage(modo: str) -> str:
    return LABEL_PARCELADO if modo == MODO_PARCELADO else LABEL_FIXO


def _cell_to_ts(val: Any) -> pd.Timestamp | None:
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (ValueError, TypeError):
        return None
    if isinstance(val, pd.Timestamp):
        return pd.Timestamp(year=int(val.year), month=int(val.month), day=1)
    if hasattr(val, "year") and hasattr(val, "month"):
        try:
            y, m = int(val.year), int(val.month)
        except (ValueError, TypeError, OverflowError):
            return None
        return pd.Timestamp(year=y, month=max(1, min(12, m)), day=1)
    ts = pd.to_datetime(val, errors="coerce")
    if pd.isna(ts):
        return None
    return pd.Timestamp(year=int(ts.year), month=int(ts.month), day=1)


def custos_fixos_records_to_df(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for r in records or []:
        modo = str(r.get("modo") or MODO_FIXO)
        modo_lbl = label_from_storage(modo)
        ano_i = int(r.get("ano_inicio") or 2026)
        mes_i = int(r.get("mes_inicio") or 1)
        mes_i = max(1, min(12, mes_i))
        n = int(r.get("vezes") or 0)
        if modo == MODO_FIXO:
            n = 0
        else:
            n = max(0, min(20, n))
        rows.append(
            {
                "Título": str(r.get("titulo", "") or ""),
                "Valor (R$)": _to_float(r.get("valor")),
                "Tipo": _norm_tipo(r.get("tipo")),
                "Modo": modo_lbl,
                COL_MES: mes_i,
                COL_ANO: ano_i,
                COL_PARCELAS: n,
            }
        )
    if not rows:
        rows.append(
            {
                "Título": "",
                "Valor (R$)": 0.0,
                "Tipo": "Despesa",
                "Modo": LABEL_FIXO,
                COL_MES: 1,
                COL_ANO: 2026,
                COL_PARCELAS: 0,
            }
        )
    return pd.DataFrame(rows)


def df_to_custos_fixos_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    def _i(row: pd.Series, col: str, default: int) -> int:
        v = pd.to_numeric(row.get(col), errors="coerce")
        if pd.isna(v):
            return default
        return int(v)

    for _, row in df.iterrows():
        titulo = str(row.get("Título", "") or "").strip()
        valor = _to_float(row.get("Valor (R$)"))
        modo_lbl = _norm_modo_label(row.get("Modo"))
        modo = modo_storage_from_label(modo_lbl)

        mes_i = max(1, min(12, _i(row, COL_MES, 1)))
        ano_i = _i(row, COL_ANO, 2026)
        n = _i(row, COL_PARCELAS, 0)

        if modo == MODO_FIXO:
            n = 0
        else:
            n = max(0, min(20, n))

        out.append(
            {
                "titulo": titulo,
                "valor": valor,
                "tipo": _norm_tipo(row.get("Tipo")),
                "modo": modo,
                "vezes": n,
                "ano_inicio": ano_i,
                "mes_inicio": mes_i,
            }
        )
    return out


def filter_custos_fixos_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove linhas totalmente vazias."""
    kept: list[dict[str, Any]] = []
    for r in records:
        if (r.get("titulo") or "").strip() or float(r.get("valor") or 0) != 0:
            kept.append(r)
    return kept


def linhas_automaticas_mes(items: list[dict[str, Any]], ano: int, mes: int) -> list[dict[str, Any]]:
    """Gera linhas (valor + tipo) que entram neste mês por regra fixa ou parcelada."""
    out: list[dict[str, Any]] = []
    cur = month_ord(ano, mes)
    for it in items:
        titulo = str(it.get("titulo") or "").strip()
        valor = float(it.get("valor") or 0)
        if not titulo or valor <= 0:
            continue
        tipo = _norm_tipo(it.get("tipo"))
        modo = str(it.get("modo") or MODO_FIXO)
        if modo == MODO_FIXO:
            out.append(
                {
                    "Título": titulo,
                    "Valor (R$)": valor,
                    "Tipo": tipo,
                    "Detalhe": "Custo fixo (todo mês)",
                }
            )
            continue
        n = max(0, min(20, int(it.get("vezes") or 0)))
        if n <= 0:
            continue
        ano0 = int(it.get("ano_inicio") or ano)
        mes0 = int(it.get("mes_inicio") or 1)
        mes0 = max(1, min(12, mes0))
        start = month_ord(ano0, mes0)
        if cur < start or cur >= start + n:
            continue
        k = cur - start + 1
        out.append(
            {
                "Título": titulo,
                "Valor (R$)": valor,
                "Tipo": tipo,
                "Detalhe": f"Parcela {k}/{n} · parcelado",
            }
        )
    return out


def automaticas_para_df(linhas: list[dict[str, Any]]) -> pd.DataFrame:
    if not linhas:
        return pd.DataFrame(columns=["Título", "Valor (R$)", "Tipo", "Detalhe"])
    return pd.DataFrame(linhas)


def ensure_custos_fixos_editor_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Tipo" not in df.columns:
        df["Tipo"] = "Despesa"
    df["Tipo"] = df["Tipo"].apply(lambda x: _norm_tipo(x)).astype(str)
    if "Modo" not in df.columns:
        df["Modo"] = LABEL_FIXO
    df["Modo"] = df["Modo"].apply(_norm_modo_label).astype(str)

    # Migração: colunas antigas → Mês / Ano
    if COL_MES not in df.columns:
        if LEG_MES_INICIO in df.columns:
            df[COL_MES] = pd.to_numeric(df[LEG_MES_INICIO], errors="coerce").fillna(1).clip(1, 12).astype(int)
        elif LEG_DATA_INICIO in df.columns:
            def _mes_de_data(v: Any) -> int:
                t = _cell_to_ts(v)
                return int(t.month) if t is not None else 1

            df[COL_MES] = df[LEG_DATA_INICIO].apply(_mes_de_data)
        else:
            df[COL_MES] = 1
    df[COL_MES] = pd.to_numeric(df[COL_MES], errors="coerce").fillna(1).clip(1, 12).astype(int)

    if COL_ANO not in df.columns:
        if LEG_ANO_INICIO in df.columns:
            df[COL_ANO] = pd.to_numeric(df[LEG_ANO_INICIO], errors="coerce").fillna(2026).astype(int)
        elif LEG_DATA_INICIO in df.columns:
            def _ano_de_data(v: Any) -> int:
                t = _cell_to_ts(v)
                return int(t.year) if t is not None else 2026

            df[COL_ANO] = df[LEG_DATA_INICIO].apply(_ano_de_data)
        else:
            df[COL_ANO] = 2026
    df[COL_ANO] = pd.to_numeric(df[COL_ANO], errors="coerce").fillna(2026).astype(int)

    if COL_PARCELAS not in df.columns:
        if LEG_VEZES in df.columns:
            df[COL_PARCELAS] = pd.to_numeric(df[LEG_VEZES], errors="coerce").fillna(0).astype(int).clip(0, 20)
        else:
            df[COL_PARCELAS] = 0
    df[COL_PARCELAS] = pd.to_numeric(df[COL_PARCELAS], errors="coerce").fillna(0).astype(int).clip(0, 20)

    # Fixo: parcelas 0 para exibição coerente
    def _ajusta_parcelas_fixo(row: pd.Series) -> int:
        if row["Modo"] == LABEL_FIXO:
            return 0
        parcelas = row[COL_PARCELAS]
        if pd.isna(parcelas):
            return 0
        return int(parcelas)

    df[COL_PARCELAS] = df.apply(_ajusta_parcelas_fixo, axis=1).astype(int)

    preferred = ["Título", "Valor (R$)", "Tipo", "Modo", COL_MES, COL_ANO, COL_PARCELAS]
    ordered = [c for c in preferred if c in df.columns]
    legacy_drop = {LEG_MES_INICIO, LEG_ANO_INICIO, LEG_VEZES, LEG_DATA_INICIO, LEG_DATA_FIM, LEG_VAI_ATE}
    rest = [c for c in df.columns if c not in ordered and c not in legacy_drop]
    return df[ordered + rest]
