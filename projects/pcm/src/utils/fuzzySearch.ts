import { BaseMedicationGroup, MedicationOption } from './medicationCatalog';

/**
 * Normaliza strings para busca insensível a acentos, maiúsculas e caracteres especiais.
 */
export const normalizeText = (text: string): string => {
  if (!text) return '';
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s\+\-\/\.]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
};

/**
 * Calcula distância de Damerau-Levenshtein entre duas strings (suporta inserções, deleções, substituições e transposições).
 */
export const damerauLevenshteinDistance = (source: string, target: string): number => {
  const s = source.toLowerCase();
  const t = target.toLowerCase();
  const sLen = s.length;
  const tLen = t.length;

  if (sLen === 0) return tLen;
  if (tLen === 0) return sLen;

  const d: number[][] = Array.from({ length: sLen + 1 }, () => Array(tLen + 1).fill(0));

  for (let i = 0; i <= sLen; i++) d[i][0] = i;
  for (let j = 0; j <= tLen; j++) d[0][j] = j;

  for (let i = 1; i <= sLen; i++) {
    for (let j = 1; j <= tLen; j++) {
      const cost = s[i - 1] === t[j - 1] ? 0 : 1;
      d[i][j] = Math.min(
        d[i - 1][j] + 1, // deleção
        d[i][j - 1] + 1, // inserção
        d[i - 1][j - 1] + cost // substituição
      );

      // Transposição (troca de letras adjacentes, ex: 'dipr' vs 'dpir')
      if (i > 1 && j > 1 && s[i - 1] === t[j - 2] && s[i - 2] === t[j - 1]) {
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
      }
    }
  }

  return d[sLen][tLen];
};

/**
 * Calcula o índice de similaridade (0 a 1) entre duas strings.
 */
export const calculateStringSimilarity = (strA: string, strB: string): number => {
  const normA = normalizeText(strA);
  const normB = normalizeText(strB);
  if (!normA || !normB) return 0;
  if (normA === normB) return 1;

  const maxLen = Math.max(normA.length, normB.length);
  if (maxLen === 0) return 1;

  const distance = damerauLevenshteinDistance(normA, normB);
  return Math.max(0, 1 - distance / maxLen);
};

/**
 * Verifica se os caracteres da query aparecem em subsequência ordenada dentro do target.
 */
export const fuzzySubsequenceScore = (target: string, query: string): number => {
  const t = normalizeText(target);
  const q = normalizeText(query);
  if (!t || !q) return 0;
  if (t === q) return 100;
  if (t.startsWith(q)) return 90 + Math.min(10, (q.length / t.length) * 10);
  if (t.includes(q)) return 80 + Math.min(10, (q.length / t.length) * 10);

  let tIdx = 0;
  let qIdx = 0;
  let matches = 0;
  let consecutive = 0;
  let maxConsecutive = 0;
  let wordBoundaryBonus = 0;

  while (tIdx < t.length && qIdx < q.length) {
    if (t[tIdx] === q[qIdx]) {
      matches++;
      consecutive++;
      if (consecutive > maxConsecutive) maxConsecutive = consecutive;
      // Bônus se a letra casar no início de uma palavra
      if (tIdx === 0 || t[tIdx - 1] === ' ' || t[tIdx - 1] === '-' || t[tIdx - 1] === '+') {
        wordBoundaryBonus += 5;
      }
      qIdx++;
    } else {
      consecutive = 0;
    }
    tIdx++;
  }

  // Se todos os caracteres da query foram encontrados na ordem
  if (qIdx === q.length) {
    const coverage = q.length / t.length;
    const baseScore = 55 + (coverage * 20) + (maxConsecutive * 3) + Math.min(15, wordBoundaryBonus);
    return Math.min(85, baseScore);
  }

  return 0;
};

/**
 * Mapeamento clínico avançado de classes terapêuticas, sinônimos médicos, indicações e sintomas comuns.
 */
export interface TherapeuticCategoryMap {
  canonicalCategory: string;
  keywords: string[];
  displayName: string;
  badgeColor?: string;
}

