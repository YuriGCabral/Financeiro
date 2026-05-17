# Autenticação

Login simples com credenciais fixas.

## Credenciais

- **Usuário:** Carol Gomes
- **Senha:** Thalis2002@

## Como funciona

1. Login salva um token no localStorage do navegador
2. Token persiste mesmo fechando o navegador
3. Logout limpa tudo

## Arquivos

- `organizador/auth.py` - lógica de login/logout
- `organizador/storage.py` - salva no navegador
- `organizador/login_ui.py` - tela de login

## Fluxo

```
Login → salva token → recarrega app
F5 → lê token → autentica automaticamente
Logout → limpa token → volta pro login
```

## Segurança

Token = hash SHA256 do username.

Não é criptografia forte, mas serve para uso pessoal.
