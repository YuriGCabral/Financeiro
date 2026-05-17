"""Camada de serviços com lógica de negócio e cálculos financeiros."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from db import dao


def get_todas_transacoes_df() -> pd.DataFrame:
    """Retorna todas as transações como DataFrame pandas.
    
    Returns:
        DataFrame com colunas: id, data, descricao, valor, tipo, categoria
    """
    transacoes = dao.get_transacoes()
    
    if not transacoes:
        return pd.DataFrame(columns=["id", "data", "descricao", "valor", "tipo", "categoria"])
    
    df = pd.DataFrame(transacoes)
    
    # Converte tipos
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["valor"] = df["valor"].astype(float)
    
    return df


def calcular_totais() -> dict[str, float]:
    """Calcula totais de receitas, despesas e saldo.
    
    Returns:
        Dicionário com:
        - total_receitas: Soma de todas as receitas
        - total_despesas: Soma de todas as despesas
        - saldo: Diferença entre receitas e despesas
    """
    transacoes = dao.get_transacoes()
    
    total_receitas = sum(
        t["valor"] for t in transacoes if t["tipo"] == "Receita"
    )
    
    total_despesas = sum(
        t["valor"] for t in transacoes if t["tipo"] == "Despesa"
    )
    
    saldo = total_receitas - total_despesas
    
    return {
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
    }


def calcular_por_categoria() -> pd.DataFrame:
    """Calcula totais agrupados por categoria.
    
    Returns:
        DataFrame com colunas: categoria, tipo, total
    """
    transacoes = dao.get_transacoes()
    
    if not transacoes:
        return pd.DataFrame(columns=["categoria", "tipo", "total"])
    
    df = pd.DataFrame(transacoes)
    
    # Agrupa por categoria e tipo
    resumo = df.groupby(["categoria", "tipo"])["valor"].sum().reset_index()
    resumo.columns = ["categoria", "tipo", "total"]
    
    # Ordena por total decrescente
    resumo = resumo.sort_values("total", ascending=False)
    
    return resumo


def calcular_por_mes() -> pd.DataFrame:
    """Calcula totais agrupados por mês.
    
    Returns:
        DataFrame com colunas: mes, total_receitas, total_despesas, saldo
    """
    transacoes = dao.get_transacoes()
    
    if not transacoes:
        return pd.DataFrame(columns=["mes", "total_receitas", "total_despesas", "saldo"])
    
    df = pd.DataFrame(transacoes)
    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M")
    
    # Separa receitas e despesas
    receitas = df[df["tipo"] == "Receita"].groupby("mes")["valor"].sum()
    despesas = df[df["tipo"] == "Despesa"].groupby("mes")["valor"].sum()
    
    # Combina em um único DataFrame
    resumo = pd.DataFrame({
        "total_receitas": receitas,
        "total_despesas": despesas,
    }).fillna(0)
    
    resumo["saldo"] = resumo["total_receitas"] - resumo["total_despesas"]
    resumo = resumo.reset_index()
    resumo["mes"] = resumo["mes"].astype(str)
    
    return resumo.sort_values("mes", ascending=False)


def get_categorias_disponiveis() -> list[str]:
    """Retorna lista de categorias únicas já usadas.
    
    Returns:
        Lista ordenada de categorias
    """
    transacoes = dao.get_transacoes()
    
    categorias = set(t["categoria"] for t in transacoes)
    
    return sorted(categorias)


def validar_transacao(
    data: date | str,
    descricao: str,
    valor: float | str,
    tipo: str,
    categoria: str,
) -> tuple[bool, str]:
    """Valida dados de uma transação.
    
    Args:
        data: Data da transação
        descricao: Descrição
        valor: Valor
        tipo: Tipo ('Receita' ou 'Despesa')
        categoria: Categoria
    
    Returns:
        Tupla (valido, mensagem_erro)
    """
    # Valida data
    if not data:
        return False, "Data é obrigatória"
    
    if isinstance(data, str):
        try:
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            return False, "Data inválida. Use formato YYYY-MM-DD"
    
    # Valida descrição
    if not descricao or not str(descricao).strip():
        return False, "Descrição é obrigatória"
    
    # Valida valor
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor deve ser maior que zero"
    except (ValueError, TypeError):
        return False, "Valor inválido"
    
    # Valida tipo
    if tipo not in ("Receita", "Despesa"):
        return False, "Tipo deve ser 'Receita' ou 'Despesa'"
    
    # Valida categoria
    if not categoria or not str(categoria).strip():
        return False, "Categoria é obrigatória"
    
    return True, ""


def criar_transacao(
    data: date | str,
    descricao: str,
    valor: float,
    tipo: str,
    categoria: str,
) -> tuple[bool, str, int | None]:
    """Cria uma nova transação com validação.
    
    Args:
        data: Data da transação
        descricao: Descrição
        valor: Valor
        tipo: Tipo
        categoria: Categoria
    
    Returns:
        Tupla (sucesso, mensagem, id_criado)
    """
    # Valida
    valido, erro = validar_transacao(data, descricao, valor, tipo, categoria)
    if not valido:
        return False, erro, None
    
    # Cria no banco
    try:
        transacao_id = dao.add_transacao(data, descricao, valor, tipo, categoria)
        return True, "Transação criada com sucesso!", transacao_id
    except Exception as e:
        return False, f"Erro ao criar transação: {str(e)}", None


def atualizar_transacao(
    transacao_id: int,
    data: date | str,
    descricao: str,
    valor: float,
    tipo: str,
    categoria: str,
) -> tuple[bool, str]:
    """Atualiza uma transação existente com validação.
    
    Args:
        transacao_id: ID da transação
        data: Nova data
        descricao: Nova descrição
        valor: Novo valor
        tipo: Novo tipo
        categoria: Nova categoria
    
    Returns:
        Tupla (sucesso, mensagem)
    """
    # Valida
    valido, erro = validar_transacao(data, descricao, valor, tipo, categoria)
    if not valido:
        return False, erro
    
    # Atualiza no banco
    try:
        sucesso = dao.update_transacao(transacao_id, data, descricao, valor, tipo, categoria)
        if sucesso:
            return True, "Transação atualizada com sucesso!"
        else:
            return False, "Transação não encontrada"
    except Exception as e:
        return False, f"Erro ao atualizar transação: {str(e)}"


def deletar_transacao(transacao_id: int) -> tuple[bool, str]:
    """Deleta uma transação.
    
    Args:
        transacao_id: ID da transação
    
    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        sucesso = dao.delete_transacao(transacao_id)
        if sucesso:
            return True, "Transação deletada com sucesso!"
        else:
            return False, "Transação não encontrada"
    except Exception as e:
        return False, f"Erro ao deletar transação: {str(e)}"