export const THERAPEUTIC_CLASSES: TherapeuticCategoryMap[] = [
  {
    canonicalCategory: 'Analgésico / Antitérmico',
    displayName: 'Analgésicos & Antitérmicos',
    keywords: [
      'analgesico', 'antitermico', 'antalgico', 'analgesia', 'antipiretico',
      'dor', 'febre', 'cefaleia', 'enxaqueca', 'dor de cabeca', 'dor muscular',
      'dipirona', 'paracetamol', 'novalgina', 'tylenol', 'tramadol', 'codeina'
    ]
  },
  {
    canonicalCategory: 'Anti-inflamatório',
    displayName: 'Anti-inflamatórios (AINEs)',
    keywords: [
      'antiinflamatorio', 'anti-inflamatorio', 'aine', 'inflamacao', 'edema',
      'dor de garganta', 'garganta inflamada', 'artrite', 'artrose', 'tendinite',
      'entorse', 'trauma', 'dor articular', 'ibuprofeno', 'cetoprofeno', 'advil',
      'alivium', 'profenid', 'nimesulida', 'diclofenaco'
    ]
  },
  {
    canonicalCategory: 'Antibiótico / Antimicrobiano',
    displayName: 'Antibióticos & Antimicrobianos',
    keywords: [
      'antibiotico', 'antimicrobiano', 'antibacteriano', 'atb', 'infeccao',
      'infeccao bacteriana', 'bacteria', 'penicilina', 'cefalosporina', 'macrolideo',
      'quinolona', 'amoxicilina', 'clavulanato', 'clavulin', 'azitromicina', 'astro',
      'cefalexina', 'keflex', 'cefuroxima', 'zinnat', 'ceftriaxona', 'rocefin',
      'ciprofloxacino', 'cipro', 'levofloxacino', 'bactrim', 'sulfametoxazol',
      'nitrofurantoina', 'macrodantina', 'sinusite', 'amigdalite', 'faringite',
      'pneumonia', 'otite', 'itu', 'infeccao urinaria', 'cistite', 'erisipela'
    ]
  },
  {
    canonicalCategory: 'Corticoide',
    displayName: 'Corticoides & Esteroides',
    keywords: [
      'corticoide', 'corticoesteroide', 'esteroide', 'anti-inflamatorio esteroidal',
      'prednisolona', 'prelone', 'prednisona', 'meticorten', 'dexametasona', 'decadron',
      'budesonida', 'pulmicort', 'fluticasona', 'avamys', 'flixotide', 'beclometasona',
      'clenil', 'laringite', 'croup', 'estridor', 'crise de asma', 'edema de glote'
    ]
  },
  {
    canonicalCategory: 'Antialérgico / Anti-histamínico',
    displayName: 'Antialérgicos & Anti-histamínicos',
    keywords: [
      'antialergico', 'anti-histaminico', 'antihistaminico', 'alergia', 'rinite',
      'urticaria', 'prurido', 'coceira', 'coriza', 'espirros', 'picada de inseto',
      'loratadina', 'claritin', 'desloratadina', 'desalex', 'cetirizina', 'zyrtec',
      'hidroxizina', 'hixizine', 'dexclorfeniramina', 'polaramine'
    ]
  },
  {
    canonicalCategory: 'Broncodilatador / Respiratório',
    displayName: 'Broncodilatadores & Respiratório',
    keywords: [
      'broncodilatador', 'respiratorio', 'pulmonar', 'asma', 'bronquite', 'chiado',
      'dispneia', 'falta de ar', 'nebulizacao', 'inalacao', 'bombinha', 'tosse',
      'salbutamol', 'aerolin', 'atrovent', 'ipratropio', 'berotec', 'fenoterol'
    ]
  },
  {
    canonicalCategory: 'Cardiovascular / Anti-hipertensivo',
    displayName: 'Anti-hipertensivos & Cardiovasculares',
    keywords: [
      'antihipertensivo', 'anti-hipertensivo', 'pressao', 'pressao alta', 'hipertensao',
      'cardiovascular', 'coracao', 'cardiologia', 'betabloqueador', 'ieca', 'bra',
      'diuretico', 'losartana', 'atenolol', 'propranolol', 'metoprolol', 'selozok',
      'carvedilol', 'anlodipino', 'norvasc', 'enalapril', 'renitec', 'captopril',
      'hidroclorotiazida', 'furosemida', 'lasix', 'espironolactona', 'aldactone'
    ]
  },
  {
    canonicalCategory: 'Gastrointestinal',
    displayName: 'Gastrointestinais & Antiácidos',
    keywords: [
      'gastro', 'gastrointestinal', 'gastroprotetor', 'protetor gastrico', 'estomago',
      'gastrite', 'refluxo', 'azia', 'pirose', 'ibp', 'antiacido', 'ulcera',
      'omeprazol', 'pantoprazol', 'esomeprazol', 'antiemetico', 'enjoo', 'vomito',
      'nausea', 'ondansetrona', 'vonau', 'domperidona', 'motilium', 'metoclopramida',
      'plasil', 'simeticona', 'luftal', 'gases', 'colica intestinal'
    ]
  },
  {
    canonicalCategory: 'Laxativo',
    displayName: 'Laxativos & Constipação',
    keywords: [
      'laxativo', 'constipacao', 'prisao de ventre', 'intestino preso', 'evacuacao',
      'lactulose', 'polietilenoglicol', 'peg 4000', 'muvinlax', 'tamarine'
    ]
  },
  {
    canonicalCategory: 'Antiparasitário',
    displayName: 'Antiparasitários & Vermífugos',
    keywords: [
      'antiparasitario', 'vermifugo', 'verme', 'parasita', 'parasitose', 'lombriga',
      'ameba', 'giardia', 'oxiuro', 'escabiose', 'sarna', 'piolho', 'pediculose',
      'albendazol', 'zentel', 'mebendazol', 'pantelmin', 'ivermectina', 'revectina',
      'nitazoxanida', 'annita'
    ]
  },
  {
    canonicalCategory: 'Antifúngico',
    displayName: 'Antifúngicos & Antimicóticos',
    keywords: [
      'antifungico', 'antimicotico', 'fungo', 'micose', 'candidiase', 'sapinho',
      'frieira', 'pano branco', 'fluconazol', 'zolt', 'nistatina'
    ]
  },
  {
    canonicalCategory: 'Saúde Mental / Psicotrópico',
    displayName: 'Psicotrópicos & Saúde Mental',
    keywords: [
      'psicotropico', 'saude mental', 'ansiolitico', 'calmante', 'sedativo',
      'tarja preta', 'benzodiazepinico', 'sono', 'insonia', 'ansiedade', 'tag',
      'antidepressivo', 'depressao', 'panico', 'isrs', 'humor', 'clonazepam',
      'rivotril', 'diazepam', 'valium', 'alprazolam', 'frontan', 'zolpidem',
      'stilnox', 'fluoxetina', 'prozac', 'sertralina', 'zoloft', 'escitalopram',
      'lexapro', 'venlafaxina', 'duloxetina', 'pregabalina', 'lyrica', 'gabapentina'
    ]
  },
  {
    canonicalCategory: 'Hipolipemiante',
    displayName: 'Hipolipemiantes (Estatinas)',
    keywords: [
      'hipolipemiante', 'estatina', 'colesterol', 'triglicerideos', 'dislipidemia',
      'gordura no sangue', 'atorvastatina', 'lipitor', 'rosuvastatina', 'crestor',
      'sinvastatina'
    ]
  },
  {
    canonicalCategory: 'Antidiabético',
    displayName: 'Antidiabéticos & Insulinas',
    keywords: [
      'antidiabetico', 'diabetes', 'glicemia', 'acucar no sangue', 'insulina',
      'hipoglicemiante', 'dm2', 'metformina', 'glifage', 'gliclazida', 'diamicron',
      'insulina nph', 'insulina regular'
    ]
  },
  {
    canonicalCategory: 'Tireoide',
    displayName: 'Hormônios Tireoidianos',
    keywords: [
      'tireoide', 'hipotireoidismo', 'tsh', 'levotiroxina', 'puran', 'euthyrox'
    ]
  },
  {
    canonicalCategory: 'Hidratação & Soluções',
    displayName: 'Hidratação & Soluções Nasais',
    keywords: [
      'hidratacao', 'reidratacao', 'sro', 'soro', 'desidratacao', 'diarreia',
      'vomito desidratacao', 'pedialyte', 'soro fisiologico', 'solucao nasal',
      'lavagem nasal', 'obstrucao nasal', 'congestao', 'rinosoro', 'maresis', 'sf 0.9'
    ]
  }
];

