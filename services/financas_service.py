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
            df = pd.DataFrame(response.data)
            return df
        else:
            return pd.DataFrame(columns=[
                "id", "ano", "mes", "data", "descricao", "tipo", 
                "valor", "entrada", "categoria", "created_at"
            ])
    except Exception as e:
        st.error(f"Erro ao carregar finanças: {e}")
        return pd.DataFrame()


def insert_financa(data: dict[str, Any]) -> bool:
    """Insere novo lançamento financeiro."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("financas").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir lançamento: {e}")
        return False


def update_financa(financa_id: int, data: dict[str, Any]) -> bool:
    """Atualiza lançamento financeiro existente."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("financas").update(data).eq("id", financa_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar lançamento: {e}")
        return False


def delete_financa(financa_id: int) -> bool:
    """Deleta lançamento financeiro."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("financas").delete().eq("id", financa_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar lançamento: {e}")
        return False
