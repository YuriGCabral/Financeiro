"""
Cálculo de plantões.

Valores 2026:
- Plantão: R$ 656,402
- ISS: 5%
- INSS: 11% (teto R$ 8.157,36)
- IR: progressivo

Tabela IR (base = bruto - INSS):
- até 2428,8 → isento
- até 2826,65 → 7,5% - 184
- até 3751,05 → 15% - 396
- até 4664,68 → 22,5% - 678
- acima → 27,5% - 911
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import BinaryIO, Iterable

import openpyxl
import pandas as pd

VALOR_PLANTAO = Decimal("656.402")
TETO_INSS = Decimal("8157.36")
ALIQUOTA_INSS = Decimal("0.11")
ALIQUOTA_ISS = Decimal("0.05")


def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calc_irrf(valor_bruto: Decimal, inss: Decimal) -> Decimal:
    """Calcula IR usando tabela progressiva 2026."""
    base = valor_bruto - inss
    if base <= Decimal("2428.8"):
        inner = Decimal("0")
    elif base <= Decimal("2826.65"):
        inner = base * Decimal("0.075") - Decimal("184")
    elif base <= Decimal("3751.05"):
        inner = base * Decimal("0.15") - Decimal("396")
    elif base <= Decimal("4664.68"):
        inner = base * Decimal("0.225") - Decimal("678")
    else:
        inner = base * Decimal("0.275") - Decimal("911")
    return _q2(inner)


def calc_from_plantoes(plantoes: float | Decimal) -> dict[str, float]:
    b = Decimal(str(plantoes or 0))
    c = _q2(b * VALOR_PLANTAO)
    d = _q2(c * ALIQUOTA_ISS)
    e = _q2(min(c, TETO_INSS) * ALIQUOTA_INSS)
    f = calc_irrf(c, e)
    g = _q2(c - (d + e + f))
    return {
        "plantoes": float(b),
        "valor_bruto": float(c),
        "iss": float(d),
        "inss": float(e),
        "irrf": float(f),
        "liquido": float(g),
    }


MONTH_ROWS = list(range(2, 14))  # linhas 2–13: Janeiro … Dezembro


@dataclass
class PlantoesSheetState:
    sheet_name: str
    meses: list[str]
    plantoes: list[float]


def read_plantoes_sheet(path: Path, sheet_name: str) -> PlantoesSheetState:
    """Lê quantidades de plantões de uma aba do Excel."""
    wb = openpyxl.load_workbook(path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Aba inexistente: {sheet_name}")
    ws = wb[sheet_name]
    
    meses: list[str] = []
    plantoes: list[float] = []
    for r in MONTH_ROWS:
        m = ws.cell(r, 1).value
        b = ws.cell(r, 2).value
        meses.append(str(m or "").strip())
        try:
            plantoes.append(float(b or 0))
        except (TypeError, ValueError):
            plantoes.append(0.0)
    return PlantoesSheetState(sheet_name=sheet_name, meses=meses, plantoes=plantoes)


def dataframe_resumo(plantoes_por_mes: Iterable[float], meses: list[str] | None = None) -> pd.DataFrame:
    rows = []
    for i, q in enumerate(plantoes_por_mes):
        r = calc_from_plantoes(q)
        nome_mes = meses[i] if meses and i < len(meses) else f"Mês {i + 1}"
        rows.append(
            {
                "Mês": nome_mes,
                "Plantões": r["plantoes"],
                "Valor bruto": r["valor_bruto"],
                "ISS": r["iss"],
                "INSS": r["inss"],
                "IRRF": r["irrf"],
                "Líquido": r["liquido"],
            }
        )
    return pd.DataFrame(rows)


def write_plantoes_column_b(
    path: Path, sheet_name: str, plantoes_por_mes: list[float], destino: Path | BinaryIO
) -> None:
    """Grava quantidades de plantões na coluna B do Excel."""
    wb = openpyxl.load_workbook(path)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Aba inexistente: {sheet_name}")
    ws = wb[sheet_name]
    for idx, r in enumerate(MONTH_ROWS):
        val = plantoes_por_mes[idx] if idx < len(plantoes_por_mes) else 0
        ws.cell(r, 2).value = float(val)
    wb.save(destino)
    if isinstance(destino, io.BytesIO):
        destino.seek(0)
