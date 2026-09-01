import { ExamItem } from '../types';

export const EXAM_CATALOG: ExamItem[] = [
  // Hematologia & Coagulação
  { id: 'hemograma', category: 'Hematologia', name: 'Hemograma Completo com Contagem de Plaquetas', selected: false, urgency: 'routine' },
  { id: 'coagulograma', category: 'Hematologia', name: 'Coagulograma Completo (TAP, TTPA, INR, Fibrinogênio)', selected: false, urgency: 'routine' },
  { id: 'tipagem-sanguinea', category: 'Hematologia', name: 'Tipagem Sanguínea (Sistema ABO e Fator Rh)', selected: false, urgency: 'routine' },
  { id: 'ferritina', category: 'Hematologia', name: 'Ferritina Sérica + Ferro Sérico + Capacidade Total de Ligação (TIBC)', selected: false, urgency: 'routine' },
  { id: 'vitamina-b12', category: 'Hematologia', name: 'Vitamina B12 (Cobalamina) e Ácido Fólico Sérico', selected: false, urgency: 'routine' },
  { id: 'reticulocitos', category: 'Hematologia', name: 'Contagem de Reticulócitos', selected: false, urgency: 'routine' },

  // Bioquímica & Metabólico
  { id: 'glicemia-jejum', category: 'Bioquímica', name: 'Glicemia de Jejum', selected: false, urgency: 'routine' },
  { id: 'hba1c', category: 'Bioquímica', name: 'Hemoglobina Glicada (HbA1c)', selected: false, urgency: 'routine' },
  { id: 'perfil-lipidico', category: 'Bioquímica', name: 'Perfil Lipídico Completo (Colesterol Total, HDL, LDL, VLDL, Triglicerídeos)', selected: false, urgency: 'routine' },
  { id: 'ureia-creatinina', category: 'Bioquímica', name: 'Ureia e Creatinina com Estimativa de Ritmo de Filtração Glomerular (eRFG)', selected: false, urgency: 'routine' },
  { id: 'acido-urico', category: 'Bioquímica', name: 'Ácido Úrico Sérico', selected: false, urgency: 'routine' },
  { id: 'eletronograma', category: 'Bioquímica', name: 'Eletrólitos Séricos (Sódio, Potássio, Cálcio Iônico, Magnésio, Fósforo)', selected: false, urgency: 'routine' },
  { id: 'gasometria-arterial', category: 'Bioquímica', name: 'Gasometria Arterial com Lactato Sérico', selected: false, urgency: 'urgent' },

  // Função Hepática & Pancreática
  { id: 'hepatograma', category: 'Hepatologia', name: 'Hepatograma Completo (TGO/AST, TGP/ALT, Gama-GT, Fosfatase Alcalina, Bilirrubinas)', selected: false, urgency: 'routine' },
  { id: 'proteinas-totais', category: 'Hepatologia', name: 'Proteínas Totais e Frações (Albumina e Globulinas)', selected: false, urgency: 'routine' },
  { id: 'amilase-lipase', category: 'Hepatologia', name: 'Amilase e Lipase Séricas', selected: false, urgency: 'routine' },

  // Marcadores Inflamatórios & Sorologias
  { id: 'pcr-vhs', category: 'Inflamatório / Sorologia', name: 'Proteína C-Reativa Ultrassensível (PCR) e VHS', selected: false, urgency: 'routine' },
  { id: 'sorologia-dengue', category: 'Inflamatório / Sorologia', name: 'Pesquisa de Antígeno NS1 para Dengue + Sorologia IgM/IgG', selected: false, urgency: 'urgent' },
  { id: 'hiv-hepatites', category: 'Inflamatório / Sorologia', name: 'Painel Sorológico (Anti-HIV 1 e 2, HBsAg, Anti-HCV, VDRL/Sífilis)', selected: false, urgency: 'routine' },
  { id: 'troponina-ckmb', category: 'Cardiovascular', name: 'Troponina Cardíaca de Alta Sensibilidade e CK-MB Massa', selected: false, urgency: 'urgent' },
  { id: 'bnp-ntprobnp', category: 'Cardiovascular', name: 'BNP / NT-proBNP (Peptídeo Natriurético)', selected: false, urgency: 'routine' },

  // Hormônios & Tireoide
  { id: 'tsh-t4livre', category: 'Endócrino', name: 'TSH e T4 Livre', selected: false, urgency: 'routine' },
  { id: 'vitamina-d', category: 'Endócrino', name: '25-Hidroxivitamina D (Vitamina D3)', selected: false, urgency: 'routine' },
  { id: 'beta-hcg', category: 'Endócrino', name: 'Beta-HCG Quantitativo Sanguíneo', selected: false, urgency: 'urgent' },

  // Urina & Fezes
  { id: 'eas-urina', category: 'Urinálise / Parasitologia', name: 'EAS / Sumário de Urina (Urina Tipo 1)', selected: false, urgency: 'routine' },
  { id: 'urocultura-tsa', category: 'Urinálise / Parasitologia', name: 'Urocultura com Teste de Sensibilidade a Antimicrobianos (TSA/Antibiograma)', selected: false, urgency: 'routine' },
  { id: 'parasitologico-fezes', category: 'Urinálise / Parasitologia', name: 'Exame Parasitológico de Fezes (3 amostras - Método Hoffman)', selected: false, urgency: 'routine' },
  { id: 'sangue-oculto', category: 'Urinálise / Parasitologia', name: 'Pesquisa de Sangue Oculto nas Fezes (Método Imunoquímico)', selected: false, urgency: 'routine' },

  // Imagem & Métodos Gráficos
  { id: 'rx-torax', category: 'Imagem & Gráficos', name: 'Radiografia de Tórax em PA e Perfil', selected: false, urgency: 'routine' },
  { id: 'rx-abdomen', category: 'Imagem & Gráficos', name: 'Radiografia Simples de Abdome (Ortostática e Decúbito)', selected: false, urgency: 'routine' },
  { id: 'usg-abdomen-total', category: 'Imagem & Gráficos', name: 'Ultrassonografia de Abdome Total com Doppler', selected: false, urgency: 'routine' },
  { id: 'usg-vias-urinarias', category: 'Imagem & Gráficos', name: 'Ultrassonografia dos Rins e Vias Urinárias', selected: false, urgency: 'routine' },
  { id: 'usg-tireoide', category: 'Imagem & Gráficos', name: 'Ultrassonografia da Glândula Tireoide com Doppler', selected: false, urgency: 'routine' },
  { id: 'tc-cranio', category: 'Imagem & Gráficos', name: 'Tomografia Computadorizada de Crânio sem Contraste', selected: false, urgency: 'urgent' },
  { id: 'tc-torax', category: 'Imagem & Gráficos', name: 'Tomografia Computadorizada de Tórax de Alta Resolução', selected: false, urgency: 'routine' },
  { id: 'ecg', category: 'Imagem & Gráficos', name: 'Eletrocardiograma Convencional de 12 Derivações (ECG)', selected: false, urgency: 'routine' },
  { id: 'ecocardiograma', category: 'Imagem & Gráficos', name: 'Ecocardiograma Transtorácico com Doppler Colorido', selected: false, urgency: 'routine' }
];

