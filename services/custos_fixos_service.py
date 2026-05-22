"""Service para gerenciar custos fixos no Supabase."""

from __future__ import annotations

from typing import Any
import pandas as pd
from supabase import Client

from services.supabase_client import get_supabase_client
from services.financas_service import insert_financa


def load_custos_fixos() -> pd.DataFrame:
    """Carrega custos fixos do Supabase."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("custos_fixos").select("*").order("descricao").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        else:
            return pd.DataFrame(columns=[
                "id", "descricao", "tipo", "valor", "entrada", "dia_vencimento",
                "parcela_atual", "total_parcelas", "ativo", "created_at"
            ])
    except Exception as e:
        st.error(f"Erro ao carregar custos fixos: {e}")
        return pd.DataFrame()


def insert_custo_fixo(data: dict[str, Any]) -> bool:
    """Insere novo custo fixo."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("custos_fixos").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir custo fixo: {e}")
        return False


def update_custo_fixo(custo_id: int, data: dict[str, Any]) -> bool:
    """Atualiza custo fixo existente."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("custos_fixos").update(data).eq("id", custo_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar custo fixo: {e}")
        return False


def delete_custo_fixo(custo_id: int) -> bool:
    """Deleta custo fixo."""
    supabase: Client = get_supabase_client()
    
    try:
        response = supabase.table("custos_fixos").delete().eq("id", custo_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar custo fixo: {e}")
        return False


def gerar_lancamentos_automaticos(ano: int, mes: int) -> bool:
    """Gera lançamentos automáticos em finanças baseado nos custos fixos ativos."""
    custos_fixos = load_custos_fixos()
    
    if custos_fixos.empty:
        return True
    
    # Filtra apenas custos ativos
    custos_ativos = custos_fixos[custos_fixos["ativo"] == True]
    
    sucesso = True
    for _, custo in custos_ativos.iterrows():
        # Verifica se é parcelado e se ainda tem parcelas
        if custo["tipo"] == "parcelado":
            if custo["parcela_atual"] > custo["total_parcelas"]:
                continue
        
        # Cria lançamento em finanças
        lancamento = {
            "ano": ano,
            "mes": mes,
            "data": f"{ano}-{mes:02d}-{custo['dia_vencimento']:02d}",
            "descricao": f"{custo['descricao']} (automático)",
            "tipo": "despesa",
            "valor": custo["valor"],
            "entrada": custo.get("entrada", False),
            "categoria": "Custo Fixo"
        }
        
        if not insert_financa(lancamento):
            sucesso = False
        
        # Se parcelado, incrementa parcela_atual
        if custo["tipo"] == "parcelado":
            nova_parcela = custo["parcela_atual"] + 1
            if nova_parcela > custo["total_parcelas"]:
                # Desativa se chegou na última parcela
                update_custo_fixo(custo["id"], {
                    "parcela_atual": nova_parcela,
                    "ativo": False
                })
            else:
                update_custo_fixo(custo["id"], {
                    "parcela_atual": nova_parcela
                })
    
    return sucesso
