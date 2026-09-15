# Arquitetura (v0.1)

## Serviços

| Serviço | Função |
|---|---|
| `caddy` | Proxy único (80/443), headers de segurança, Basic Auth em `/revisao*` |
| `web` | Build estático Astro → volume `web_dist` |
| `api` | FastAPI: submissões, revisão, público, streaming de mídia |
| `worker` | RQ consumer: miniatura WebP + análise mock |
| `postgres` | Metadados |
| `redis` | Fila RQ |
| `minio` | Objetos privados |
| `minio-init` | Cria buckets privados |

## Buckets MinIO (privados)

- `submissions-quarantine`
- `originals`
- `derived`
- `approved-assets`

O navegador **nunca** recebe credenciais MinIO. Mídia pública sai por `GET /api/public/assets/{id}/media` somente se `PUBLISHED`.

## Estados de submissão

`RECEIVED → QUEUED → PROCESSING → READY_FOR_REVIEW → APPROVED → PUBLISHED` (também `CHANGES_REQUESTED`, `REJECTED`, `ERROR`).

## Providers

Interfaces em `apps/api/app/providers/`:

- `ImageAnalysisProvider`
- `LLMProvider`

Implementações atuais: `Mock*`. Seleção por `IMAGE_PROVIDER` / `LLM_PROVIDER`.

## Extensão CAPTCHA

No formulário (`/contribuir`), há comentário de extensão antes do `POST /api/submissions`. Validar no servidor quando for adicionado.