export interface ExamPackage {
  id: string;
  name: string;
  badge: string;
  examIds: string[];
  description: string;
}

export const EXAM_PACKAGES: ExamPackage[] = [
  {
    id: 'checkup-geral',
    name: 'Check-up Geral Clínico',
    badge: 'Rotina',
    examIds: ['hemograma', 'glicemia-jejum', 'perfil-lipidico', 'ureia-creatinina', 'hepatograma', 'eas-urina', 'ecg', 'vitamina-d'],
    description: 'Painel completo preventivo de saúde do adulto.'
  },
  {
    id: 'investigacao-infecciosa',
    name: 'Investigação de Síndrome Infecciosa / Febre',
    badge: 'Urgência',
    examIds: ['hemograma', 'pcr-vhs', 'eas-urina', 'urocultura-tsa', 'rx-torax', 'sorologia-dengue'],
    description: 'Rastreio sistemático de foco bacteriano ou viral agudo.'
  },
  {
    id: 'pre-operatorio',
    name: 'Painel Pré-Operatório Básico',
    badge: 'Cirúrgico',
    examIds: ['hemograma', 'coagulograma', 'ureia-creatinina', 'glicemia-jejum', 'ecg', 'rx-torax', 'tipagem-sanguinea'],
    description: 'Avaliação de risco cirúrgico e anestésico padrão.'
  },
  {
    id: 'cardio-renal',
    name: 'Avaliação Cardiovascular & Renal',
    badge: 'Especializado',
    examIds: ['hemograma', 'ureia-creatinina', 'eletronograma', 'perfil-lipidico', 'hba1c', 'eas-urina', 'ecg', 'ecocardiograma'],
    description: 'Monitoramento rigoroso de pacientes hipertensos, diabéticos ou nefropatas.'
  },
  {
    id: 'pediatrico-basico',
    name: 'Painel Pediátrico de Rotina / Anemia',
    badge: 'Pediatria',
    examIds: ['hemograma', 'ferritina', 'parasitologico-fezes', 'eas-urina', 'vitamina-d'],
    description: 'Rastreio de anemia ferropriva, verminoses e desenvolvimento infantil.'
  }
];
