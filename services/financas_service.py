"""Service para gerenciar finanças no Supabase."""

from __future__ import annotations

from typing import Any
import pandas as pd
from supabase import Client

from services.supabase_client import get_supabase_client


def load_financas(ano: int | None = None, mes: int | None = None) -> pd.DataFrame:
    """Carrega lançamentos financeiros do Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        query = supabase.table("financas").select("*")
        
        if ano:
            query = query.eq("ano", ano)
        if mes:
            query = query.eq("mes", mes)
        
        response = query.order("data", desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame(columns=[
                "id", "ano", "mes", "data", "descricao", "tipo", 
                "valor", "entrada", "categoria", "resolvido", "created_at"
            ])
    except Exception as e:
        raise Exception(f"Erro ao carregar finanças: {e}")


def insert_financa(data: dict[str, Any]) -> None:
    """Insere novo lançamento financeiro."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("financas").insert(data).execute()
    except Exception as e:
        raise Exception(f"Erro ao inserir lançamento: {e}")


def update_financa(financa_id: int, data: dict[str, Any]) -> None:
    """Atualiza lançamento financeiro existente."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("financas").update(data).eq("id", financa_id).execute()
    except Exception as e:
        raise Exception(f"Erro ao atualizar lançamento: {e}")


def delete_financa(financa_id: int) -> None:
    """Deleta lançamento financeiro."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("financas").delete().eq("id", financa_id).execute()
    except Exception as e:
        raise Exception(f"Erro ao deletar lançamento: {e}")
