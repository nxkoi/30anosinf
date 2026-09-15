export const API_BASE = import.meta.env.PUBLIC_API_BASE || '/api';

export type Milestone = {
  id: string;
  year: number;
  title: string;
  summary: string;
  source_url?: string | null;
  source_label?: string | null;
};

export type PublicAsset = {
  id: string;
  public_code: string;
  photo_date_text?: string | null;
  date_precision?: string | null;
  location?: string | null;
  people?: string | null;
  story?: string | null;
  author_name?: string | null;
  relationship?: string | null;
  width?: number | null;
  height?: number | null;
  media_url: string;
  published_at?: string | null;
};

/** Fallback milestones from official commemorative page summary (used if API unreachable at build/runtime client). */
export const FALLBACK_MILESTONES: Milestone[] = [
  {
    id: '1975',
    year: 1975,
    title: 'Criação do DEI',
    summary: 'Criação do Departamento de Estatística e Informática (DEI) no então Instituto de Matemática e Física (IMF).',
    source_url: 'https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao',
    source_label: 'Página comemorativa INF',
  },
  {
    id: '1983',
    year: 1983,
    title: 'Criação do curso',
    summary: 'Criação do Curso de Bacharelado em Ciências da Computação.',
    source_url: 'https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao',
    source_label: 'Página comemorativa INF',
  },
  {
    id: '1984',
    year: 1984,
    title: 'Primeira turma',
    summary: 'Ingresso da primeira turma do curso de Ciências da Computação.',
    source_url: 'https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao',
    source_label: 'Página comemorativa INF',
  },
  {
    id: '1988',
    year: 1988,
    title: 'Reconhecimento do curso',
    summary: 'Reconhecimento do curso pelo Ministério da Educação.',
    source_url: 'https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao',
    source_label: 'Página comemorativa INF',
  },
  {
    id: '1996',
    year: 1996,
    title: 'Criação do INF',
    summary: 'Criação do Instituto de Informática como unidade acadêmica autônoma da UFG.',
    source_url: 'https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao',
    source_label: 'Página comemorativa INF',
  },
  {
    id: '2026',
    year: 2026,
    title: '30 anos do INF',
    summary: 'Celebração dos 30 anos do Instituto de Informática.',
    source_url: 'https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao',
    source_label: 'Página comemorativa INF',
  },
];
