import { AdultMedication, PediatricMedication, Patient } from '../types';
import { ADULT_MEDICATIONS } from '../data/adultMeds';
import { PEDIATRIC_MEDICATIONS } from '../data/pediatricMeds';
import { calculatePediatricDose } from './doseCalculator';

export interface MedicationOption {
  id: string;
  sourceType: 'adult' | 'pediatric';
  name: string; // Ex: "Dipirona 500 mg (Novalgina)" ou "Dipirona Gotas 500 mg/mL"
  presentation: string; // Ex: "500 mg - Comprimido" ou "500 mg/mL (1 gota = 25 mg)"
  pharmaceuticalForm: string; // Ex: "Comprimido", "Gotas", "Suspensão oral", "Cápsula"
  concentration: string; // Ex: "500 mg", "500 mg/mL", "250 mg/5 mL"
  posology: string; // Posologia padrão ou calculada
  calculatedDoseBadge?: string; // Para ped: "14 gotas (0,7 mL)"
  calculatedVolumeText?: string;
  calculatedDrops?: number;
  calculatedMg?: number;
  route: string;
  defaultQuantity: string;
  defaultFrequency: string;
  defaultDays?: number;
  isSpecialControl: boolean;
  isPediatric: boolean;
  observations?: string;
  standardDoseMgKg?: number;
  maxDoseMg?: number;
  pediatricMed?: PediatricMedication;
  adultMed?: AdultMedication;
}

export interface BaseMedicationGroup {
  id: string;
  baseName: string; // Ex: "Dipirona", "Amoxicilina", "Paracetamol"
  tradeNames: string[]; // Ex: ["Novalgina", "Anador"]
  activeIngredient: string; // Ex: "Dipirona monoidratada"
  category: string; // Ex: "Analgésico / Antitérmico"
  hasPediatric: boolean;
  hasAdult: boolean;
  isSpecialControl: boolean;
  options: MedicationOption[];
}

