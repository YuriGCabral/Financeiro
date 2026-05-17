"""Data Access Object (DAO) para operações CRUD de transações."""

from __future__ import annotations

from datetime import date
from typing import Any

from db.connection import get_connection


def get_transacoes() -> list[dict[str, Any]]:
    """Busca todas as transações do banco.
    
    Returns:
        Lista de dicionários com dados das transações
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, data, descricao, valor, tipo, categoria
            FROM transacoes
            ORDER BY data DESC, id DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_transacao_by_id(transacao_id: int) -> dict[str, Any] | None:
    """Busca uma transação específica por ID.
    
    Args:
        transacao_id: ID da transação
    
    Returns:
        Dicionário com dados da transação ou None se não encontrada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, data, descricao, valor, tipo, categoria
            FROM transacoes
            WHERE id = ?
        """, (transacao_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None


def add_transacao(
    data: date | str,
    descricao: str,
    valor: float,
    tipo: str,
    categoria: str,
) -> int:
    """Adiciona uma nova transação ao banco.
    
    Args:
        data: Data da transação (date ou string YYYY-MM-DD)
        descricao: Descrição da transação
        valor: Valor da transação (positivo)
        tipo: Tipo da transação ('Receita' ou 'Despesa')
        categoria: Categoria da transação
    
    Returns:
        ID da transação criada
    
    Raises:
        ValueError: Se dados inválidos
    """
    # Validações
    if not descricao or not descricao.strip():
        raise ValueError("Descrição não pode ser vazia")
    
    if valor <= 0:
        raise ValueError("Valor deve ser maior que zero")
    
    if tipo not in ("Receita", "Despesa"):
        raise ValueError("Tipo deve ser 'Receita' ou 'Despesa'")
    
    if not categoria or not categoria.strip():
        raise ValueError("Categoria não pode ser vazia")
    
    # Converte data se necessário
    if isinstance(data, date):
        data_str = data.isoformat()
    else:
        data_str = str(data)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transacoes (data, descricao, valor, tipo, categoria)
            VALUES (?, ?, ?, ?, ?)
        """, (data_str, descricao.strip(), valor, tipo, categoria.strip()))
        
        conn.commit()
        return cursor.lastrowid


def update_transacao(
    transacao_id: int,
    data: date | str,
    descricao: str,
    valor: float,
    tipo: str,
    categoria: str,
) -> bool:
    """Atualiza uma transação existente.
    
    Args:
        transacao_id: ID da transação a atualizar
        data: Nova data
        descricao: Nova descrição
        valor: Novo valor
        tipo: Novo tipo
        categoria: Nova categoria
    
    Returns:
        True se atualizou, False se transação não existe
    
    Raises:
        ValueError: Se dados inválidos
    """
    # Validações
    if not descricao or not descricao.strip():
        raise ValueError("Descrição não pode ser vazia")
    
    if valor <= 0:
        raise ValueError("Valor deve ser maior que zero")
    
    if tipo not in ("Receita", "Despesa"):
        raise ValueError("Tipo deve ser 'Receita' ou 'Despesa'")
    
    if not categoria or not categoria.strip():
        raise ValueError("Categoria não pode ser vazia")
    
    # Converte data se necessário
    if isinstance(data, date):
        data_str = data.isoformat()
    else:
        data_str = str(data)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes
            SET data = ?, descricao = ?, valor = ?, tipo = ?, categoria = ?
            WHERE id = ?
        """, (data_str, descricao.strip(), valor, tipo, categoria.strip(), transacao_id))
        
        conn.commit()
        return cursor.rowcount > 0


def delete_transacao(transacao_id: int) -> bool:
    """Deleta uma transação do banco.
    
    Args:
        transacao_id: ID da transação a deletar
    
    Returns:
        True se deletou, False se transação não existe
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM transacoes
            WHERE id = ?
        """, (transacao_id,))
        
        conn.commit()
        return cursor.rowcount > 0


def delete_all_transacoes() -> int:
    """Deleta todas as transações (usar com cuidado!).
    
    Returns:
        Número de transações deletadas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes")
        
        conn.commit()
        return cursor.rowcount


def get_transacoes_by_tipo(tipo: str) -> list[dict[str, Any]]:
    """Busca transações por tipo.
    
    Args:
        tipo: 'Receita' ou 'Despesa'
    
    Returns:
        Lista de transações do tipo especificado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, data, descricao, valor, tipo, categoria
            FROM transacoes
            WHERE tipo = ?
            ORDER BY data DESC, id DESC
        """, (tipo,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_transacoes_by_categoria(categoria: str) -> list[dict[str, Any]]:
    """Busca transações por categoria.
    
    Args:
        categoria: Nome da categoria
    
    Returns:
        Lista de transações da categoria especificada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, data, descricao, valor, tipo, categoria
            FROM transacoes
            WHERE categoria = ?
            ORDER BY data DESC, id DESC
        """, (categoria,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