export interface FuzzySearchResult {
  group: BaseMedicationGroup;
  score: number;
  matchField: 'baseName' | 'activeIngredient' | 'category' | 'therapeuticClass' | 'tradeName' | 'option' | 'synonym';
  matchedTerm: string;
  matchedHighlight: string;
  matchedCategoryBadge?: string;
}

/**
 * Avalia o matching de um grupo de medicamentos contra uma query do usuário.
 */
export const scoreMedicationGroup = (
  group: BaseMedicationGroup,
  rawQuery: string
): FuzzySearchResult | null => {
  const query = normalizeText(rawQuery);
  if (!query) {
    return {
      group,
      score: 100,
      matchField: 'baseName',
      matchedTerm: group.baseName,
      matchedHighlight: group.baseName
    };
  }

  const queryTokens = query.split(/\s+/).filter(t => t.length > 0);

  let bestScore = 0;
  let bestField: FuzzySearchResult['matchField'] = 'baseName';
  let bestTerm = group.baseName;
  let bestHighlight = group.baseName;
  let bestCategoryBadge: string | undefined = undefined;

  const normBaseName = normalizeText(group.baseName);
  const normActive = normalizeText(group.activeIngredient);
  const normCategory = normalizeText(group.category);
  const normTradeNames = group.tradeNames.map(t => ({ original: t, norm: normalizeText(t) }));

  // 1. MATCH EXATO OU PREFIXO NO NOME PRINCIPAL DO MEDICAMENTO
  if (normBaseName === query) {
    return {
      group,
      score: 110,
      matchField: 'baseName',
      matchedTerm: group.baseName,
      matchedHighlight: `Nome exato: ${group.baseName}`
    };
  }

  if (normBaseName.startsWith(query)) {
    const score = 95 + Math.min(10, (query.length / normBaseName.length) * 10);
    if (score > bestScore) {
      bestScore = score;
      bestField = 'baseName';
      bestTerm = group.baseName;
      bestHighlight = `Início do nome: ${group.baseName}`;
    }
  }

  // 2. MATCH NOS NOMES COMERCIAIS (Ex: Novalgina, Tylenol, Aerolin, Clavulin)
  for (const t of normTradeNames) {
    if (t.norm === query) {
      const score = 105;
      if (score > bestScore) {
        bestScore = score;
        bestField = 'tradeName';
        bestTerm = t.original;
        bestHighlight = `Marca comercial: ${t.original}`;
      }
    } else if (t.norm.startsWith(query)) {
      const score = 92 + Math.min(8, (query.length / t.norm.length) * 8);
      if (score > bestScore) {
        bestScore = score;
        bestField = 'tradeName';
        bestTerm = t.original;
        bestHighlight = `Marca comercial: ${t.original}`;
      }
    } else if (t.norm.includes(query)) {
      const score = 80 + Math.min(8, (query.length / t.norm.length) * 8);
      if (score > bestScore) {
        bestScore = score;
        bestField = 'tradeName';
        bestTerm = t.original;
        bestHighlight = `Marca comercial: ${t.original}`;
      }
    }
  }

  // 3. MATCH NO PRINCÍPIO ATIVO (Ex: Dipirona monoidratada)
  if (normActive.startsWith(query)) {
    const score = 90 + Math.min(10, (query.length / normActive.length) * 10);
    if (score > bestScore) {
      bestScore = score;
      bestField = 'activeIngredient';
      bestTerm = group.activeIngredient;
      bestHighlight = `Princípio ativo: ${group.activeIngredient}`;
    }
  } else if (normActive.includes(query)) {
    const score = 82 + Math.min(8, (query.length / normActive.length) * 8);
    if (score > bestScore) {
      bestScore = score;
      bestField = 'activeIngredient';
      bestTerm = group.activeIngredient;
      bestHighlight = `Princípio ativo: ${group.activeIngredient}`;
    }
  }

  // 4. MATCH NA CATEGORIA DIRETA OU CLASSE TERAPÊUTICA
  if (normCategory.startsWith(query)) {
    const score = 88;
    if (score > bestScore) {
      bestScore = score;
      bestField = 'category';
      bestTerm = group.category;
      bestHighlight = `Classe: ${group.category}`;
      bestCategoryBadge = group.category;
    }
  } else if (normCategory.includes(query)) {
    const score = 78;
    if (score > bestScore) {
      bestScore = score;
      bestField = 'category';
      bestTerm = group.category;
      bestHighlight = `Classe: ${group.category}`;
      bestCategoryBadge = group.category;
    }
  }

  // 5. MATCH DE CLASSE TERAPÊUTICA AMPLIADA & SINÔNIMOS CLÍNICOS
  // (Ex: Usuário digita "antibiotico", "febre", "dor", "pressao", "asma", "corticoide", "gastro")
  for (const tc of THERAPEUTIC_CLASSES) {
    const categoryMatches = normCategory.includes(normalizeText(tc.canonicalCategory)) ||
      normalizeText(tc.displayName).includes(normCategory) ||
      tc.keywords.some(kw => normBaseName.includes(kw) || normActive.includes(kw));

    if (categoryMatches) {
      // Verifica se a query do usuário bate com alguma keyword da classe
      for (const kw of tc.keywords) {
        if (kw === query) {
          const score = 85;
          if (score > bestScore) {
            bestScore = score;
            bestField = 'therapeuticClass';
            bestTerm = tc.displayName;
            bestHighlight = `Classe Terapêutica: ${tc.displayName}`;
            bestCategoryBadge = tc.displayName;
          }
        } else if (kw.startsWith(query) && query.length >= 3) {
          const score = 76;
          if (score > bestScore) {
            bestScore = score;
            bestField = 'therapeuticClass';
            bestTerm = tc.displayName;
            bestHighlight = `Classe Terapêutica: ${tc.displayName}`;
            bestCategoryBadge = tc.displayName;
          }
        } else if (query.includes(kw) && kw.length >= 3) {
          const score = 74;
          if (score > bestScore) {
            bestScore = score;
            bestField = 'therapeuticClass';
            bestTerm = tc.displayName;
            bestHighlight = `Classe Terapêutica: ${tc.displayName}`;
            bestCategoryBadge = tc.displayName;
          }
        }
      }
    }
  }

  // 6. MULTI-TOKEN QUERY (Ex: "amox clav", "dip 500", "para gotas", "dipirona adulto", "losartana 50")
  if (queryTokens.length > 1) {
    let tokensMatched = 0;
    let tokenScoreSum = 0;

    for (const token of queryTokens) {
      let tokenMatched = false;
      let maxTokenScore = 0;

      // Testa no nome base
      if (normBaseName.includes(token)) {
        tokenMatched = true;
        maxTokenScore = Math.max(maxTokenScore, 85);
      }
      // Testa no princípio ativo
      if (normActive.includes(token)) {
        tokenMatched = true;
        maxTokenScore = Math.max(maxTokenScore, 80);
      }
      // Testa nas marcas
      if (normTradeNames.some(t => t.norm.includes(token))) {
        tokenMatched = true;
        maxTokenScore = Math.max(maxTokenScore, 80);
      }
      // Testa na classe
      if (normCategory.includes(token)) {
        tokenMatched = true;
        maxTokenScore = Math.max(maxTokenScore, 75);
      }
      // Testa nas opções individuais (ex: "gotas", "500 mg", "suspensao", "oral")
      for (const opt of group.options) {
        const normOpt = normalizeText(`${opt.name} ${opt.presentation} ${opt.pharmaceuticalForm} ${opt.concentration}`);
        if (normOpt.includes(token)) {
          tokenMatched = true;
          maxTokenScore = Math.max(maxTokenScore, 70);
          break;
        }
      }

      if (tokenMatched) {
        tokensMatched++;
        tokenScoreSum += maxTokenScore;
      }
    }

    if (tokensMatched === queryTokens.length) {
      const combinedScore = 88 + (tokenScoreSum / queryTokens.length) * 0.15;
      if (combinedScore > bestScore) {
        bestScore = combinedScore;
        bestField = 'baseName';
        bestTerm = group.baseName;
        bestHighlight = `Correspondência múltipla: ${group.baseName}`;
      }
    }
  }

  // 7. FUZZY SUBSEQUENCE MATCHING (Subsequência de caracteres, tolerando pequenas abreviações)
  const subScore = fuzzySubsequenceScore(group.baseName, query);
  if (subScore > bestScore) {
    bestScore = subScore;
    bestField = 'baseName';
    bestTerm = group.baseName;
    bestHighlight = `Busca parcial: ${group.baseName}`;
  }

  // 8. FUZZY DISTANCE / TYPO TOLERANCE (Tolerância a erros de digitação, ex: "diprona" -> "dipirona", "amoxilina" -> "amoxicilina")
  if (query.length >= 3) {
    // Compara com cada palavra do nome base
    const baseWords = normBaseName.split(/\s+/);
    for (const w of baseWords) {
      if (w.length >= 3) {
        const sim = calculateStringSimilarity(w, query);
        if (sim >= 0.72) {
          const score = Math.floor(sim * 82);
          if (score > bestScore) {
            bestScore = score;
            bestField = 'baseName';
            bestTerm = group.baseName;
            bestHighlight = `Similaridade (${Math.round(sim * 100)}%): ${group.baseName}`;
          }
        }
      }
    }

    // Compara com marcas
    for (const t of normTradeNames) {
      const sim = calculateStringSimilarity(t.norm, query);
      if (sim >= 0.72) {
        const score = Math.floor(sim * 80);
        if (score > bestScore) {
          bestScore = score;
          bestField = 'tradeName';
          bestTerm = t.original;
          bestHighlight = `Marca similar (${Math.round(sim * 100)}%): ${t.original}`;
        }
      }
    }
  }

  // 9. MATCH NAS APRESENTAÇÕES / OPÇÕES INDIVIDUAIS
  for (const opt of group.options) {
    const optText = normalizeText(`${opt.name} ${opt.presentation} ${opt.pharmaceuticalForm} ${opt.concentration}`);
    if (optText.includes(query)) {
      const score = 72;
      if (score > bestScore) {
        bestScore = score;
        bestField = 'option';
        bestTerm = opt.presentation;
        bestHighlight = `Apresentação: ${opt.presentation}`;
      }
    }
  }

  if (bestScore >= 45) {
    return {
      group,
      score: bestScore,
      matchField: bestField,
      matchedTerm: bestTerm,
      matchedHighlight: bestHighlight,
      matchedCategoryBadge: bestCategoryBadge
    };
  }

  return null;
};

