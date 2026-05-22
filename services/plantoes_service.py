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
            df = pd.DataFrame(response.data)
            return df
        else:
            return pd.DataFrame(columns=[
                "id", "ano", "mes", "quantidade", "valor_bruto", 
                "imposto", "valor_liquido", "entrada", "created_at"
            ])
    except Exception as e:
        st.error(f"Erro ao carregar plantões: {e}")
        return pd.DataFrame()


def insert_plantao(data: dict[str, Any]) -> bool:
    """Insere novo plantão no Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("plantoes").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir plantão: {e}")
        return False


def update_plantao(plantao_id: int, data: dict[str, Any]) -> bool:
    """Atualiza plantão existente."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("plantoes").update(data).eq("id", plantao_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar plantão: {e}")
        return False


def delete_plantao(plantao_id: int) -> bool:
    """Deleta plantão do Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("plantoes").delete().eq("id", plantao_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar plantão: {e}")
        return False
