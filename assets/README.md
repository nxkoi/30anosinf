# Assets oficiais — 30 anos INF/UFG

Coleta realizada em `2026-09-15T03:33:57Z` a partir de páginas e arquivos nos domínios `inf.ufg.br`, `files.cercomp.ufg.br` e outros `*.ufg.br`.

## Aviso importante

- A página oficial [Manual da Marca de 30 anos do INF](https://inf.ufg.br/p/manual-da-marca-de-trinta-anos-inf) informa que o **manual completo da marca comemorativa ainda está em construção**.
- **Não recolorir** os arquivos oficiais da marca. Usar somente as versões publicadas (branco, P&B, outline).
- Arquivos em `references/` e `references/screenshots/` são **apenas referência de design** e não devem ir para a versão pública do site sem curadoria.
- Originais oficiais da marca de 30 anos estão preservados sem alteração em `brand/30anos/original/` (hardlinks quando o sistema de arquivos permite).

## Quando usar cada versão

- **Horizontal branca**: cabeçalho sobre fundo escuro.
- **Horizontal P&B**: páginas claras e documentos.
- **Vertical**: peças estreitas ou cards; não como marca principal no desktop.
- **Selo branco / P&B**: destaque comemorativo conforme contraste do fundo.
- **Selo outline**: elemento decorativo discreto.
- **JPG**: apenas prévia oficial; preferir PNG (transparência) ou PDF (vetorial) no site/impressão.
- **Marcas INF/UFG**: rodapé institucional e continuidade com o portal.

### Marca 30 anos (página oficial de downloads)

| Versão | PNG | PDF | JPG |
|---|---|---|---|
| Horizontal branca | sim | sim | — |
| Horizontal P&B | sim | sim | sim (prévia) |
| Vertical branca | sim | sim | — |
| Vertical P&B | sim | sim | sim (prévia) |
| Selo branco | sim | sim | — |
| Selo P&B | sim | sim | sim (prévia) |
| Selo outline | sim | sim | sim (prévia) |


## Referências (não obrigatórias no site)

Arquivos de conceito, rascunhos, mockups de papelaria e capturas de tela do portal. Ver manifesto (`assets/manifests/assets.json`) com `kind` = `reference` ou `screenshot`.

## Downloads que falharam

Nenhum arquivo ficou indisponível após retentativa. Quatro arquivos de `ww2.inf.ufg.br` (marca INF) exigiram TLS com cadeia/DH fracos; conteúdo validado por magic bytes e registrado no manifesto com nota técnica.

## Itens ainda pendentes / dependem do manual definitivo

- Manual completo da marca comemorativa de 30 anos (status oficial: em construção).
- Paleta cromática oficial definitiva dos 30 anos (hoje só há aproximações a partir das peças).
- Extração editorial completa da timeline embutida em [História do INF](https://inf.ufg.br/p/30147-historia-do-inf) (fonte do embed fora de `ufg.br`).
- Eventual publicação de novas variantes da marca após a conclusão do manual.

## Fontes históricas coletadas

Arquivos em `content/sources/`:

- `content/sources/celebra-30-anos.md`
- `content/sources/concurso-selo-30-anos.md`
- `content/sources/historia-do-inf.md`
- `content/sources/manual-marca-30-anos.md`
- `content/sources/marcos-historicos-resumo-projeto.md`

## Manifesto e relatório

- Manifesto: `assets/manifests/assets.json`
- Relatório desta coleta: `assets/manifests/collection-report.md`

## Estrutura

```text
assets/
├── brand/
│   ├── 30anos/
│   │   ├── horizontal/
│   │   ├── vertical/
│   │   ├── selo/
│   │   └── original/
│   ├── inf/
│   └── ufg/
├── references/
│   ├── concept/
│   ├── mockups/
│   ├── screenshots/
│   └── original/
└── manifests/
```

Total de entradas no manifesto: **45** (incluindo falhas e aliases de conteúdo duplicado).
Arquivos baixados com sucesso (status `downloaded`): **45**.
