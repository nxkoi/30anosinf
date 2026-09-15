# Template visual — 30 anos do INF/UFG

## 1. Decisão de identidade

O arquivo recebido é uma versão oficial da marca comemorativa, não a única versão disponível. O INF publicou versões:

- horizontal: branca e preto e branco;
- vertical: branca e preto e branco;
- selo: branco, preto e branco e contorno.

Para o site, usar preferencialmente:

- **horizontal branca** no cabeçalho sobre fundo escuro;
- **horizontal P&B** em páginas claras e documentos;
- **selo outline** apenas como elemento decorativo discreto;
- **vertical** em peças estreitas ou cards, nunca como marca principal no desktop.

Não recolorir os arquivos da marca. Usar somente as versões oficiais fornecidas pelo INF.

## 2. Conceito visual

O selo representa um caminho ascendente que forma o número 30, ligando passado, presente e futuro. As peças oficiais mostram também um padrão gráfico de setas/fragmentos, com azul-marinho, violeta e verde-água.

O site deve parecer uma **exposição digital comemorativa**, e não uma cópia do portal administrativo do INF. Deve, porém, manter continuidade institucional por meio de:

- marca INF/UFG no rodapé;
- linguagem clara e institucional;
- tipografia sem serifa;
- alto contraste e acessibilidade;
- azul como cor estrutural;
- links para o portal oficial.

## 3. Paleta inicial

O manual completo dos 30 anos ainda aparece como “em construção”. Portanto, estes valores são aproximações das peças oficiais e devem ficar centralizados em variáveis CSS para ajuste posterior.

```css
:root {
  --inf-navy: #10234b;
  --inf-violet: #6337e6;
  --inf-mint: #50dfc5;
  --inf-blue: #2196e3;
  --inf-ink: #171820;
  --inf-paper: #f6f6f4;
  --inf-white: #ffffff;
  --inf-muted: #68707d;
  --inf-border: #d9dde4;
}
```

Uso recomendado:

| Elemento | Cor |
|---|---|
| Cabeçalho e rodapé | `--inf-navy` |
| Botão principal e destaques | `--inf-violet` |
| Datas, linhas e detalhes gráficos | `--inf-mint` |
| Links institucionais | `--inf-blue` |
| Fundo principal | `--inf-paper` |
| Texto | `--inf-ink` |

Evitar gradientes genéricos, excesso de brilho e fundos permanentemente escuros. Fotografias históricas devem ser o foco.

## 4. Tipografia

Usar **Lato**, já presente no portal do INF, com fallback de sistema:

```css
font-family: "Lato", "Segoe UI", Arial, sans-serif;
```

- títulos: Lato 700 ou 800;
- corpo: Lato 400;
- datas e legendas: Lato 600;
- texto base: 18 px no desktop e 16 px no celular;
- largura máxima de leitura: 70 caracteres.

## 5. Estrutura do site

### Cabeçalho

- fundo azul-marinho;
- marca horizontal branca à esquerda;
- navegação curta à direita;
- botão destacado “Envie sua história”.

Menu:

1. Início
2. Nossa história
3. Linha do tempo
4. Acervo
5. Eventos
6. Contribua

No celular, usar menu recolhido e manter o botão “Contribua” visível.

### Página inicial

1. **Hero comemorativo**
   - selo grande;
   - frase: “30 anos construindo o futuro da Computação em Goiás”;
   - fotografia histórica em destaque;
   - ações: “Conheça a história” e “Envie uma foto”.

2. **Marcos essenciais**
   - 1975: criação do Departamento de Estatística e Informática;
   - 1983/1984: criação do curso e ingresso da primeira turma;
   - 1996: criação do Instituto de Informática;
   - 2026: 30 anos do INF como unidade acadêmica.

3. **Histórias em destaque**
   - grade com 3 a 6 fotografias aprovadas;
   - data, título, local e legenda curta;
   - sem texto inventado para preencher espaço.

4. **Linha do tempo resumida**
   - eixo vertical no celular e horizontal apenas quando houver espaço;
   - datas em verde-água;
   - marcos selecionáveis.

5. **Chamada para contribuição**
   - bloco violeta;
   - texto simples convidando estudantes, egressos, técnicos e docentes;
   - botão “Compartilhe sua memória”.

6. **Próximos eventos**
   - mostrar apenas se houver eventos cadastrados;
   - ocultar a seção vazia.

