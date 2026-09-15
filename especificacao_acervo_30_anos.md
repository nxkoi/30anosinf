# Especificação do Sistema — Acervo 30 Anos do INF/UFG

## 1. Objetivo

Criar um site temporário para os 30 anos do Instituto de Informática da UFG. Qualquer pessoa poderá enviar fotografias e relatos. O sistema analisará as imagens com IA e usará os materiais aprovados para construir uma narrativa histórica.

Nenhuma alteração será publicada automaticamente. Toda versão do site deverá ser aprovada por um administrador.

## 2. Endereços

- `https://30anos.inf.ufg.br`: site público.
- `https://30anos.inf.ufg.br/contribuir`: formulário público de envio.
- `https://revisao.30anos.inf.ufg.br`: prévia e painel protegidos por usuário e senha.
- SSH da VM: acesso à interface de terminal do agente.

## 3. Tecnologias

Todo o sistema será executado com Docker Compose.

- Caddy: proxy reverso, HTTPS e proteção do painel.
- Astro: site estático.
- FastAPI/Python: API, painel e serviços dos agentes.
- PostgreSQL: metadados, submissões, requisitos e revisões.
- Redis: fila de tarefas.
- MinIO: originais e imagens processadas.
- Git: versionamento do site e do conteúdo.

## 4. Serviços Docker

O `docker-compose.yml` deverá conter inicialmente:

```text
caddy
web-api
worker-ingest
agent-archive
agent-interactive
agent-site
publisher
postgres
redis
minio
site-public
site-preview
```

Os contêineres não devem executar como `root`, exceto quando indispensável. PostgreSQL e MinIO devem usar volumes persistentes.

## 5. Formulário público

O formulário deverá aceitar:

- nome;
- e-mail;
- vínculo com o INF/UFG;
- data ou período aproximado;
- local;
- evento ou ocasião;
- pessoas presentes;
- história ou relato;
- autoria da fotografia, se conhecida;
- autorização de uso e publicação;
- imagens ou arquivo ZIP.

O formulário não exigirá Conta Google. Deve ter CAPTCHA, limites de tamanho e limite de envios por IP.

O navegador enviará os arquivos diretamente ao MinIO usando autorização temporária criada pela API. O MinIO não será exposto publicamente e suas credenciais nunca serão enviadas ao navegador.

## 6. Armazenamento

Buckets do MinIO:

```text
quarantine      Arquivos recém-enviados
originals       Originais validados
derived         Miniaturas e imagens otimizadas
approved-assets Arquivos liberados para o site
rejected        Arquivos rejeitados
```

Os originais serão privados. O site público usará somente arquivos aprovados.

## 7. Recepção e validação

Depois que o usuário finalizar uma submissão, a API deverá colocá-la na fila. O `worker-ingest` fará:

1. verificação do formato real;
2. limite de tamanho e quantidade;
3. verificação antivírus;
4. extração segura de ZIP;
5. bloqueio de ZIP criptografado ou excessivo;
6. cálculo de SHA-256;
7. criação de miniatura e versão web;
8. extração de metadados EXIF;
9. envio da tarefa ao agente de acervo.

Arquivos idênticos usarão o mesmo objeto armazenado, mas cada submissão e relato permanecerá independente. Imagens apenas semelhantes serão marcadas para revisão, sem exclusão automática.

## 8. Agentes

### 8.1 Agente de acervo

Executado quando uma submissão for validada. Usará a API de imagem e a API LLM para:

- descrever a fotografia;
- extrair texto visível;
- sugerir data, local, temas e eventos;
- comparar a imagem com o relato enviado;
- relacionar a fotografia aos textos históricos;
- identificar dúvidas ou contradições;
- produzir um registro JSON estruturado.

Inferências da IA devem ser identificadas como inferências e possuir nível de confiança.

### 8.2 Agente interativo

Será acessível pelo painel e pelo terminal:

```bash
acervo chat
```

Funções:

- conversar com o administrador;
- consultar o acervo;
- registrar requisitos para o site;
- solicitar correções;
- criar tarefas para o agente do site;
- informar o estado das submissões e revisões.

