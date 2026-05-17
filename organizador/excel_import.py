"""Importação opcional a partir de Excel — só para mesclar/atualizar dados locais."""

from __future__ import annotations

from pathlib import Path

from organizador.paths import plantoes_workbook
from organizador.plantoes import read_plantoes_sheet


def try_import_plantoes(year_sheet: str) -> tuple[list[str], list[float]] | None:
    path = plantoes_workbook()
    if not path:
        return None
    try:
        state = read_plantoes_sheet(path, year_sheet)
    except Exception:
        return None
    return state.meses, state.plantoes


def template_plantoes_path() -> Path | None:
    return plantoes_workbook()
