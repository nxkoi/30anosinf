# Deploy na VM temporária

## Acesso atual

Enquanto o DNS não existir, use o IP da VM:

```text
http://IP/
http://IP/contribuir
http://IP/acervo
http://IP/revisao
```

Atualize `API_CORS_ORIGINS` e `PUBLIC_HOST` no `.env` com esse IP.

## Subir

```bash
cd /home/supdanilo/30anosinf
make up
make seed
make verify
```

## DNS futuro

Quando `30anos.inf.ufg.br` e `revisao.30anos.inf.ufg.br` apontarem para a VM:

1. Ajuste o `infra/caddy/Caddyfile` para os blocos com `tls` / hostnames (já documentados como próximo passo).
2. Libere a porta 443.
3. Remova `auto_https off` / `email off` conforme política do CERCOMP.

## Credenciais de revisão

- Caddy: `REVIEW_USERNAME` + `REVIEW_PASSWORD_HASH`
- API: `REVIEW_USERNAME` + `REVIEW_PASSWORD` (texto, só no ambiente)

Na UI de revisão, informe as mesmas credenciais na sessão do navegador para as chamadas `/api/review/*`.

## Recursos

A VM de ~2 GB usa `mem_limit` nos serviços. Se houver OOM, reduza paralelismo ou aumente a memória.
