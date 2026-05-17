# Clínica Financeira

App de controle financeiro pessoal feito em Streamlit.

## O que tem aqui

- **Plantões**: calcula líquido com impostos (ISS, INSS, IR)
- **Finanças**: lançamentos do mês + custos fixos
- **Casamento**: planejamento financeiro do casamento

## Como usar

```bash
# Instalar
pip install -r requirements.txt

# Rodar
streamlit run app.py
```

**Login:**
- Usuário: Carol Gomes
- Senha: Thalis2002@

## Estrutura

```
organizador/        # código principal
├── auth.py        # login/logout
├── storage.py     # salva login no navegador
├── plantoes.py    # cálculos de plantões
├── store.py       # JSON local
└── ui.py          # componentes visuais

pages/             # páginas do app
├── 1_Plantoes.py
├── 2_Financas.py
└── 3_Casamento.py

data/              # dados salvos
└── usuario.json   # seus dados ficam aqui
```

## Dados

Tudo fica salvo em `data/usuario.json`. Faça backup de vez em quando.

## Cálculos de Plantões (2026)

- Valor: R$ 656,40 por plantão
- ISS: 5%
- INSS: 11% (teto R$ 8.157,36)
- IR: progressivo conforme tabela oficial

## Login Persistente

O login fica salvo no navegador. Só precisa fazer uma vez.

Para sair: botão "Sair" na barra lateral.

## Notas

- Dados só salvam quando você clica em "Salvar"
- F5 não deslo

ga mais
- Cada página carrega automaticamente seus dados

---

Feito com Streamlit + Python
