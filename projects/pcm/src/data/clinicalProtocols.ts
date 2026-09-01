import { PathologyProtocol } from '../types';

/**
 * Decks de patologias comuns no Brasil com tratamento de 1ª linha.
 * Doses/posologias de referência conforme protocolos do Ministério da Saúde
 * (PCDT e manuais oficiais) e diretrizes das sociedades de especialidade.
 * São REFERÊNCIAS de apoio — a conduta final é sempre do médico assistente.
 *
 * Quando a medicação existe em PEDIATRIC_MEDICATIONS, use `pediatricMedId`
 * com o id EXATO do catálogo para habilitar o cálculo de dose por peso.
 */
export const PATHOLOGY_PROTOCOLS: PathologyProtocol[] = [
  {
    id: 'geca',
    name: 'GECA — Gastroenterocolite Aguda',
    category: 'Gastrointestinal',
    firstLineSummary: 'Hidratação oral com SRO em volume proporcional às perdas + antiemético se vômitos persistentes. Manter alimentação precoce.',
    pediatricRelevant: true,
    clinicalWarning: 'Antibióticos NÃO são rotineiros na GECA viral. Reavaliar se desidratação moderada/grave, sangue nas fezes ou vômitos incoercíveis.',
    reference: 'Protocolos SBP / Ministério da Saúde — Gastroenterite aguda.',
    medications: [
      {
        name: 'Sais de Reidratação Oral (SRO)',
        presentation: 'Envelope para diluição em 1 litro de água potável',
        route: 'Oral',
        quantity: '10 envelopes',
        posology: 'Oferecer livremente após cada evacuação ou vômito (~10 mL/kg por perda), em pequenos goles frequentes',
        frequencyText: 'após cada evacuação ou vômito, em goles frequentes',
        scheduleInterval: 'S.O.S',
        instructions: 'Diluir cada envelope em exatamente 1 litro de água filtrada ou fervida. Oferecer em goles pequenos e frequentes, mantendo enquanto houver perdas. Não adicionar açúcar nem sal.'
      },
      {
        pediatricMedId: 'ondansetrona-solucao',
        name: 'Ondansetrona Solução Oral',
        presentation: '0,8 mg/mL (4 mg/5 mL)',
        route: 'Oral',
        quantity: '1 frasco',
        posology: '0,15 mg/kg/dose de 8/8h se náuseas ou vômitos persistentes (máx 8 mg/dose)',
        frequencyText: 'de 8 em 8 horas se náuseas ou vômitos',
        scheduleInterval: 'S.O.S',
        durationDays: 2
      }
    ]
  },
  {
    id: 'dengue-grupo-a-ambulatorial',
    name: 'Dengue (Grupo A — Ambulatorial)',
    category: 'Infectológica',
    firstLineSummary: 'Hidratação oral guiada por peso (1/3 SRO + 2/3 líquidos caseiros) + sintomáticos APENAS com dipirona ou paracetamol. Retorno diário e orientação de sinais de alarme.',
    pediatricRelevant: true,
    clinicalWarning: 'PROIBIDO AAS e AINEs (ibuprofeno, nimesulida, cetoprofeno, diclofenaco) — risco hemorrágico. Expansão volêmica dos Grupos C e D no deck de urgência abaixo.',
    reference: 'Diretrizes de manejo da dengue — Ministério da Saúde.',
    medications: [
      {
        pediatricMedId: 'dipirona-gotas',
        name: 'Dipirona Gotas',
        presentation: '500 mg/mL (1 gota = 25 mg)',
        route: 'Oral',
        quantity: '1 frasco',
        posology: '20 mg/kg/dose (~1 gota/kg) de 6/6h se dor ou febre (máx 1000 mg/dose)',
        frequencyText: 'de 6 em 6 horas se dor ou febre',
        scheduleInterval: 'S.O.S',
        durationDays: 5
      },
      {
        name: 'Dipirona sódica',
        presentation: '500 mg comprimido',
        route: 'Oral',
        quantity: '20 comprimidos',
        posology: '500 a 1000 mg de 6/6h se dor ou febre (máx 4 g/dia) — adulto',
        frequencyText: 'de 6 em 6 horas se dor ou febre',
        scheduleInterval: 'S.O.S',
        durationDays: 5
      }
    ]
  },
  {
    id: 'pac',
    name: 'PAC — Pneumonia Adquirida na Comunidade',
    category: 'Infectológica',
    firstLineSummary: 'Amoxicilina oral (altas doses na criança, por 7 a 10 dias; 500 mg 8/8h por 7 dias no adulto ambulatorial sem comorbidades). Considerar macrolídeo se suspeita de germe atípico.',
    pediatricRelevant: true,
    clinicalWarning: 'Estratificar gravidade (CRB-65 / PSI / CURB-65): internar se hipotensão, confusão mental, SatO2 < 90% ou comorbidades graves descompensadas.',
    reference: 'Diretrizes Brasileiras de PAC (SBPT) e protocolos do Ministério da Saúde.',
    medications: [
      {
        pediatricMedId: 'amoxicilina-250-altas-doses',
        name: 'Amoxicilina Susp 250 mg/5 mL (Altas Doses)',
        presentation: '50 mg/mL (250 mg/5 mL)',
        route: 'Oral',
        quantity: '2 frascos',
        posology: '90 mg/kg/dia divididos em 3 tomadas de 8/8h por 10 dias (máx 1000 mg/dose) — pediatria',
        frequencyText: 'de 8 em 8 horas por 10 dias',
        scheduleInterval: '8/8h',
        durationDays: 10
      },
      {
        name: 'Amoxicilina',
        presentation: '500 mg comprimido',
        route: 'Oral',
        quantity: '21 comprimidos',
        posology: '500 mg de 8/8h por 7 dias — adulto ambulatorial',
        frequencyText: 'de 8 em 8 horas por 7 dias',
        scheduleInterval: '8/8h',
        durationDays: 7
      }
    ]
  },
  {
    id: 'itu-cistite',
    name: 'ITU — Cistite Aguda Não Complicada',
    category: 'Infectológica',
    firstLineSummary: 'Fosfomicina trometamol 3 g em dose única (1ª linha) ou nitrofurantoína 100 mg de 12/12h por 5 a 7 dias, em mulheres adultas.',
    pediatricRelevant: false,
    clinicalWarning: 'Colher urocultura ANTES do tratamento em gestantes, homens e suspeita de pielonefrite (febre + dor lombar). Não usar fosfomicina em pielonefrite.',
    reference: 'PCDT ITU / Diretrizes SBU (adaptadas das diretrizes IDSA).',
    medications: [
      {
        name: 'Fosfomicina trometamol',
        presentation: '3 g sachê',
        route: 'Oral',
        quantity: '1 sachê',
        posology: '3 g em dose única, à noite, após esvaziar a bexiga',
        frequencyText: 'dose única',
        scheduleInterval: 'Dose Única',
        durationDays: 1,
        instructions: 'Dissolver todo o conteúdo do sachê em meio copo de água e ingerir à noite, preferencialmente após esvaziar a bexiga.'
      },
      {
        name: 'Nitrofurantoína',
        presentation: '100 mg comprimido',
        route: 'Oral',
        quantity: '14 comprimidos',
        posology: '100 mg de 12/12h por 5 a 7 dias',
        frequencyText: 'de 12 em 12 horas por 5 a 7 dias',
        scheduleInterval: '12/12h',
        durationDays: 7
      }
    ]
  },
  {
    id: 'has',
    name: 'HAS — Hipertensão Arterial Sistêmica',
    category: 'Cardiovascular',
    firstLineSummary: 'Iniciar/otimizar com losartana 50 mg 1x/dia; associar hidroclorotiazida (combinação fixa) se a PA permanecer acima da meta após 2 a 4 semanas.',
    pediatricRelevant: false,
    clinicalWarning: 'Prescrever UMA das opções abaixo (não ambas). Dosar creatinina e potássio 2 a 4 semanas após início/ajuste de BRA. Contraindicado na gestação.',
    reference: 'Diretrizes Brasileiras de Hipertensão Arterial (SBH 2020).',
    medications: [
      {
        name: 'Losartana potássica',
        presentation: '50 mg comprimido',
        route: 'Oral',
        quantity: '30 comprimidos',
        posology: '50 mg 1x ao dia pela manhã (titular até 100 mg/dia se necessário)',
        frequencyText: '1x ao dia pela manhã',
        scheduleInterval: 'Uso Contínuo',
        isContinuous: true
      },
      {
        name: 'Losartana + Hidroclorotiazida',
        presentation: '50 + 12,5 mg comprimido',
        route: 'Oral',
        quantity: '30 comprimidos',
        posology: '1 comprimido 1x ao dia pela manhã (alternativa em combinação fixa)',
        frequencyText: '1x ao dia pela manhã',
        scheduleInterval: 'Uso Contínuo',
        isContinuous: true
      }
    ]
  },
  {
    id: 'dm2',
    name: 'DM2 — Diabetes Mellitus tipo 2',
    category: 'Endocrinológica',
    firstLineSummary: 'Metformina 500 mg 2x/dia junto às refeições, com titulação gradual até a meta de HbA1c, associada a mudanças de estilo de vida.',
    pediatricRelevant: false,
    clinicalWarning: 'Contraindicada se TFG < 30 mL/min (reavaliar se 30–45). Suspender 48 h antes de exames com contraste iodado. Vigiar hipovitaminose B12 no uso crônico.',
    reference: 'Diretrizes SBD / PCDT DM2 — Ministério da Saúde.',
    medications: [
      {
        name: 'Cloridrato de metformina',
        presentation: '500 mg comprimido',
        route: 'Oral',
        quantity: '60 comprimidos',
        posology: '500 mg 2x ao dia (café da manhã e jantar); titular até 1000 mg 2x/dia conforme tolerância e meta de HbA1c',
        frequencyText: '2x ao dia junto às refeições',
        scheduleInterval: 'Uso Contínuo',
        isContinuous: true
      }
    ]
  },
  {
    id: 'candidiase-vulvovaginal',
    name: 'Candidíase Vulvovaginal',
    category: 'Ginecológica',
    firstLineSummary: 'Fluconazol 150 mg VO em dose única; pode associar nistatina creme vaginal à noite por 14 dias.',
    pediatricRelevant: false,
    clinicalWarning: 'Evitar fluconazol ORAL na gestação (preferir nistatina vaginal). Investigar DM2 em casos recorrentes (≥ 4 episódios/ano).',
    reference: 'PCDT Infecções Sexualmente Transmissíveis — Ministério da Saúde.',
    medications: [
      {
        name: 'Fluconazol',
        presentation: '150 mg cápsula',
        route: 'Oral',
        quantity: '1 cápsula',
        posology: '150 mg em dose única',
        frequencyText: 'dose única',
        scheduleInterval: 'Dose Única',
        durationDays: 1
      },
      {
        name: 'Nistatina',
        presentation: 'Creme vaginal 25.000 UI/g (60 g) com aplicadores',
        route: 'Tópica',
        quantity: '1 bisnaga',
        posology: '1 aplicador (5 g) por via vaginal, à noite, por 14 dias',
        frequencyText: '1x ao dia à noite por 14 dias',
        scheduleInterval: '24/24h',
        durationDays: 14
      }
    ]
  },
  {
    id: 'malaria',
    name: 'Malária (não complicada)',
    category: 'Infectológica',
    firstLineSummary: 'Confirmação diagnóstica (gota espessa ou TDR) e tratamento conforme espécie, peso e região, seguindo o esquema do Manual de Tratamento da Malária do MS; sintomáticos com dipirona/paracetamol.',
    pediatricRelevant: true,
    clinicalWarning: 'Notificação compulsória IMEDIATA (SINAN). P. falciparum pode evoluir para forma grave — baixo limiar para internação. Não automedicar antimaláricos.',
    reference: 'Manual de Tratamento da Malária no Brasil — Ministério da Saúde (SVSA).',
    medications: [
      {
        name: 'Antimalárico — esquema conforme espécie',
        presentation: 'Conforme protocolo MS (P. vivax / P. falciparum) e peso do paciente',
        route: 'Oral',
        quantity: 'Conforme esquema',
        posology: 'Esquema completo conforme o Manual de Tratamento da Malária no Brasil (Ministério da Saúde) — dispensação e supervisão em unidade de saúde',
        frequencyText: 'conforme esquema supervisionado do MS',
        scheduleInterval: 'Uso Contínuo',
        instructions: 'Definir esquema antimalárico conforme espécie (P. vivax, P. falciparum ou mista), peso e situação clínica, seguindo o Manual de Tratamento da Malária no Brasil (MS/SVSA). Notificação imediata obrigatória.'
      },
      {
        pediatricMedId: 'dipirona-gotas',
        name: 'Dipirona Gotas',
        presentation: '500 mg/mL (1 gota = 25 mg)',
        route: 'Oral',
        quantity: '1 frasco',
        posology: '20 mg/kg/dose (~1 gota/kg) de 6/6h se febre (máx 1000 mg/dose)',
        frequencyText: 'de 6 em 6 horas se febre',
        scheduleInterval: 'S.O.S',
        durationDays: 5
      }
    ]
  }
];
