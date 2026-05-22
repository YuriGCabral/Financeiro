"""Service para gerenciar plantões no Supabase."""

from __future__ import annotations

from typing import Any
import pandas as pd
from supabase import Client

from services.supabase_client import get_supabase_client


def load_plantoes(ano: int | None = None) -> pd.DataFrame:
    """Carrega plantões do Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        query = supabase.table("plantoes").select("*")
        
        if ano:
            query = query.eq("ano", ano)
        
        response = query.order("ano", desc=True).order("mes").execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame(columns=[
                "id", "ano", "mes", "quantidade", "valor_bruto", 
                "imposto", "valor_liquido", "entrada", "created_at"
            ])
    except Exception as e:
        raise Exception(f"Erro ao carregar plantões: {e}")


def insert_plantao(data: dict[str, Any]) -> None:
    """Insere novo plantão no Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("plantoes").insert(data).execute()
    except Exception as e:
        raise Exception(f"Erro ao inserir plantão: {e}")


def update_plantao(plantao_id: int, data: dict[str, Any]) -> None:
    """Atualiza plantão existente."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("plantoes").update(data).eq("id", plantao_id).execute()
    except Exception as e:
        raise Exception(f"Erro ao atualizar plantão: {e}")


def delete_plantao(plantao_id: int) -> None:
    """Deleta plantão do Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        supabase.table("plantoes").delete().eq("id", plantao_id).execute()
    except Exception as e:
        raise Exception(f"Erro ao deletar plantão: {e}")
