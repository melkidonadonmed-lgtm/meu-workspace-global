export interface DoctorProfile {
  name: string;
  crm: string;
  crmState: string;
  specialty: string;
  rqe?: string;
  clinicName: string;
  address: string;
  cityState: string;
  phone: string;
  email: string;
  showSignature: boolean;
  signatureText?: string;
  stampText?: string;
}

export interface Patient {
  id: string;
  name: string;
  weightKg: number;
  weightCalcEnabled?: boolean;
  birthDate?: string;
  ageText?: string;
  gender: 'male' | 'female' | 'other';
  documentNumber?: string; // RG or CPF
  allergies: string[];
  motherName?: string;
  notes?: string;
  phone?: string;
}

export interface PediatricMedication {
  id: string;
  category: string;
  name: string;
  presentation: string;
  concentrationMgPerMl: number;
  standardDoseMgKg: number;
  maxDoseMg: number;
  unitType: 'drops' | 'ml' | 'mg' | 'fixed' | 'spray' | 'ampoule';
  frequency: string;
  route: string;
  observations: string;
  dropsPerMl?: number; // default is 20 drops per ml unless specified
  doseCustomLabel?: string;
  defaultDays?: number;
}

export interface AdultMedication {
  id: string;
  activeIngredient: string;
  tradeName: string;
  concentration: string;
  pharmaceuticalForm: string;
  adultPosology: string;
  pediatricDose?: string;
  observations?: string;
  category?: string;
  route?: string;
  defaultQuantity?: string;
  defaultFrequency?: string;
  isSpecialControl?: boolean;
}

export interface PrescriptionItem {
  id: string;
  name: string;
  presentation: string;
  route: string; // Oral, Tópica, Inalatória, Injetável, Otológica, Oftálmica, Sublingual, Retal
  quantity: string; // ex: "1 frasco", "2 caixas", "30 comprimidos"
  doseCalculatedText: string; // ex: "18 gotas (0,9 mL)", "1 comprimido", "5 mL"
  frequencyText: string; // ex: "de 6 em 6 horas se dor ou febre"
  scheduleInterval: string; // "4/4h", "6/6h", "8/8h", "12/12h", "24/24h", "Dose Única", "Uso Contínuo", "S.O.S"
  scheduleTimes: string[]; // ex: ["06:00", "12:00", "18:00", "00:00"]
  durationDays?: number;
  instructions: string; // Detailed instructions
  isContinuous: boolean;
  isSpecialControl?: boolean; // Receita de controle especial (C1, B1, etc.)
  calculatedFromWeight?: number; // If calculated for a specific weight
}

export interface ExamItem {
  id: string;
  category: string;
  name: string;
  description?: string;
  selected: boolean;
  urgency: 'routine' | 'urgent';
  clinicalIndication?: string;
}

export interface MedicalCertificate {
  id?: string;
  patientName: string;
  documentType?: 'RG' | 'CPF';
  documentNumber: string;
  birthDate?: string;
  daysOff: number;
  startDate: string;
  endDate: string;
  periodText: string; // "por motivo de saúde", "para fins de acompanhamento", "para fins de perícia"
  includeCID: boolean;
  cid10Code: string;
  cid10Description: string;
  observations: string;
  cityDateText?: string;
}

export interface MedicalReferral {
  id?: string;
  patientName: string;
  documentNumber: string;
  destinationSpecialty: string;
  destinationInstitution?: string;
  reason: string;
  clinicalSummary: string;
  relevantExams: string;
  hypothesisCID: string;
  priority: 'eletivo' | 'prioritario' | 'urgente';
  date?: string;
}

export interface ClinicalProtocol {
  id: string;
  title: string;
  condition: string;
  ruleFormula: string;
  routeDilution: string;
  frequencyTime: string;
  clinicalNotes: string;
  calculateVolume: (weight: number) => { volumeText: string; detail: string; rate?: string };
}

// Decks de patologias (protocolos ambulatoriais acionáveis)
export interface ProtocolMedication {
  /** Referência opcional ao id em PEDIATRIC_MEDICATIONS para cálculo de dose por peso */
  pediatricMedId?: string;
  name: string;
  presentation: string;
  route: string; // Oral, Tópica, Inalatória, Injetável, etc.
  quantity: string; // ex: "1 frasco", "30 comprimidos"
  posology: string; // posologia de referência (texto exibido no card)
  frequencyText: string; // ex: "de 6 em 6 horas se dor ou febre"
  scheduleInterval: string; // "6/6h", "12/12h", "24/24h", "Dose Única", "Uso Contínuo", "S.O.S"
  durationDays?: number;
  isContinuous?: boolean;
  instructions?: string; // instruções extras para a prescrição
}

export interface PathologyProtocol {
  id: string;
  name: string;
  category: string; // grupo (ex: Infectológica, Cardiovascular)
  firstLineSummary: string; // resumo do tratamento de 1ª linha
  pediatricRelevant: boolean; // se contempla dose pediátrica por peso
  clinicalWarning?: string; // alerta clínico de segurança
  reference: string; // fonte de referência (ex: manual/protocolo do MS)
  medications: ProtocolMedication[];
}

export type ActiveTab = 
  | 'prescription' 
  | 'pediatric_calc' 
  | 'exams' 
  | 'certificate' 
  | 'referral' 
  | 'protocols'
  | 'models'
  | 'print_preview' 
  | 'patients';
