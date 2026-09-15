# Prompt para o Cursor — deploy em produção (máquina final)

Copie o bloco abaixo e cole em uma nova conversa do Cursor **na máquina final**, na pasta do repositório clonado.

---

```text
Você está na máquina FINAL de produção do projeto “30 anos do Instituto de Informática da UFG”.

## Contexto

- Repositório GitHub: https://github.com/nxkoi/30anosinf
- O DNS `30anos.inf.ufg.br` JÁ aponta para esta máquina.
- Planeje também `revisao.30anos.inf.ufg.br` (mesmo host ou CNAME para a mesma VM). Se o DNS de revisão ainda não existir, configure o Caddy mesmo assim e documente o pendente.
- O código já contém um MVP funcional com Docker Compose:
  - caddy, web (Astro estático), api (FastAPI), worker (RQ), postgres, redis, minio, minio-init
- Fluxo: formulário → upload → quarentena MinIO → PostgreSQL → Redis/RQ → análise mock → /revisao → aprovação/publicação → /acervo
- NÃO reinventar a aplicação. Monte, configure para produção e valide.
- NÃO integrar APIs reais de LLM/imagem nesta etapa (manter mock).
- NÃO commitar `.env` nem segredos.

## Objetivo

Deixar a aplicação no ar com HTTPS em:

- https://30anos.inf.ufg.br
- https://revisao.30anos.inf.ufg.br (Basic Auth na área /revisao e proteção equivalente)

## Passos obrigatórios

1. Inspecione o repositório (README.md, compose.yaml, infra/caddy/Caddyfile, .env.example, docs/).
2. Verifique pré-requisitos:
   - Docker Engine + Compose
   - usuário no grupo docker (ou use sudo/sg docker)
   - portas 80 e 443 livres
   - se a CPU NÃO suportar x86-64-v2, mantenha MinIO em
     `quay.io/minio/minio:RELEASE.2023-03-20T20-16-18Z`
     e mc em
     `quay.io/minio/mc:RELEASE.2023-03-20T17-17-53Z`
     (já usado na VM temporária por incompatibilidade de CPU).
3. Crie `.env` a partir de `.env.example` com senhas FORTES e novas (não reutilize as da VM temporária):
   - PUBLIC_HOST=30anos.inf.ufg.br
   - API_CORS_ORIGINS=https://30anos.inf.ufg.br,https://revisao.30anos.inf.ufg.br
   - REVIEW_USERNAME / REVIEW_PASSWORD fortes
   - REVIEW_PASSWORD_HASH gerado com Caddy; no .env do Compose escape cada `$` como `$$`
   - POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD fortes
   - DATABASE_URL coerente com usuário/senha/db
4. Atualize `infra/caddy/Caddyfile` para produção:
   - Remova `auto_https off` / modo só `:80` da VM temporária
   - Site público no host `30anos.inf.ufg.br` com TLS automático do Caddy
   - Área de revisão em `revisao.30anos.inf.ufg.br` com TLS + basicauth
   - Alternativa aceitável se só existir um hostname: manter `/revisao*` com basicauth em `30anos.inf.ufg.br`
   - Preserve reverse_proxy de `/api/*` para `api:8000`
   - Preserve headers de segurança
   - HTTP → HTTPS redirect
5. Suba a stack:
   ```bash
   make up
   make seed
   make verify
   ```
   Ajuste `scripts/verify.sh` se necessário para testar HTTPS e os hosts oficiais.
6. Valide explicitamente:
   - https://30anos.inf.ufg.br/ responde 200
   - https://30anos.inf.ufg.br/api/health responde ok
   - https://30anos.inf.ufg.br/contribuir carrega
   - /revisao exige autenticação
   - buckets MinIO existem e são privados
   - postgres/redis saudáveis
   - worker processa uma submissão de teste (ou a do seed fica READY_FOR_REVIEW)
7. Documente no README ou docs/deployment-vm.md:
   - URLs finais
   - como gerar o hash da senha de revisão
   - comando de backup dos volumes
   - limitações restantes (CAPTCHA, rate limit, etc. em docs/next-steps.md)

## Regras

- Preserve assets oficiais e content/sources.
- Não publique automaticamente a submissão demo do seed.
- Não exponha portas de Postgres/MinIO/Redis publicamente.
- Containers sem root quando já estiver assim.
- Se algo falhar (TLS, DNS, memória, MinIO/CPU), diagnostique e corrija; não declare sucesso sem teste real.

## Entrega ao final

Informe:
1. URLs ativas
2. o que mudou (Caddyfile, .env.example, verify, docs)
3. resultado de make verify / testes manuais HTTPS
4. usuário da revisão (NÃO imprima a senha em texto claro no chat se puder evitar; diga onde está no .env)
5. pendências (ex.: DNS de revisao.* ainda não criado)
```

---

## Como usar na máquina final

```bash
git clone https://github.com/nxkoi/30anosinf.git
cd 30anosinf
# abra no Cursor e cole o prompt acima
```

Se preferir começar manualmente antes do agente:

```bash
cp .env.example .env
# edite senhas, PUBLIC_HOST=30anos.inf.ufg.br e CORS https://...
docker run --rm caddy:2.9-alpine caddy hash-password --plaintext 'SUA_SENHA_FORTE'
# cole o hash no .env com cada $ virando $$
```
