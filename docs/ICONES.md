# Ícones

O projeto usa ícones do [Lucide](https://lucide.dev/).

## Como usar

```python
from organizador.lucide import inline_svg

# Básico
inline_svg("heart")

# Com tamanho
inline_svg("check", 24)

# Com classe CSS
inline_svg("x", 16, "minha-classe")
```

## Ícones disponíveis

Os SVGs ficam em `organizador/_lucide_data.json`.

Para adicionar um novo:
1. Pegue o SVG no https://lucide.dev
2. Adicione no JSON com o nome em kebab-case
3. Use no código

## Fallback

Se um ícone não existir, aparece um círculo vazio por padrão.

## Validação

Para checar se todos os ícones usados existem:

```bash
python scripts/validate_icons.py
```
