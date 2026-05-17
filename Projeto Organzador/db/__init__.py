"""Módulo de acesso a dados."""

from db.connection import get_connection, get_db_path, init_database
from db.dao import (
    add_transacao,
    delete_all_transacoes,
    delete_transacao,
    get_transacao_by_id,
    get_transacoes,
    get_transacoes_by_categoria,
    get_transacoes_by_tipo,
    update_transacao,
)

__all__ = [
    "get_connection",
    "get_db_path",
    "init_database",
    "add_transacao",
    "delete_all_transacoes",
    "delete_transacao",
    "get_transacao_by_id",
    "get_transacoes",
    "get_transacoes_by_categoria",
    "get_transacoes_by_tipo",
    "update_transacao",
]
