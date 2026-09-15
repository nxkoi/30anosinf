# Relatório de coleta de assets oficiais

- Gerado em: `2026-09-15T03:33:57Z`
- Atualizado em: `2026-09-15T03:36:50Z`
- Manifesto: `assets/manifests/assets.json`
- Validação: `assets/manifests/validation.json` (ok=True)
- README: `assets/README.md`

## Árvore dos diretórios

```text
assets/
├── brand/
│   ├── 30anos/
│   │   ├── horizontal/   (PNG/PDF/JPG oficiais com nomes locais)
│   │   ├── vertical/
│   │   ├── selo/
│   │   └── original/     (arquivos oficiais preservados; hardlink quando possível)
│   ├── inf/
│   │   └── original/
│   └── ufg/
│       └── original/
├── references/
│   ├── concept/
│   ├── mockups/
│   ├── screenshots/
│   └── original/
└── manifests/
    ├── assets.json
    ├── collection-report.md
    └── validation.json
content/
└── sources/
```

Arquivos em disco sob `assets/` + `content/`: **91**.

## Contagens

- Entradas no manifesto: **45**
- Baixados (`downloaded`): **45**
- Duplicatas de conteúdo entre URLs distintas (`duplicate_content`): **0**
- Falhas finais: **0**
- Fontes históricas em `content/sources/`: **5**
- Hashes únicos de binários em `assets/` (excluindo md/json): **45** (paths em `original/` são hardlinks dos mesmos inodes, não cópias extras)

## Versões da marca 30 anos disponíveis

| Versão | PNG | PDF | JPG |
|---|---|---|---|
| Horizontal branca | sim | sim | — |
| Horizontal P&B | sim | sim | sim (prévia) |
| Vertical branca | sim | sim | — |
| Vertical P&B | sim | sim | sim (prévia) |
| Selo branco | sim | sim | — |
| Selo P&B | sim | sim | sim (prévia) |
| Selo outline | sim | sim | sim (prévia) |

Também coletado: `selo30.png` da página comemorativa (banner 1600×571; conteúdo distinto das versões do manual).

## Downloads que falharam

Nenhum na versão final. Observação técnica: os arquivos `INF.pdf` / `INF-0x.png` hospedados em `ww2.inf.ufg.br` exigiram contorno de TLS fraco (cadeia incompleta / `DH_KEY_TOO_SMALL`); o conteúdo foi validado por magic bytes e registrado com nota no manifesto.

## Arquivos potencialmente duplicados

- Nenhuma URL distinta produziu o mesmo SHA-256.
- Paths em `*/original/` compartilham inode (hardlink) com a cópia de trabalho correspondente — intencional, para preservar o nome remoto sem duplicar bytes.

## Fontes históricas coletadas

- `content/sources/celebra-30-anos.md`
- `content/sources/concurso-selo-30-anos.md`
- `content/sources/historia-do-inf.md`
- `content/sources/manual-marca-30-anos.md`
- `content/sources/marcos-historicos-resumo-projeto.md`

## Itens ainda pendentes

- Manual completo da marca comemorativa de 30 anos (página oficial: **em construção**).
- Paleta cromática oficial definitiva dos 30 anos.
- Extração editorial completa da timeline embutida em https://inf.ufg.br/p/30147-historia-do-inf (fonte do embed Knight Lab fora de `ufg.br`).

## Validação automática

Todos os hashes, tamanhos e originais referenciados no manifesto foram validados com sucesso (`validation.json`: ok=true, errors=[]).

## Confirmação de escopo

**Nenhuma página do site foi implementada nesta etapa.** Não foram criados componentes, CSS, Docker Compose de aplicação nem páginas Astro/HTML do site público. Apenas coleta, organização e documentação de assets/textos oficiais.
