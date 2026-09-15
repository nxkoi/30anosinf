# 30 anos do INF/UFG — Acervo temporário

Site temporário para receber, revisar e publicar fotografias e relatos dos 30 anos do Instituto de Informática da UFG.

## Visão geral

Fluxo da v0.1:

```text
formulário /contribuir
→ API (PostgreSQL + MinIO quarentena)
→ fila Redis/RQ
→ worker (miniatura + análise simulada)
→ /revisao (Basic Auth)
→ aprovação / publicação
→ /acervo (somente PUBLISHED)
```

Providers reais de LLM/imagem **ainda não são chamados** — apenas `MockImageAnalysisProvider` e `MockLLMProvider`.

## Requisitos

- Docker Engine + Docker Compose v2
- Portas 80 (e 443 reservada) livres na VM
- ~2 GB RAM recomendados

## Configuração do `.env`

```bash
cp .env.example .env
```

Preencha pelo menos:

| Variável | Função |
|---|---|
| `REVIEW_USERNAME` / `REVIEW_PASSWORD` | Login da área e da API de revisão |
| `REVIEW_PASSWORD_HASH` | Hash bcrypt para o Caddy (`$$` escapado no Compose) |
| `POSTGRES_PASSWORD` | Senha do banco |
| `MINIO_ROOT_PASSWORD` | Senha do MinIO |
| `API_CORS_ORIGINS` | Origens permitidas (IP da VM, localhost) |

Gerar hash da senha de revisão:

```bash
docker run --rm caddy:2.9-alpine caddy hash-password --plaintext 'sua-senha'
```

No `.env`, cada `$` do hash deve virar `$$` (interpolação do Compose).

## Inicialização

```bash
make setup   # se ainda não houver .env
make up      # build + sobe stack
make seed    # marcos históricos + submissão demo (não publicada)
make verify  # checagens básicas
```

## Acesso

Na VM temporária (substitua pelo IP):

- Site: `http://IP/`
- Contribuir: `http://IP/contribuir`
- Acervo: `http://IP/acervo`
- Revisão: `http://IP/revisao` (HTTP Basic no Caddy)

O Caddyfile já está preparado para, após DNS/TLS:

- `https://30anos.inf.ufg.br`
- `https://revisao.30anos.inf.ufg.br`

## Migrations

Rodam automaticamente na subida da API (`alembic upgrade head`). Manualmente:

```bash
make migrate
```

## Testes

```bash
make test
```

Cobrem health, upload, rejeições, deduplicação, worker, auth da revisão, bloqueio de publicação sem autorização, aprovação, publicação e visibilidade no acervo.

## Logs

```bash
make logs
# ou
docker compose logs -f api worker caddy
```

## Backup dos volumes

Volumes Compose: `postgres_data`, `minio_data`, `redis_data`, `caddy_data`.

Exemplo:

```bash
docker compose stop
docker run --rm -v 30anosinf_postgres_data:/data -v "$PWD/backup:/backup" alpine tar czf /backup/postgres.tgz -C /data .
docker run --rm -v 30anosinf_minio_data:/data -v "$PWD/backup:/backup" alpine tar czf /backup/minio.tgz -C /data .
```

## Trocar providers simulados

Variáveis `IMAGE_PROVIDER` e `LLM_PROVIDER` (hoje só `mock`). Implemente classes em `apps/api/app/providers/` seguindo `ImageAnalysisProvider` / `LLMProvider` e selecione via env — **sem alterar o restante do fluxo**.

## Limitações atuais

- Sem CAPTCHA, rate limit, antivírus, ZIP, confirmação de e-mail
- Sem agente construtor / publicações imutáveis / rollback
- Upload passa pela API (não presigned no browser)
- Análise de imagem é simulada
- Autenticação da revisão: Basic Auth (Caddy + API)

Veja `docs/next-steps.md`.

## Documentação

- `docs/architecture.md`
- `docs/deployment-vm.md`
- `docs/next-steps.md`
- `especificacao_acervo_30_anos.md`
- `template_visual_site_30anos_inf.md`
- `assets/README.md`

## Nota sobre MinIO nesta VM

Imagens recentes do MinIO exigem CPU x86-64-v2. Esta VM usa `quay.io/minio/minio:RELEASE.2023-03-20T20-16-18Z` por compatibilidade.

