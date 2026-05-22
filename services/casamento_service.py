"""Service para gerenciar gastos do casamento no Supabase."""

from __future__ import annotations

from typing import Any
import pandas as pd
from supabase import Client

from services.supabase_client import get_supabase_client


def load_casamento() -> pd.DataFrame:
    """Carrega gastos do casamento do Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("casamento").select("*").order("categoria").order("item").execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame(columns=[
                "id", "categoria", "item", "orcamento", "valor_pago",
                "entrada", "valor_restante", "status", "observacoes", "created_at"
            ])
    except Exception as e:
        raise Exception(f"Erro ao carregar gastos do casamento: {e}")


def insert_gasto_casamento(data: dict[str, Any]) -> None:
    """Insere novo gasto do casamento."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("casamento").insert(data).execute()
    except Exception as e:
        raise Exception(f"Erro ao inserir gasto: {e}")


def update_gasto_casamento(gasto_id: int, data: dict[str, Any]) -> None:
    """Atualiza gasto do casamento existente."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("casamento").update(data).eq("id", gasto_id).execute()
    except Exception as e:
        raise Exception(f"Erro ao atualizar gasto: {e}")


def delete_gasto_casamento(gasto_id: int) -> None:
    """Deleta gasto do casamento."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("casamento").delete().eq("id", gasto_id).execute()
    except Exception as e:
        raise Exception(f"Erro ao deletar gasto: {e}")