### Página Nossa história

- narrativa em capítulos curtos;
- fotografias intercaladas;
- cada afirmação histórica deve apontar sua fonte editorial;
- relatos pessoais devem ser identificados como depoimentos.

### Linha do tempo

- filtros por década e tema;
- cartões com data, título, imagem e fonte;
- itens sem data exata podem usar “década de...” ou “data aproximada”.

### Acervo

- grade responsiva de fotografias;
- filtros: década, local, tema e tipo de evento;
- busca textual;
- página individual com imagem, descrição, relato original autorizado, autoria, data e nível de precisão;
- descrição automática da IA não deve aparecer como fato histórico sem revisão.

### Contribua

- formulário público com upload;
- explicar o destino das imagens antes do envio;
- solicitar autorização de uso separadamente;
- mostrar confirmação e código da submissão.

## 6. Componentes visuais

- `Header`: marca, navegação e ação principal.
- `Hero30`: selo, mensagem e fotografia.
- `MilestoneCard`: ano, título, resumo e fonte.
- `StoryCard`: fotografia, data, local e título.
- `Timeline`: marcos cronológicos.
- `PhotoGallery`: grade e filtros.
- `Testimonial`: relato identificado e autorizado.
- `ContributionCTA`: chamada para envio.
- `Footer`: marcas INF/UFG, endereço, contato e link para `inf.ufg.br`.

Cards devem ter borda fina, cantos discretos (8–12 px) e sombra mínima. O padrão gráfico de setas pode aparecer como máscara, divisor ou textura com baixa opacidade; não deve competir com as fotografias.

## 7. Regras para imagens

- preservar o original no acervo;
- publicar derivados WebP/AVIF;
- usar proporção 4:3 nas grades e imagem integral na página do item;
- não colorizar fotografias automaticamente;
- indicar quando a imagem foi restaurada, recortada ou tratada;
- sempre exibir legenda e texto alternativo revisados;
- não publicar rostos ou nomes quando a autorização não permitir.

## 8. Acessibilidade e responsividade

- contraste mínimo WCAG AA;
- navegação completa por teclado;
- foco visível;
- `alt` significativo nas fotografias;
- respeitar `prefers-reduced-motion`;
- não depender apenas de cor para indicar década ou estado;
- tamanhos de toque com pelo menos 44 px;
- página utilizável a partir de 360 px de largura.

## 9. Movimento

Usar animações leves apenas para reforçar o conceito de continuidade:

- entrada suave de marcos conforme a rolagem;
- progressão da linha do tempo;
- pequenos deslocamentos do padrão de setas.

Evitar parallax forte, abertura cinematográfica obrigatória e animações que atrasem o acesso ao conteúdo.

## 10. Direção para implementação

O template deve ser orientado por conteúdo e aceitar páginas geradas pelo agente sem quebrar a identidade. Cores, espaçamento e tipografia ficam em tokens globais. Todos os cards usam um mesmo esquema de dados, mas a página inicial pode destacar manualmente itens aprovados.

O agente construtor pode reorganizar conteúdo, mas não deve:

- editar ou redesenhar a marca;
- inventar datas, nomes ou fatos;
- publicar fotografias ainda não aprovadas;
- trocar os tokens oficiais sem criar uma revisão explícita;
- modificar o cabeçalho, rodapé e requisitos de acessibilidade sem aprovação.

## 11. Referências oficiais consultadas

- Portal do INF: https://inf.ufg.br/
- Celebração dos 30 anos e resumo histórico: https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao
- Concurso e conceito do selo: https://inf.ufg.br/n/premiacao-concurso-selo-comemorativo-instituto-de-informatica-ufg-trinta-anos
- Downloads oficiais da marca de 30 anos: https://inf.ufg.br/p/manual-da-marca-de-trinta-anos-inf
- Manual e marcas institucionais: https://inf.ufg.br/p/52142-manual-da-marca

## 12. Critério de aceite do template

O template estará pronto quando houver:

- versões desktop e celular da página inicial;
- uso correto da marca horizontal branca e P&B;
- página de linha do tempo;
- galeria do acervo e página de fotografia;
- formulário de contribuição;
- rodapé institucional;
- contraste e navegação por teclado verificados;
- dados fictícios claramente marcados como demonstração;
- nenhuma publicação automática sem aprovação.