/**
 * Busca fuzzy com classificação e ordenação de relevância.
 */
export const searchMedicationsFuzzy = (
  groups: BaseMedicationGroup[],
  query: string,
  filter: 'todos' | 'pediatric' | 'adult' | 'special' = 'todos',
  categoryFilter: string = 'todos'
): FuzzySearchResult[] => {
  const normQuery = normalizeText(query);
  const normCatFilter = normalizeText(categoryFilter);

  const scoredResults: FuzzySearchResult[] = [];

  for (const group of groups) {
    // Filtro por tipo de paciente
    if (filter === 'pediatric' && !group.hasPediatric) continue;
    if (filter === 'adult' && !group.hasAdult) continue;
    if (filter === 'special' && !group.isSpecialControl) continue;

    // Filtro por categoria terapêutica selecionada explicitamente
    if (normCatFilter !== 'todos' && normCatFilter !== '') {
      const normGroupCategory = normalizeText(group.category);
      if (!normGroupCategory.includes(normCatFilter)) {
        // Verifica se a classe selecionada casa com as keywords
        const catMap = THERAPEUTIC_CLASSES.find(tc => normalizeText(tc.displayName) === normCatFilter || normalizeText(tc.canonicalCategory) === normCatFilter);
        const matchesKeywords = catMap?.keywords.some(kw => normalizeText(group.baseName).includes(kw) || normalizeText(group.activeIngredient).includes(kw));
        if (!matchesKeywords) continue;
      }
    }

    const scored = scoreMedicationGroup(group, normQuery);
    if (scored) {
      scoredResults.push(scored);
    }
  }

  // Ordena por maior pontuação (relevância); se pontuação empatar, ordena alfabeticamente
  scoredResults.sort((a, b) => {
    if (b.score !== a.score) {
      return b.score - a.score;
    }
    return a.group.baseName.localeCompare(b.group.baseName, 'pt-BR');
  });

  return scoredResults;
};
