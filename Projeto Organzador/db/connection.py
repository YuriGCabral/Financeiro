"""Gerenciamento de conexão com banco de dados SQLite."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

# Caminho do banco de dados
DB_PATH = Path(__file__).parent.parent / "data" / "financas.db"


def init_database() -> None:
    """Inicializa o banco de dados e cria tabelas se não existirem."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Cria tabela de transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('Receita', 'Despesa')),
            categoria TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Cria índices para melhor performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transacoes_data 
        ON transacoes(data)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transacoes_tipo 
        ON transacoes(tipo)
    """)
    
    conn.commit()
    conn.close()


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager para conexão com banco de dados.
    
    Yields:
        Conexão SQLite configurada
    
    Example:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacoes")
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    try:
        yield conn
    finally:
        conn.close()


def get_db_path() -> Path:
    """Retorna o caminho do banco de dados.
    
    Returns:
        Path do arquivo SQLite
    """
    return DB_PATH