As decisões devem ser gravadas no banco como requisitos persistentes. A memória da conversa não poderá ser a única fonte dos requisitos.

### 8.3 Agente do site

Receberá o modelo visual, os textos históricos, os requisitos e os materiais aprovados. Poderá:

- criar ou modificar páginas e componentes;
- organizar linha do tempo e galerias;
- inserir materiais aprovados;
- executar build e testes;
- criar uma revisão para aprovação.

O agente trabalhará em branch ou worktree isolada e não terá permissão para publicar.

## 9. APIs de IA

Devem existir dois adaptadores independentes:

```text
LLMProvider
ImageProvider
```

URLs, chaves, modelo e parâmetros serão fornecidos por variáveis de ambiente ou Docker Secrets. Nenhuma chave poderá ser gravada no repositório.

As respostas da API de imagem deverão ser convertidas para um esquema JSON interno. A API LLM será usada na conversa, interpretação histórica e construção do site.

## 10. Revisão e publicação

O agente do site criará uma revisão identificada, por exemplo `REV-000127`. O painel protegido mostrará:

- descrição da mudança;
- páginas e arquivos alterados;
- fotografias incluídas;
- alertas da IA;
- prévia completa;
- ações para aprovar, rejeitar ou solicitar alteração.

A publicação será feita pelo serviço `publisher`, não pelo agente. Ele deverá publicar somente se:

- a revisão foi aprovada por usuário autenticado;
- o código não mudou depois da aprovação;
- o build terminou com sucesso;
- os testes básicos passaram.

Cada build será armazenado como uma versão imutável. A publicação trocará atomicamente a versão ativa e deverá permitir rollback.

## 11. Estados principais

```text
RECEIVED
QUARANTINED
VALIDATED
ANALYZED
DRAFT
AWAITING_REVIEW
APPROVED
PUBLISHED
REJECTED
ERROR
```

Falhas de API deverão permitir nova tentativa sem criar submissões ou arquivos duplicados.

## 12. Segurança mínima

- HTTPS em todos os endereços.
- Painel protegido por senha com hash.
- MinIO, Redis e PostgreSQL sem portas públicas.
- Uploads sempre em quarentena.
- Validação de CAPTCHA no servidor.
- Rate limit e limites de upload.
- Cookies seguros e proteção CSRF no painel.
- Logs de aprovação, rejeição e publicação.
- Credenciais fora do Git.
- Backup dos volumes do MinIO e PostgreSQL.

## 13. Estrutura sugerida do repositório

```text
30anos-inf/
├── compose.yaml
├── .env.example
├── infra/
│   └── caddy/
├── apps/
│   ├── api/
│   ├── agents/
│   ├── cli/
│   └── site/
├── content/
│   ├── historia/
│   └── requisitos/
├── migrations/
├── scripts/
├── tests/
└── README.md
```

## 14. Escopo inicial

Para manter o projeto simples e adequado a um site temporário, a primeira versão deverá ter apenas:

1. formulário público;
2. upload para MinIO;
3. validação e deduplicação exata;
4. análise por API de imagem e LLM;
5. conversa pelo terminal;
6. agente modificador do site;
7. prévia protegida;
8. aprovação e publicação;
9. rollback para a versão anterior.

Não fazem parte da primeira versão: aplicativo móvel, login dos colaboradores, reconhecimento facial automático, busca vetorial avançada, múltiplos níveis editoriais ou infraestrutura distribuída.

## 15. Critérios de aceite

O MVP será considerado concluído quando:

- uma pessoa não autenticada conseguir enviar uma imagem e um relato;
- o arquivo passar por quarentena e validação;
- uma duplicata exata não gerar outra cópia física;
- a imagem for analisada pelas APIs fornecidas;
- o administrador conseguir conversar com o agente por SSH;
- o agente conseguir gerar uma alteração no site;
- a alteração aparecer somente no endereço de revisão;
- o site público permanecer inalterado até a aprovação;
- a aprovação publicar exatamente a revisão visualizada;
- for possível retornar à versão publicada anteriormente.

