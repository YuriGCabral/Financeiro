"""Modelo simples da tabela de finanças mensais."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pandas as pd


def ensure_tipo_column(df: pd.DataFrame) -> pd.DataFrame:
    """Evita NaN/valores inválidos na coluna Tipo (bug do editor com Despesa sumindo)."""
    df = df.copy()
    if "Tipo" not in df.columns:
        df["Tipo"] = "Despesa"

    def norm(x: Any) -> str:
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return "Despesa"
        s = str(x).strip()
        if s in ("Receita", "Despesa"):
            return s
        return "Despesa"

    df["Tipo"] = df["Tipo"].map(norm).astype("object")
    return df


def _to_float(v: Any) -> float:
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return 0.0
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(
            columns=["Título", "Valor (R$)", "Tipo", "Resolvido"],
        )
    rows = []
    for r in records:
        rows.append(
            {
                "Título": str(r.get("titulo", "") or ""),
                "Valor (R$)": _to_float(r.get("valor")),
                "Tipo": r.get("tipo") if r.get("tipo") in ("Receita", "Despesa") else "Despesa",
                "Resolvido": bool(r.get("resolvido", False)),
            }
        )
    df = pd.DataFrame(rows)
    return ensure_tipo_column(df)


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        tipo = row.get("Tipo", "Despesa")
        if tipo not in ("Receita", "Despesa"):
            tipo = "Despesa"
        out.append(
            {
                "titulo": str(row.get("Título", "") or "").strip(),
                "valor": _to_float(row.get("Valor (R$)")),
                "tipo": tipo,
                "resolvido": bool(row.get("Resolvido", False)),
            }
        )
    return out


def financas_placeholder_record() -> dict[str, Any]:
    return {"titulo": "", "valor": 0.0, "tipo": "Despesa", "resolvido": False}


def financas_df_has_meaningful_rows(df: pd.DataFrame | None) -> bool:
    """True se há pelo menos uma linha com título, valor ≠ 0 ou Resolvido."""
    if df is None or df.empty:
        return False
    df = ensure_tipo_column(df)
    for _, row in df.iterrows():
        if str(row.get("Título", "") or "").strip():
            return True
        if abs(_to_float(row.get("Valor (R$)"))) > 1e-12:
            return True
        if bool(row.get("Resolvido", False)):
            return True
    return False


def financas_seed_dataframe(records: list[dict[str, Any]] | None) -> pd.DataFrame:
    """DataFrame para o editor: nunca vazio (uma linha em branco como mínimo)."""
    raw = records if isinstance(records, list) else []
    df = ensure_tipo_column(records_to_dataframe(raw))
    if df.empty:
        df = ensure_tipo_column(records_to_dataframe([financas_placeholder_record()]))
    return df


def financas_records_for_save(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Persiste **todas** as linhas do editor (inclusive em branco entre preenchidas). Só evita gravar DataFrame vazio (bug intermitente do widget)."""
    df = ensure_tipo_column(df.copy())
    if df.empty:
        return [financas_placeholder_record()]
    return dataframe_to_records(df)


def compute_totals(df: pd.DataFrame) -> tuple[float, float, float]:
    if df is None or df.empty:
        return 0.0, 0.0, 0.0
    rec = 0.0
    des = 0.0
    for _, row in df.iterrows():
        v = _to_float(row.get("Valor (R$)"))
        tipo = row.get("Tipo", "Despesa")
        if tipo == "Receita":
            rec += v
        else:
            des += v
    saldo = rec - des
    return rec, des, saldo


def compute_totals_two(df_manual: pd.DataFrame, df_auto: pd.DataFrame | None) -> tuple[float, float, float]:
    parts: list[pd.DataFrame] = [ensure_tipo_column(df_manual)]
    if df_auto is not None and not df_auto.empty:
        a = df_auto.copy()
        if "Tipo" not in a.columns:
            a["Tipo"] = "Despesa"
        a["Valor (R$)"] = [_to_float(v) for v in a["Valor (R$)"]]
        a["Tipo"] = [x if x in ("Receita", "Despesa") else "Despesa" for x in a["Tipo"]]
        parts.append(a[["Valor (R$)", "Tipo"]])
    combined = pd.concat(parts, ignore_index=True) if len(parts) > 1 else parts[0]
    return compute_totals(combined)


def format_brl(value: float) -> str:
    d = Decimal(str(round(value, 2)))
    s = f"{d:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")
