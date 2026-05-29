"""Camada de serviços com lógica de negócio e cálculos financeiros."""

from __future__ import annotations

from datetime import datetime
import calendar
from typing import Any

import pandas as pd

from db import dao


COLUNAS_FINANCAS = ["id", "ano", "mes", "titulo", "valor", "tipo"]


def _criar_dataframe_financas(registros: list[dict[str, Any]]) -> pd.DataFrame:
    if not registros:
        return pd.DataFrame(columns=COLUNAS_FINANCAS + ["data_ref"])

    df = pd.DataFrame(registros)

    for col in COLUNAS_FINANCAS:
        if col not in df.columns:
            df[col] = None

    df = df[COLUNAS_FINANCAS].copy()
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce").astype("Int64")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)

    df["data_ref"] = pd.to_datetime(
        dict(year=df["ano"], month=df["mes"], day=1),
        errors="coerce"
    )

    return df


def get_todas_transacoes_df() -> pd.DataFrame:
    """Retorna todos os lançamentos financeiros como DataFrame pandas."""
    transacoes = dao.get_transacoes()
    return _criar_dataframe_financas(transacoes)


def calcular_totais() -> dict[str, float]:
    """Calcula totais de receitas, despesas e saldo."""
    transacoes = dao.get_transacoes()

    total_receitas = sum(
        float(t["valor"]) for t in transacoes if t["tipo"] == "Receita"
    )

    total_despesas = sum(
        float(t["valor"]) for t in transacoes if t["tipo"] == "Despesa"
    )

    saldo = total_receitas - total_despesas

    return {
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
    }


def calcular_por_tipo() -> pd.DataFrame:
    """Calcula totais agrupados por tipo."""
    transacoes = dao.get_transacoes()

    if not transacoes:
        return pd.DataFrame(columns=["tipo", "total"])

    df = _criar_dataframe_financas(transacoes)
    resumo = df.groupby("tipo", dropna=False)["valor"].sum().reset_index()
    resumo.columns = ["tipo", "total"]

    return resumo.sort_values("total", ascending=False)


def calcular_por_mes() -> pd.DataFrame:
    """Calcula totais agrupados por mês."""
    transacoes = dao.get_transacoes()

    if not transacoes:
        return pd.DataFrame(columns=["mes", "total_receitas", "total_despesas", "saldo"])

    df = _criar_dataframe_financas(transacoes)

    receitas = df[df["tipo"] == "Receita"].groupby("data_ref")["valor"].sum()
    despesas = df[df["tipo"] == "Despesa"].groupby("data_ref")["valor"].sum()

    resumo = pd.DataFrame({
        "total_receitas": receitas,
        "total_despesas": despesas,
    }).fillna(0)

    resumo["saldo"] = resumo["total_receitas"] - resumo["total_despesas"]
    resumo = resumo.reset_index()
    resumo["mes"] = resumo["data_ref"].dt.strftime("%Y-%m")
    resumo = resumo[["mes", "total_receitas", "total_despesas", "saldo"]]

    return resumo.sort_values("mes", ascending=False)


def get_anos_disponiveis() -> list[int]:
    """Retorna lista de anos únicos já usados."""
    transacoes = dao.get_transacoes()

    anos = {
        int(t["ano"])
        for t in transacoes
        if t.get("ano") is not None
    }

    return sorted(anos)


def validar_transacao(
    ano: int | str,
    mes: int | str,
    titulo: str,
    valor: float | str,
    tipo: str,
) -> tuple[bool, str]:
    """Valida dados de um lançamento financeiro."""
    try:
        ano_int = int(ano)
        if ano_int < 2000 or ano_int > 2100:
            return False, "Ano inválido"
    except (ValueError, TypeError):
        return False, "Ano inválido"

    try:
        mes_int = int(mes)
        if mes_int < 1 or mes_int > 12:
            return False, "Mês deve estar entre 1 e 12"
    except (ValueError, TypeError):
        return False, "Mês inválido"

    if not titulo or not str(titulo).strip():
        return False, "Título é obrigatório"

    try:
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor deve ser maior que zero"
    except (ValueError, TypeError):
        return False, "Valor inválido"

    if tipo not in ("Receita", "Despesa"):
        return False, "Tipo deve ser 'Receita' ou 'Despesa'"

    return True, ""


def criar_transacao(
    ano: int,
    mes: int,
    titulo: str,
    valor: float,
    tipo: str,
) -> tuple[bool, str, Any | None]:
    """Cria um novo lançamento com validação."""
    valido, erro = validar_transacao(ano, mes, titulo, valor, tipo)
    if not valido:
        return False, erro, None

    try:
        transacao_id = dao.add_transacao(ano, mes, titulo, valor, tipo)
        return True, "Lançamento criado com sucesso!", transacao_id
    except Exception as e:
        return False, f"Erro ao criar lançamento: {str(e)}", None


def atualizar_transacao(
    transacao_id: Any,
    ano: int,
    mes: int,
    titulo: str,
    valor: float,
    tipo: str,
) -> tuple[bool, str]:
    """Atualiza um lançamento existente com validação."""
    valido, erro = validar_transacao(ano, mes, titulo, valor, tipo)
    if not valido:
        return False, erro

    try:
        sucesso = dao.update_transacao(transacao_id, ano, mes, titulo, valor, tipo)
        if sucesso:
            return True, "Lançamento atualizado com sucesso!"
        return False, "Lançamento não encontrado"
    except Exception as e:
        return False, f"Erro ao atualizar lançamento: {str(e)}"


def deletar_transacao(transacao_id: Any) -> tuple[bool, str]:
    """Deleta um lançamento."""
    try:
        sucesso = dao.delete_transacao(transacao_id)
        if sucesso:
            return True, "Lançamento deletado com sucesso!"
        return False, "Lançamento não encontrado"
    except Exception as e:
        return False, f"Erro ao deletar lançamento: {str(e)}"


def formatar_mes_nome(ano: int, mes: int) -> str:
    """Retorna nome do mês/ano no formato MM/YYYY ou nome do mês."""
    return f"{int(mes):02d}/{int(ano)}"