// Normaliza texto para busca insensível a acentos e maiúsculas
export const normalizeSearchText = (text: string): string =>
  (text || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

// Deriva o nome base/fármaco principal a partir de um nome de medicamento
const extractBaseKey = (name: string, activeIngredient?: string): string => {
  const norm = normalizeSearchText(name + ' ' + (activeIngredient || ''));

  if (norm.includes('amoxicilina') && (norm.includes('clavulanat') || norm.includes('clavulin'))) {
    return 'amoxicilina-clavulanato';
  }
  if (norm.includes('amoxicilina')) return 'amoxicilina';
  if (norm.includes('dipirona') || norm.includes('novalgina') || norm.includes('anador')) return 'dipirona';
  if (norm.includes('paracetamol') || norm.includes('tylenol')) return 'paracetamol';
  if (norm.includes('ibuprofeno') || norm.includes('alivium') || norm.includes('advil')) return 'ibuprofeno';
  if (norm.includes('cetoprofeno') || norm.includes('profenid')) return 'cetoprofeno';
  if (norm.includes('losartana')) return 'losartana';
  if (norm.includes('omeprazol')) return 'omeprazol';
  if (norm.includes('pantoprazol')) return 'pantoprazol';
  if (norm.includes('esomeprazol')) return 'esomeprazol';
  if (norm.includes('prednisolona') || norm.includes('prelone')) return 'prednisolona';
  if (norm.includes('prednisona') || norm.includes('meticorten')) return 'prednisona';
  if (norm.includes('dexametasona') || norm.includes('decadron')) return 'dexametasona';
  if (norm.includes('ondansetrona') || norm.includes('vonau')) return 'ondansetrona';
  if (norm.includes('domperidona') || norm.includes('motilium')) return 'domperidona';
  if (norm.includes('metoclopramida') || norm.includes('plasil')) return 'metoclopramida';
  if (norm.includes('azitromicina') || norm.includes('zitromax') || norm.includes('astro')) return 'azitromicina';
  if (norm.includes('cefalexina') || norm.includes('keflex')) return 'cefalexina';
  if (norm.includes('cefuroxima') || norm.includes('zinnat')) return 'cefuroxima';
  if (norm.includes('ceftriaxona') || norm.includes('rocefin')) return 'ceftriaxona';
  if (norm.includes('ciprofloxacino') || norm.includes('cipro')) return 'ciprofloxacino';
  if (norm.includes('levofloxacino') || norm.includes('tamiram')) return 'levofloxacino';
  if (norm.includes('sulfametoxazol') || norm.includes('bactrim')) return 'sulfametoxazol-trimetoprima';
  if (norm.includes('nitrofurantoina') || norm.includes('macrodantina')) return 'nitrofurantoina';
  if (norm.includes('loratadina') || norm.includes('claritin')) return 'loratadina';
  if (norm.includes('desloratadina') || norm.includes('desalex')) return 'desloratadina';
  if (norm.includes('cetirizina') || norm.includes('zyrtec')) return 'cetirizina';
  if (norm.includes('hidroxizina') || norm.includes('hixizine')) return 'hidroxizina';
  if (norm.includes('dexclorfeniramina') || norm.includes('polaramine')) return 'dexclorfeniramina';
  if (norm.includes('salbutamol') || norm.includes('aerolin')) return 'salbutamol';
  if (norm.includes('budesonida') || norm.includes('bifos') || norm.includes('pulmicort')) return 'budesonida';
  if (norm.includes('fluticasona') || norm.includes('flixotide') || norm.includes('avamys')) return 'fluticasona';
  if (norm.includes('brometo de ipratropio') || norm.includes('atrovent')) return 'ipratropio';
  if (norm.includes('beclometasona') || norm.includes('clenil')) return 'beclometasona';
  if (norm.includes('clonazepam') || norm.includes('rivotril')) return 'clonazepam';
  if (norm.includes('diazepam') || norm.includes('valium')) return 'diazepam';
  if (norm.includes('alprazolam') || norm.includes('frontan')) return 'alprazolam';
  if (norm.includes('zolpidem') || norm.includes('stilnox')) return 'zolpidem';
  if (norm.includes('fluoxetina') || norm.includes('prozac') || norm.includes('daforin')) return 'fluoxetina';
  if (norm.includes('sertralina') || norm.includes('zoloft') || norm.includes('assert')) return 'sertralina';
  if (norm.includes('escitalopram') || norm.includes('lexapro') || norm.includes('reconter')) return 'escitalopram';
  if (norm.includes('venlafaxina') || norm.includes('efexor')) return 'venlafaxina';
  if (norm.includes('duloxetina') || norm.includes('cymbalta')) return 'duloxetina';
  if (norm.includes('pregabalina') || norm.includes('lyrica')) return 'pregabalina';
  if (norm.includes('gabapentina') || norm.includes('neurontin')) return 'gabapentina';
  if (norm.includes('tramadol') || norm.includes('tramal')) return 'tramadol';
  if (norm.includes('codeina') || norm.includes('paco') || norm.includes('tylex')) return 'codeina';
  if (norm.includes('morfina') || norm.includes('dimorf')) return 'morfina';
  if (norm.includes('atenolol')) return 'atenolol';
  if (norm.includes('propranolol')) return 'propranolol';
  if (norm.includes('metoprolol') || norm.includes('selozok')) return 'metoprolol';
  if (norm.includes('carvedilol')) return 'carvedilol';
  if (norm.includes('anlodipino') || norm.includes('norvasc')) return 'anlodipino';
  if (norm.includes('enalapril') || norm.includes('renitec')) return 'enalapril';
  if (norm.includes('captopril')) return 'captopril';
  if (norm.includes('hidroclorotiazida')) return 'hidroclorotiazida';
  if (norm.includes('furosemida') || norm.includes('lasix')) return 'furosemida';
  if (norm.includes('espironolactona') || norm.includes('aldactone')) return 'espironolactona';
  if (norm.includes('atorvastatina') || norm.includes('lipitor') || norm.includes('citalor')) return 'atorvastatina';
  if (norm.includes('rosuvastatina') || norm.includes('crestor')) return 'rosuvastatina';
  if (norm.includes('sinvastatina')) return 'sinvastatina';
  if (norm.includes('metformina') || norm.includes('glifage')) return 'metformina';
  if (norm.includes('gliclazida') || norm.includes('diamicron')) return 'gliclazida';
  if (norm.includes('insulina nph')) return 'insulina-nph';
  if (norm.includes('insulina regular')) return 'insulina-regular';
  if (norm.includes('levotiroxina') || norm.includes('puran') || norm.includes('euthyrox')) return 'levotiroxina';
  if (norm.includes('albendazol') || norm.includes('zentel')) return 'albendazol';
  if (norm.includes('mebendazol') || norm.includes('pantelmin')) return 'mebendazol';
  if (norm.includes('ivermectina') || norm.includes('revectina')) return 'ivermectina';
  if (norm.includes('nitazoxanida') || norm.includes('annita')) return 'nitazoxanida';
  if (norm.includes('fluconazol') || norm.includes('zolt') || norm.includes('flucanil')) return 'fluconazol';
  if (norm.includes('nistatina')) return 'nistatina';
  if (norm.includes('simeticona') || norm.includes('luftal')) return 'simeticona';
  if (norm.includes('lactulose')) return 'lactulose';
  if (norm.includes('polietilenoglicol') || norm.includes('peg 4000') || norm.includes('muvinlax')) return 'peg-4000';
  if (norm.includes('soro de reidratacao') || norm.includes('reidratacao oral') || norm.includes('pedialyte')) return 'soro-reidratacao';
  if (norm.includes('soro fisiologico') || norm.includes('cloreto de sodio 0,9') || norm.includes('rinosoro') || norm.includes('maresis')) return 'soro-fisiologico-nasal';

  // Fallback: primeira palavra limpa
  const firstWord = norm.split(/[\s\-\(\)\/,]+/)[0];
  return firstWord || 'outro';
};

// Formata o nome limpo e refinado para exibição do Grupo Base
const formatBaseDisplayName = (key: string, sampleTradeName: string, sampleActive: string): string => {
  const map: Record<string, string> = {
    'amoxicilina-clavulanato': 'Amoxicilina + Clavulanato de Potássio',
    'amoxicilina': 'Amoxicilina',
    'dipirona': 'Dipirona Monoidratada',
    'paracetamol': 'Paracetamol',
    'ibuprofeno': 'Ibuprofeno',
    'cetoprofeno': 'Cetoprofeno',
    'losartana': 'Losartana Potássica',
    'omeprazol': 'Omeprazol',
    'pantoprazol': 'Pantoprazol',
    'esomeprazol': 'Esomeprazol',
    'prednisolona': 'Prednisolona',
    'prednisona': 'Prednisona',
    'dexametasona': 'Dexametasona',
    'ondansetrona': 'Ondansetrona',
    'domperidona': 'Domperidona',
    'metoclopramida': 'Metoclopramida',
    'azitromicina': 'Azitromicina',
    'cefalexina': 'Cefalexina',
    'cefuroxima': 'Cefuroxima Axetil',
    'ceftriaxona': 'Ceftriaxona Sódica',
    'ciprofloxacino': 'Ciprofloxacino',
    'levofloxacino': 'Levofloxacino',
    'sulfametoxazol-trimetoprima': 'Sulfametoxazol + Trimetoprima',
    'nitrofurantoina': 'Nitrofurantoína',
    'loratadina': 'Loratadina',
    'desloratadina': 'Desloratadina',
    'cetirizina': 'Cetirizina',
    'hidroxizina': 'Hidroxizina',
    'dexclorfeniramina': 'Dexclorfeniramina (Polaramine)',
    'salbutamol': 'Sulfato de Salbutamol (Aerolin)',
    'budesonida': 'Budesonida',
    'fluticasona': 'Fluticasona',
    'ipratropio': 'Brometo de Ipratrópio (Atrovent)',
    'beclometasona': 'Dipropionato de Beclometasona',
    'clonazepam': 'Clonazepam (Rivotril)',
    'diazepam': 'Diazepam (Valium)',
    'alprazolam': 'Alprazolam (Frontal)',
    'zolpidem': 'Hemitartarato de Zolpidem',
    'fluoxetina': 'Cloridrato de Fluoxetina',
    'sertralina': 'Cloridrato de Sertralina',
    'escitalopram': 'Oxalato de Escitalopram',
    'venlafaxina': 'Cloridrato de Venlafaxina',
    'duloxetina': 'Cloridrato de Duloxetina',
    'pregabalina': 'Pregabalina',
    'gabapentina': 'Gabapentina',
    'tramadol': 'Cloridrato de Tramadol',
    'codeina': 'Fosfato de Codeína',
    'morfina': 'Sulfato de Morfina',
    'atenolol': 'Atenolol',
    'propranolol': 'Cloridrato de Propranolol',
    'metoprolol': 'Succinato de Metoprolol',
    'carvedilol': 'Carvedilol',
    'anlodipino': 'Besilato de Anlodipino',
    'enalapril': 'Maleato de Enalapril',
    'captopril': 'Captopril',
    'hidroclorotiazida': 'Hidroclorotiazida',
    'furosemida': 'Furosemida (Lasix)',
    'espironolactona': 'Espironolactona (Aldactone)',
    'atorvastatina': 'Atorvastatina Cálcica',
    'rosuvastatina': 'Rosuvastatina Cálcica',
    'sinvastatina': 'Sinvastatina',
    'metformina': 'Cloridrato de Metformina',
    'gliclazida': 'Gliclazida MR',
    'insulina-nph': 'Insulina Humana NPH',
    'insulina-regular': 'Insulina Humana Regular',
    'levotiroxina': 'Levotiroxina Sódica',
    'albendazol': 'Albendazol',
    'mebendazol': 'Mebendazol',
    'ivermectina': 'Ivermectina',
    'nitazoxanida': 'Nitazoxanida (Annita)',
    'fluconazol': 'Fluconazol',
    'nistatina': 'Nistatina',
    'simeticona': 'Simeticona (Luftal)',
    'lactulose': 'Lactulose',
    'peg-4000': 'Polietilenoglicol 4000 (PEG 4000)',
    'soro-reidratacao': 'Sais para Reidratação Oral (SRO)',
    'soro-fisiologico-nasal': 'Solução Salina Nasal (SF 0,9%)'
  };

  if (map[key]) return map[key];
  if (sampleActive) return sampleActive;
  return sampleTradeName.split(' ')[0] || key;
};

// Constrói todos os grupos de medicamentos base com suas opções individuais
export const getAllMedicationGroups = (patient?: Patient): BaseMedicationGroup[] => {
  const patientWeight = patient?.weightKg ?? 0;
  const hasWeight = patientWeight > 0;

  const groupsMap = new Map<string, {
    baseName: string;
    tradeNames: Set<string>;
    activeIngredient: string;
    category: string;
    options: MedicationOption[];
  }>();

  // 1. Processa Medicamentos Adultos
  ADULT_MEDICATIONS.forEach((adult) => {
    const key = extractBaseKey(adult.tradeName, adult.activeIngredient);
    const isSpecial = adult.isSpecialControl ||
      (adult.category ? (adult.category.toLowerCase().includes('control') || adult.category.toLowerCase().includes('psicotrópico') || adult.category.toLowerCase().includes('b1')) : false);

    const option: MedicationOption = {
      id: `adult-${adult.id}`,
      sourceType: 'adult',
      name: adult.tradeName,
      presentation: adult.pharmaceuticalForm ? `${adult.concentration} - ${adult.pharmaceuticalForm}` : adult.concentration,
      pharmaceuticalForm: adult.pharmaceuticalForm || 'Comprimido',
      concentration: adult.concentration,
      posology: adult.adultPosology,
      route: adult.route || 'Oral',
      defaultQuantity: adult.defaultQuantity || '1 caixa',
      defaultFrequency: adult.defaultFrequency || '8/8h',
      isSpecialControl: isSpecial,
      isPediatric: false,
      observations: adult.observations,
      adultMed: adult
    };

    if (!groupsMap.has(key)) {
      groupsMap.set(key, {
        baseName: formatBaseDisplayName(key, adult.tradeName, adult.activeIngredient),
        tradeNames: new Set([adult.tradeName]),
        activeIngredient: adult.activeIngredient || adult.tradeName,
        category: adult.category || 'Adulto',
        options: [option]
      });
    } else {
      const g = groupsMap.get(key)!;
      g.tradeNames.add(adult.tradeName);
      g.options.push(option);
    }
  });

  // 2. Processa Medicamentos Pediátricos
  PEDIATRIC_MEDICATIONS.forEach((ped) => {
    const key = extractBaseKey(ped.name);
    const calc = hasWeight ? calculatePediatricDose(ped, patientWeight) : null;
    let posologyText = ped.observations || 'Uso pediátrico conforme orientação médica.';
    if (calc) {
      posologyText = calc.instructionsText || calc.formattedPrescriptionText;
    }

    const option: MedicationOption = {
      id: `ped-${ped.id}`,
      sourceType: 'pediatric',
      name: ped.name,
      presentation: ped.presentation,
      pharmaceuticalForm: ped.unitType === 'drops' ? 'Solução oral gotas' : ped.unitType === 'ml' ? 'Suspensão / Solução oral' : ped.unitType === 'spray' ? 'Spray / Inalatório' : 'Uso Pediátrico',
      concentration: ped.presentation,
      posology: posologyText,
      calculatedDoseBadge: calc ? `${calc.volumeText} (${calc.dropsText !== '-' ? calc.dropsText : calc.rawDoseText})` : undefined,
      calculatedVolumeText: calc?.volumeText,
      calculatedDrops: calc?.calculatedDrops,
      calculatedMg: calc?.calculatedMg,
      route: ped.route || 'Oral',
      defaultQuantity: ped.unitType === 'fixed' && !ped.presentation.toLowerCase().includes('gotas') ? '1 caixa' : '1 frasco',
      defaultFrequency: ped.frequency.includes('6/6') ? '6/6h' : ped.frequency.includes('8/8') ? '8/8h' : ped.frequency.includes('12/12') ? '12/12h' : '24/24h',
      defaultDays: ped.defaultDays || 3,
      isSpecialControl: false,
      isPediatric: true,
      observations: ped.observations,
      standardDoseMgKg: ped.standardDoseMgKg,
      maxDoseMg: ped.maxDoseMg,
      pediatricMed: ped
    };

    if (!groupsMap.has(key)) {
      groupsMap.set(key, {
        baseName: formatBaseDisplayName(key, ped.name, ped.name),
        tradeNames: new Set([ped.name]),
        activeIngredient: ped.name,
        category: ped.category || 'Pediátrico',
        options: [option]
      });
    } else {
      const g = groupsMap.get(key)!;
      g.tradeNames.add(ped.name);
      g.options.push(option);
    }
  });

  // Converte para array estruturado e ordenado
  const result: BaseMedicationGroup[] = Array.from(groupsMap.entries()).map(([id, g]) => ({
    id,
    baseName: g.baseName,
    tradeNames: Array.from(g.tradeNames),
    activeIngredient: g.activeIngredient,
    category: g.category,
    hasPediatric: g.options.some(o => o.isPediatric),
    hasAdult: g.options.some(o => !o.isPediatric),
    isSpecialControl: g.options.some(o => o.isSpecialControl),
    options: g.options
  }));

  // Ordena alfabeticamente pelo nome base
  result.sort((a, b) => a.baseName.localeCompare(b.baseName, 'pt-BR'));

  return result;
};

import { searchMedicationsFuzzy, scoreMedicationGroup } from './fuzzySearch';

// Filtra e classifica grupos de medicamentos com base no termo de busca fuzzy e filtro de categoria/tipo
export const searchMedicationGroups = (
  groups: BaseMedicationGroup[],
  query: string,
  filter: 'todos' | 'pediatric' | 'adult' | 'special' = 'todos',
  categoryFilter: string = 'todos'
): BaseMedicationGroup[] => {
  const fuzzyResults = searchMedicationsFuzzy(groups, query, filter, categoryFilter);
  return fuzzyResults.map(r => r.group);
};

