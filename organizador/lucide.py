"""Ícones Lucide (SVG) embutidos via `assets/lucide_data.json`."""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.parse
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "assets" / "lucide_data.json"
_FALLBACK_ICON = "circle"

logger = logging.getLogger(__name__)


def validate_assets() -> bool:
    """Valida que a pasta assets existe e contém os arquivos necessários."""
    assets_dir = Path(__file__).parent.parent / "assets"
    
    if not assets_dir.exists():
        logger.error(f"Pasta assets não encontrada: {assets_dir}")
        return False
    
    try:
        files = os.listdir(str(assets_dir))
        logger.info(f"Arquivos em assets/: {files}")
        
        if "lucide_data.json" not in files:
            logger.error("lucide_data.json não encontrado em assets/")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Erro ao validar assets: {e}")
        return False


@lru_cache(maxsize=1)
def _icons() -> dict[str, str]:
    """Carrega todos os ícones do arquivo JSON."""
    validate_assets()
    
    try:
        raw = _DATA_PATH.read_text(encoding="utf-8")
        return json.loads(raw)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao carregar ícones: {e}")
        logger.error(f"Caminho tentado: {_DATA_PATH}")
        return {}


def _get_icon_svg(name: str) -> str:
    """Obtém o SVG do ícone com fallback seguro."""
    icons = _icons()
    
    if name in icons:
        return icons[name]
    
    # Tenta normalizar nome (kebab-case)
    normalized = name.lower().replace("_", "-")
    if normalized in icons:
        logger.warning(f"Ícone '{name}' não encontrado, usando '{normalized}'")
        return icons[normalized]
    
    # Fallback para ícone padrão
    if _FALLBACK_ICON in icons:
        logger.warning(f"Ícone '{name}' não encontrado, usando fallback '{_FALLBACK_ICON}'")
        return icons[_FALLBACK_ICON]
    
    # Último recurso: SVG vazio minimalista
    logger.error(f"Ícone '{name}' não encontrado e fallback '{_FALLBACK_ICON}' ausente")
    return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/></svg>'


def inline_svg(name: str, size: int = 20, class_name: str = "lucide-ic") -> str:
    """Retorna SVG inline do ícone com tamanho e classe customizados.
    
    Args:
        name: Nome do ícone (kebab-case, ex: 'heart-pulse')
        size: Tamanho em pixels
        class_name: Classe CSS para o SVG
    
    Returns:
        String HTML com o SVG do ícone
    """
    svg = _get_icon_svg(name)
    svg = re.sub(r'width="\d+"', f'width="{size}"', svg, count=1)
    svg = re.sub(r'height="\d+"', f'height="{size}"', svg, count=1)
    if 'class="' not in svg:
        svg = svg.replace("<svg ", f'<svg class="{class_name}" ', 1)
    return svg


def svg_data_uri(name: str) -> str:
    """Retorna data URI do ícone para uso em CSS."""
    svg = _get_icon_svg(name)
    return "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(svg)


def sidebar_nav_icon_css() -> str:
    """Ícones na navegação lateral (Streamlit) via ::before + data-uri."""
    rules: list[str] = []
    # Início (primeiro item costuma ser o script principal)
    house = svg_data_uri("house")
    rules.append(
        f"""
[data-testid="stSidebarNavItems"] > li:first-child [data-testid="stSidebarNavLink"]::before {{
  background-image: url("{house}");
}}
"""
    )
    mapping = [
        (["Plantoes", "plantoes", "1_P"], "stethoscope"),
        (["Financas", "financas", "2_F"], "wallet"),
        (["Casamento", "casamento", "3_C"], "heart"),
        (["Aulas", "aulas", "tarefas", "Tarefas"], "clipboard-list"),
    ]
    for needles, icon in mapping:
        uri = svg_data_uri(icon)
        for n in needles:
            rules.append(
                f"""
[data-testid="stSidebarNavLink"][href*="{n}"]::before {{
  background-image: url("{uri}");
}}
"""
            )
    return "<style>" + "\n".join(rules) + "\n" + _sidebar_icon_base_css() + "</style>"


def _sidebar_icon_base_css() -> str:
    return """
[data-testid="stSidebarNavLink"] {
  position: relative;
  min-height: 44px;
  display: flex;
  align-items: center;
}
[data-testid="stSidebarNavLink"]::before {
  content: "";
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  background: none no-repeat center / contain;
  opacity: 0.95;
}
[data-testid="stSidebarNavLink"] {
  padding-left: 40px !important;
  padding-top: 10px !important;
  padding-bottom: 10px !important;
}
"""
