# App Financeiro SQLite

Um exemplo de app com arquitetura em camadas.

Fica em `main_financas.py` - rode separado do app principal.

## Estrutura

```
db/
  connection.py  # SQLite
  dao.py         # CRUD
services/
  financas.py    # cálculos
main_financas.py # UI
```

## Rodar

```bash
streamlit run main_financas.py
```

## Diferença do app principal

- Usa SQLite ao invés de JSON
- Mais estruturado
- Exemplo de arquitetura em camadas

Serve como referência se quiser migrar o app principal pro SQLite no futuro.
