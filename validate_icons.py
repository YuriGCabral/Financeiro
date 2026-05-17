#!/usr/bin/env python3
"""Valida que os icones estao carregando corretamente."""

import os
import sys
from pathlib import Path


def main():
    """Valida setup dos assets e icones."""
    print("Validando configuracao de icones...")
    print("-" * 50)
    
    # Verificar pasta assets
    assets_dir = Path(__file__).parent / "assets"
    
    if not assets_dir.exists():
        print("[ERROR] Pasta assets/ nao encontrada!")
        return False
    
    print(f"[OK] Pasta assets existe: {assets_dir}")
    
    # Listar arquivos
    print("\nArquivos em assets/:")
    try:
        files = os.listdir(str(assets_dir))
        if not files:
            print("[WARN] Pasta assets esta vazia!")
            return False
            
        for filename in sorted(files):
            filepath = assets_dir / filename
            size = filepath.stat().st_size
            print(f"  - {filename} ({size:,} bytes)")
    except Exception as e:
        print(f"[ERROR] Erro ao listar assets: {e}")
        return False
    
    # Verificar lucide_data.json
    lucide_file = assets_dir / "lucide_data.json"
    
    if not lucide_file.exists():
        print("\n[ERROR] lucide_data.json nao encontrado!")
        return False
    
    print(f"\n[OK] lucide_data.json encontrado")
    
    # Tentar carregar JSON
    try:
        import json
        
        with open(lucide_file, 'r', encoding='utf-8') as f:
            icon_data = json.load(f)
        
        print(f"[OK] JSON valido com {len(icon_data)} icones")
        
        # Listar alguns icones
        print("\nIcones disponiveis (amostra):")
        for i, icon_name in enumerate(sorted(icon_data.keys())[:10]):
            print(f"  - {icon_name}")
        
        if len(icon_data) > 10:
            print(f"  ... e mais {len(icon_data) - 10} icones")
            
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON invalido: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Erro ao carregar JSON: {e}")
        return False
    
    # Testar importacao do modulo
    print("\n" + "-" * 50)
    print("Testando modulo organizador.lucide...")
    
    try:
        from organizador.lucide import validate_assets, inline_svg
        
        if validate_assets():
            print("[OK] validate_assets() passou")
        else:
            print("[ERROR] validate_assets() falhou")
            return False
        
        # Testar alguns icones
        test_icons = ["house", "stethoscope", "wallet", "heart"]
        print("\nTestando icones:")
        
        for icon_name in test_icons:
            svg = inline_svg(icon_name, size=20)
            if svg and "<svg" in svg:
                print(f"  [OK] {icon_name}: {len(svg)} chars")
            else:
                print(f"  [WARN] {icon_name}: SVG vazio ou invalido")
                
    except ImportError as e:
        print(f"[ERROR] Erro ao importar modulo: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Erro ao testar icones: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Validacao completa! Icones prontos para uso.")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
