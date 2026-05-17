"""Resolve arquivos Excel na raiz do projeto (nomes podem variar com acentos no disco)."""

from __future__ import annotations

from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]


def _first_match(glob_pattern: str) -> Path | None:
    matches = sorted(ROOT.glob(glob_pattern))
    return matches[0] if matches else None


def plantoes_workbook() -> Path | None:
    return _first_match("Plant*Impost*.xlsx*")


def financas_workbook() -> Path | None:
    return _first_match("Finan*.xlsx")
