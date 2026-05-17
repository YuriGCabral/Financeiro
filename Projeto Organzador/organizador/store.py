"""Persistência local em JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from organizador.paths import ROOT

DATA_DIR = ROOT / "data"
STORE_PATH = DATA_DIR / "usuario.json"

DEFAULT_MONTHS_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _default_store() -> dict[str, Any]:
    zeros = [0.0] * 12
    return {
        "plantoes": {
            "2025": {"meses": DEFAULT_MONTHS_PT.copy(), "quantidades": zeros.copy()},
            "2026": {"meses": DEFAULT_MONTHS_PT.copy(), "quantidades": zeros.copy()},
        },
        "financas": {},
        "custos_fixos": [],
        "casamento": [],
    }


def load_store() -> dict[str, Any]:
    """Carrega dados do JSON ou cria arquivo se não existir."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.is_file():
        data = _default_store()
        save_store(data)
        return data
    try:
        raw = STORE_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        data = _default_store()
    
    # Garante estrutura mínima
    base = _default_store()
    if "plantoes" not in data or not isinstance(data["plantoes"], dict):
        data["plantoes"] = base["plantoes"]
    if "financas" not in data or not isinstance(data["financas"], dict):
        data["financas"] = {}
    if "custos_fixos" not in data or not isinstance(data["custos_fixos"], list):
        data["custos_fixos"] = []
    if "casamento" not in data or not isinstance(data["casamento"], list):
        data["casamento"] = []
    for year in ("2025", "2026"):
        if year not in data["plantoes"]:
            data["plantoes"][year] = {
                "meses": DEFAULT_MONTHS_PT.copy(),
                "quantidades": [0.0] * 12,
            }
        else:
            block = data["plantoes"][year]
            if not isinstance(block, dict):
                data["plantoes"][year] = base["plantoes"][year].copy()
                continue
            q = block.get("quantidades")
            if not isinstance(q, list) or len(q) != 12:
                block["quantidades"] = [0.0] * 12
            m = block.get("meses")
            if not isinstance(m, list) or len(m) != 12:
                block["meses"] = DEFAULT_MONTHS_PT.copy()
    return data


def save_store(data: dict[str, Any]) -> None:
    """Salva dados no JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def financas_key(ano: int, mes: int) -> str:
    return f"{ano:04d}-{mes:02d}"
