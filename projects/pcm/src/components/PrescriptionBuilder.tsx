import React, { useState, useEffect, useMemo } from 'react';
import {
  Plus,
  Trash2,
  Copy,
  Check,
  ChevronUp,
  ChevronDown,
  Search,
  Scale,
  AlertTriangle,
  X,
  Pill,
  RotateCcw,
  Printer,
  FileText,
  Sparkles,
  ArrowRight,
  Calculator,
  Clock,
  Layers,
  Edit2,
  Send,
  Share2
} from 'lucide-react';
import { PrescriptionItem, Patient, DoctorProfile } from '../types';
import { generateScheduleTimes } from '../utils/doseCalculator';
import { generateMedicalPDF } from '../utils/pdfGenerator';
import { UNIFIED_MEDICATIONS, UnifiedMedication, CATEGORY_LABELS } from '../data/medicationDatabase';

interface PrescriptionBuilderProps {
  darkMode: boolean;
  doctor: DoctorProfile;
  onUpdateDoctor: (doctor: DoctorProfile) => void;
  patient: Patient;
  onUpdatePatient: (patient: Patient) => void;
  items: PrescriptionItem[];
  onUpdateItems: (items: PrescriptionItem[]) => void;
  weightCalcEnabled?: boolean;
  onToggleWeightCalc?: (enabled: boolean) => void;
  onClearPrescription?: () => void;
  onNavigateToPrint: () => void;
  onNavigateToPediatricCalc: () => void;
  onOpenDoctorModal: () => void;
  onOpenPatientModal: () => void;
}

export const PrescriptionBuilder: React.FC<PrescriptionBuilderProps> = ({
  darkMode,
  doctor,
  patient,
  onUpdatePatient,
  items,
  onUpdateItems,
  onClearPrescription,
  onNavigateToPrint,
  onNavigateToPediatricCalc,
  onOpenPatientModal
}) => {
  // Mobile active tab ('composer' | 'preview')
  const [mobileSection, setMobileSection] = useState<'composer' | 'preview'>('composer');

  // Search & Category Filter
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Active form fields for adding/editing
  const [selectedMedName, setSelectedMedName] = useState('');
  const [selectedRoute, setSelectedRoute] = useState('Uso Oral');
  const [selectedQuantity, setSelectedQuantity] = useState('1 caixa');
  const [selectedPosology, setSelectedPosology] = useState('');
  const [selectedIsSpecial, setSelectedIsSpecial] = useState(false);

  // Pediatric quick dosage calculation state
  const [selectedPediaDrugKey, setSelectedPediaDrugKey] = useState<string | null>(null);
  const [calculatedPediaResult, setCalculatedPediaResult] = useState<{
    name: string;
    route: string;
    quantity: string;
    instructions: string;
    calculatedDrops?: number;
    calculatedMl?: number;
    doseMg?: number;
  } | null>(null);

  // Feedbacks
  const [copiedSuccess, setCopiedSuccess] = useState(false);
  const [itemAddedToast, setItemAddedToast] = useState(false);

  // Estados de Recolher/Expandir (Collapsible) para Kits e Calculadora Pediátrica
  const [showKits, setShowKits] = useState<boolean>(() => {
    const saved = localStorage.getItem('prescmed_show_kits');
    return saved !== null ? saved === 'true' : false; // Fechado por padrão para dar prioridade máxima à busca
  });

  const [showPediaCalc, setShowPediaCalc] = useState<boolean>(() => {
    const saved = localStorage.getItem('prescmed_show_pedia_calc');
    if (saved !== null) return saved === 'true';
    return false; // Fechado por padrão, com expansão sob demanda
  });

  const toggleKits = () => {
    setShowKits(prev => {
      const next = !prev;
      localStorage.setItem('prescmed_show_kits', String(next));
      return next;
    });
  };

  const togglePediaCalc = () => {
    setShowPediaCalc(prev => {
      const next = !prev;
      localStorage.setItem('prescmed_show_pedia_calc', String(next));
      return next;
    });
  };

  const patientWeight = patient?.weightKg && patient.weightKg > 0 ? patient.weightKg : 0;
  const hasWeight = patientWeight > 0;
  const patientName = patient?.name?.trim() || '';

  // Quick frequent drugs chips for 1-click loading
  const quickMedChips = [
    { label: 'Dipirona 500mg', query: 'Dipirona Sódica 500mg comprimido' },
    { label: 'Paracetamol 750mg', query: 'Paracetamol 750mg comprimido' },
    { label: 'Ibuprofeno 600mg', query: 'Ibuprofeno 600mg comprimido' },
    { label: 'Amoxicilina 500mg', query: 'Amoxicilina 500mg cápsulas' },
    { label: 'Amox + Clav 875mg', query: 'Amoxicilina + Clavulanato 875' },
    { label: 'Losartana 50mg', query: 'Losartana Potássica 50mg' },
    { label: 'Omeprazol 20mg', query: 'Omeprazol 20mg' },
    { label: 'Prednisolona 3mg/mL', query: 'Prednisolona 3mg/mL' },
    { label: 'Azitromicina 500mg', query: 'Azitromicina 500mg' },
    { label: 'Ondansetrona 4mg', query: 'Ondansetrona 4mg' },
    { label: 'Metformina 850mg', query: 'Cloridrato de Metformina 850mg' },
    { label: 'SRO Envelopes', query: 'Sais de Reidratação Oral' }
  ];

  // Quick Posology text shortcuts
  const posologyShortcuts = [
    { label: '6/6h se dor/febre', text: 'Tomar 1 comprimido via oral de 6 em 6 horas em caso de dor ou febre.' },
    { label: '8/8h por 3-5 dias', text: 'Tomar 1 comprimido via oral de 8 em 8 horas após as refeições por 3 a 5 dias.' },
    { label: '1x ao dia (Manhã)', text: 'Tomar 1 comprimido via oral 1 vez ao dia, pela manhã.' },
    { label: '12/12h por 7-10 dias', text: 'Tomar 1 comprimido via oral de 12 em 12 horas durante 7 a 10 dias seguidos.' },
    { label: 'Uso Contínuo', text: 'Uso contínuo conforme orientação médica.' },
    { label: 'À noite ao deitar', text: 'Tomar 1 comprimido via oral à noite ao deitar.' },
    { label: 'Jejum 30min antes', text: 'Tomar 1 cápsula via oral pela manhã em jejum, 30 minutos antes do café da manhã.' }
  ];

  // Kits Clínicos Rápidos para Visitas Domiciliares e Plantão de Pronto-Atendimento
  const clinicalKits = [
    {
      id: 'kit_amigdalite',
      name: 'Amigdalite Bacteriana',
      badge: 'Amoxicilina + AINE',
      description: 'Amoxicilina 500mg (10d) + Ibuprofeno 600mg + Dipirona',
      items: [
        {
          name: 'Amoxicilina 500mg cápsula (Amoxil)',
          route: 'Uso Oral',
          quantity: '1 caixa (21 cápsulas)',
          instructions: 'Tomar 1 cápsula via oral de 8 em 8 horas durante 7 a 10 dias consecutivos.',
          pediaDrugKey: 'amoxicilina_susp'
        },
        {
          name: 'Ibuprofeno 600mg comprimido',
          route: 'Uso Oral',
          quantity: '1 caixa (10 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral de 8 em 8 horas após as refeições por 3 dias.',
          pediaDrugKey: 'ibuprofeno_100'
        },
        {
          name: 'Dipirona Sódica 500mg comprimido (Novalgina)',
          route: 'Uso Oral',
          quantity: '1 caixa (20 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral de 6 em 6 horas em caso de dor ou febre.',
          pediaDrugKey: 'dipirona_gotas'
        }
      ]
    },
    {
      id: 'kit_geca',
      name: 'Gastroenterite & Vômitos (GECA)',
      badge: 'Antiemético + SRO',
      description: 'Ondansetrona + SRO Hidratação + Simeticona',
      items: [
        {
          name: 'Ondansetrona 8mg comprimido de desintegração oral (Vonau Flash)',
          route: 'Uso Oral',
          quantity: '1 caixa (10 comprimidos)',
          instructions: 'Dissolver 1 comprimido sob a língua de 8 em 8 horas em caso de náuseas ou vômitos.'
        },
        {
          name: 'Sais para Reidratação Oral (SRO) 27,9g sachê',
          route: 'Uso Oral',
          quantity: '4 envelopes',
          instructions: 'Diluir 1 envelope em 1 litro de água filtrada/fervida. Beber ao longo do dia e após cada evacuação líquida.'
        },
        {
          name: 'Simeticona 75mg/mL emulsão oral gotas (Luftal)',
          route: 'Uso Oral',
          quantity: '1 frasco (15 mL)',
          instructions: 'Tomar 40 gotas via oral de 8 em 8 horas em caso de cólicas e gases.'
        }
      ]
    },
    {
      id: 'kit_ivas',
      name: 'IVAS / Gripe & Resfriado',
      badge: 'Sintomáticos + Lavagem',
      description: 'Dipirona + Paracetamol + Lavagem Nasal com SF 0,9%',
      items: [
        {
          name: 'Dipirona Sódica 500mg comprimido (Novalgina)',
          route: 'Uso Oral',
          quantity: '1 caixa (20 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral de 6 em 6 horas em caso de dor ou febre.',
          pediaDrugKey: 'dipirona_gotas'
        },
        {
          name: 'Paracetamol 750mg comprimido (Tylenol)',
          route: 'Uso Oral',
          quantity: '1 caixa (20 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral de 8 em 8 horas se dor persistente.',
          pediaDrugKey: 'paracetamol_gotas'
        },
        {
          name: 'Cloreto de Sódio 0,9% frasco para lavagem nasal (Soro Fisiológico)',
          route: 'Uso Nasal',
          quantity: '1 frasco (100 mL)',
          instructions: 'Aplicar 5 a 10 mL em cada narina com seringa ou spray de 4 em 4 horas.'
        }
      ]
    },
    {
      id: 'kit_lombalgia',
      name: 'Lombalgia / Dor Aguda',
      badge: 'AINE + Relaxante Muscular',
      description: 'Cetoprofeno + Dipirona 1g + Ciclobenzaprina + Omeprazol',
      items: [
        {
          name: 'Cetoprofeno 100mg comprimido (Profenid)',
          route: 'Uso Oral',
          quantity: '1 caixa (10 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral de 12 em 12 horas após as refeições por 5 dias.'
        },
        {
          name: 'Dipirona Sódica 1g comprimido',
          route: 'Uso Oral',
          quantity: '1 caixa (10 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral de 6 em 6 horas em caso de dor intensa.'
        },
        {
          name: 'Cloridrato de Ciclobenzaprina 5mg comprimido (Miosan)',
          route: 'Uso Oral',
          quantity: '1 caixa (10 comprimidos)',
          instructions: 'Tomar 1 comprimido via oral à noite ao deitar durante 5 dias.'
        },
        {
          name: 'Omeprazol 20mg cápsula',
          route: 'Uso Oral',
          quantity: '1 caixa (14 cápsulas)',
          instructions: 'Tomar 1 cápsula via oral pela manhã em jejum durante o uso do anti-inflamatório.'
        }
      ]
    },
    {
      id: 'kit_itu',
      name: 'Infecção Urinária (ITU)',
      badge: 'Fosfomicina + Analgésico',
      description: 'Fosfomicina 3g Dose Única + Buscopan Composto',
      items: [
        {
          name: 'Fosfomicina Trometamol 3g sachê granulado (Monuril)',
          route: 'Uso Oral',
          quantity: '1 envelope (3g)',
          instructions: 'Dissolver em 1/2 copo de água e tomar em dose única à noite antes de deitar, após esvaziar a bexiga.'
        },
        {
          name: 'Butilbrometo de Escopolamina + Dipirona (Buscopan Composto)',
          route: 'Uso Oral',
          quantity: '1 caixa (20 drágeas)',
          instructions: 'Tomar 1 a 2 drágeas via oral de 8 em 8 horas em caso de dor ou cólica.'
        }
      ]
    },
    {
      id: 'kit_asma',
      name: 'Crise de Asma / Broncoespasmo',
      badge: 'Spray + Corticoide',
      description: 'Salbutamol Spray 100mcg + Prednisolona Oral',
      items: [
        {
          name: 'Sulfato de Salbutamol 100mcg/dose spray aerossol (Aerolin)',
          route: 'Uso Inalatória',
          quantity: '1 frasco (200 doses)',
          instructions: 'Inalar 2 a 4 jatos com espaçador de 6 em 6 horas ou de 4 em 4 horas se tosse/falta de ar.'
        },
        {
          name: 'Prednisolona 20mg comprimido (ou 3mg/mL suspensão)',
          route: 'Uso Oral',
          quantity: '1 caixa (10 comprimidos)',
          instructions: 'Tomar 1 a 2 comprimidos (40mg) via oral pela manhã durante 5 dias.',
          pediaDrugKey: 'prednisolona_sol'
        }
      ]
    }
  ];

  // Filter medications based on search and category
  const filteredMedications = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    return UNIFIED_MEDICATIONS.filter(med => {
      const matchCat = activeCategory === 'all' || med.category === activeCategory;
      if (!matchCat) return false;
      if (!term) return true;
      return (
        med.name.toLowerCase().includes(term) ||
        med.activeIngredient.toLowerCase().includes(term)
      );
    });
  }, [searchTerm, activeCategory]);

  // Autocomplete suggestions (top 8)
  const searchSuggestions = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term || term.length < 2) return [];
    return UNIFIED_MEDICATIONS.filter(med =>
      med.name.toLowerCase().includes(term) ||
      med.activeIngredient.toLowerCase().includes(term)
    ).slice(0, 8);
  }, [searchTerm]);

  // Select medication from database into the composer form
  const handleSelectMedication = (med: UnifiedMedication) => {
    setSelectedMedName(med.name);
    setSelectedRoute(med.route);
    setSelectedQuantity(med.defaultQuantity);
    setSelectedPosology(med.defaultPosology);
    setSelectedIsSpecial(Boolean(med.isSpecialControl));
    setSearchTerm('');
    setShowSuggestions(false);
  };

  // Select by quick pill
  const handleSelectByQuery = (query: string) => {
    const found = UNIFIED_MEDICATIONS.find(m => m.name.toLowerCase().includes(query.toLowerCase()));
    if (found) {
      handleSelectMedication(found);
    } else {
      setSelectedMedName(query);
    }
  };

  // Add Item to Prescription
  const handleAddMedicationToPrescription = () => {
    if (!selectedMedName.trim()) {
      alert('Por favor, selecione ou digite o nome do medicamento.');
      return;
    }
    if (!selectedPosology.trim()) {
      alert('Por favor, informe a posologia / instruções de uso.');
      return;
    }

    const newItem: PrescriptionItem = {
      id: `item-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      name: selectedMedName.trim(),
      presentation: selectedQuantity || 'Uso oral',
      route: selectedRoute,
      quantity: selectedQuantity.trim() || '1 unidade',
      doseCalculatedText: '',
      frequencyText: selectedPosology.trim(),
      scheduleInterval: '8/8h',
      scheduleTimes: generateScheduleTimes('8/8h'),
      instructions: selectedPosology.trim(),
      isContinuous: selectedPosology.toLowerCase().includes('contínuo'),
      isSpecialControl: selectedIsSpecial
    };

    onUpdateItems([...items, newItem]);
    setItemAddedToast(true);
    setTimeout(() => setItemAddedToast(false), 2000);

    // Reset fields for next entry
    setSelectedMedName('');
    setSelectedQuantity('1 caixa');
    setSelectedPosology('');
    setSelectedIsSpecial(false);
  };

  // Pediatric Quick Calculator Calculation
  const handleCalculatePedia = (drugKey: string) => {
    setSelectedPediaDrugKey(drugKey);
    const weight = patientWeight;

    if (!weight || weight <= 0) {
      setCalculatedPediaResult(null);
      return;
    }

    if (drugKey === 'dipirona_gotas') {
      let drops = Math.round(weight * 1);
      if (drops > 40) drops = 40;
      setCalculatedPediaResult({
        name: 'Dipirona Sódica 500mg/mL gotas (Novalgina)',
        route: 'Uso Oral',
        quantity: '1 frasco (20 mL)',
        instructions: `Administrar ${drops} gotas via oral de 6 em 6 horas em caso de dor ou febre (Temp >= 37,8°C).`,
        calculatedDrops: drops,
        doseMg: drops * 25
      });
    } else if (drugKey === 'paracetamol_gotas') {
      let drops = Math.round(weight * 1);
      if (drops > 35) drops = 35;
      setCalculatedPediaResult({
        name: 'Paracetamol 200mg/mL gotas (Tylenol)',
        route: 'Uso Oral',
        quantity: '1 frasco (15 mL)',
        instructions: `Administrar ${drops} gotas via oral de 6 em 6 horas em caso de febre ou dor.`,
        calculatedDrops: drops,
        doseMg: drops * 10
      });
    } else if (drugKey === 'ibuprofeno_100') {
      let drops = Math.round(weight * 1);
      if (drops > 30) drops = 30;
      setCalculatedPediaResult({
        name: 'Ibuprofeno 100mg/mL gotas (Alivium 100)',
        route: 'Uso Oral',
        quantity: '1 frasco (20 mL)',
        instructions: `Administrar ${drops} gotas via oral de 8 em 8 horas por 3 dias em caso de dor ou febre.`,
        calculatedDrops: drops,
        doseMg: drops * 5
      });
    } else if (drugKey === 'amoxicilina_susp') {
      let mlPerDose = parseFloat(((weight * 50) / 3 / 50).toFixed(1));
      setCalculatedPediaResult({
        name: 'Amoxicilina 250mg/5mL suspensão oral (Amoxil)',
        route: 'Uso Oral',
        quantity: '2 frascos (150 mL)',
        instructions: `Administrar ${mlPerDose} mL via oral de 8 em 8 horas durante 10 dias seguidos.`,
        calculatedMl: mlPerDose,
        doseMg: mlPerDose * 50
      });
    } else if (drugKey === 'prednisolona_sol') {
      let mlPerDose = parseFloat((weight / 3).toFixed(1));
      setCalculatedPediaResult({
        name: 'Prednisolona 3mg/mL solução oral (Prelone, Predsim)',
        route: 'Uso Oral',
        quantity: '1 frasco (60 mL)',
        instructions: `Administrar ${mlPerDose} mL via oral 1 vez ao dia pela manhã por 3 a 5 dias.`,
        calculatedMl: mlPerDose,
        doseMg: weight
      });
    } else if (drugKey === 'azitromicina_susp') {
      let mlPerDose = parseFloat(((weight * 10) / 40).toFixed(1));
      setCalculatedPediaResult({
        name: 'Azitromicina 200mg/5mL suspensão oral (Astro, Zitromax)',
        route: 'Uso Oral',
        quantity: '1 frasco (600 mg)',
        instructions: `Administrar ${mlPerDose} mL via oral 1 vez ao dia durante 5 dias consecutivos.`,
        calculatedMl: mlPerDose,
        doseMg: weight * 10
      });
    } else if (drugKey === 'cefalexina_susp') {
      let mlPerDose = parseFloat(((weight * 50) / 4 / 50).toFixed(1));
      setCalculatedPediaResult({
        name: 'Cefalexina 250mg/5mL suspensão oral (Keflex)',
        route: 'Uso Oral',
        quantity: '2 frascos (100 mL)',
        instructions: `Administrar ${mlPerDose} mL via oral de 6 em 6 horas durante 7 a 10 dias.`,
        calculatedMl: mlPerDose,
        doseMg: mlPerDose * 50
      });
    } else if (drugKey === 'sulfametoxazol_susp') {
      let mlPerDose = parseFloat(((weight * 40) / 2 / 40).toFixed(1));
      setCalculatedPediaResult({
        name: 'Sulfametoxazol + Trimetoprima 200+40mg/5mL suspensão (Bactrim)',
        route: 'Uso Oral',
        quantity: '1 frasco (100 mL)',
        instructions: `Administrar ${mlPerDose} mL via oral de 12 em 12 horas por 7 a 10 dias.`,
        calculatedMl: mlPerDose,
        doseMg: weight * 20
      });
    }
  };

  // Recalculate if weight changes
  useEffect(() => {
    if (selectedPediaDrugKey) {
      handleCalculatePedia(selectedPediaDrugKey);
    }
  }, [patientWeight]);

  // Insert pediatric calculated dose into the prescription
  const handleApplyPediaDose = () => {
    if (!calculatedPediaResult) return;
    const newItem: PrescriptionItem = {
      id: `item-pedia-${Date.now()}`,
      name: calculatedPediaResult.name,
      presentation: calculatedPediaResult.quantity,
      route: calculatedPediaResult.route,
      quantity: calculatedPediaResult.quantity,
      doseCalculatedText: calculatedPediaResult.calculatedDrops
        ? `${calculatedPediaResult.calculatedDrops} gotas`
        : `${calculatedPediaResult.calculatedMl} mL`,
      frequencyText: calculatedPediaResult.instructions,
      scheduleInterval: '6/6h',
      scheduleTimes: generateScheduleTimes('6/6h'),
      instructions: calculatedPediaResult.instructions,
      isContinuous: false,
      calculatedFromWeight: patientWeight
    };

    onUpdateItems([...items, newItem]);
    setItemAddedToast(true);
    setTimeout(() => setItemAddedToast(false), 2000);
  };

  // Remove item
  const handleRemoveItem = (id: string) => {
    onUpdateItems(items.filter(i => i.id !== id));
  };

  // Move item up/down
  const handleMoveItem = (index: number, direction: 'up' | 'down') => {
    const newItems = [...items];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= newItems.length) return;
    const temp = newItems[index];
    newItems[index] = newItems[targetIndex];
    newItems[targetIndex] = temp;
    onUpdateItems(newItems);
  };

  // Copy prescription text
  const handleCopyText = () => {
    if (items.length === 0) return;
    const text = items.map((it, idx) => `${idx + 1}. ${it.name} (${it.route})\n   Qtd: ${it.quantity}\n   Posologia: ${it.instructions}\n`).join('\n');
    navigator.clipboard.writeText(text);
    setCopiedSuccess(true);
    setTimeout(() => setCopiedSuccess(false), 2000);
  };

  // Format prescription for WhatsApp
  const formatPrescriptionForWhatsApp = () => {
    if (items.length === 0) return '';
    const doctorLine = doctor?.name?.trim()
      ? `👨‍⚕️ *${doctor.name.trim()}* — CRM ${doctor.crm || '------'}/${doctor.crmState || 'SP'}\n`
      : '👨‍⚕️ *Receituário Médico*\n';
    const patientLine = patient?.name?.trim()
      ? `👤 *Paciente:* ${patient.name.trim()}${patient?.weightKg && patient.weightKg > 0 ? ` (${patient.weightKg} kg)` : ''}\n`
      : '';
    const dateLine = `📅 *Data:* ${new Date().toLocaleDateString('pt-BR')}\n`;

    let text = `📋 *RECEITUÁRIO MÉDICO DIGITAL*\n${doctorLine}${patientLine}${dateLine}------------------------------------\n`;

    items.forEach((it, idx) => {
      text += `\n*${idx + 1}. ${it.name}* (${it.route})\n   📦 *Qtd:* ${it.quantity}\n   👉 *Posologia:* ${it.instructions}\n`;
    });

    text += `\n------------------------------------\n⚠️ _Documento de orientação terapêutica emitido pelo médico. Siga as orientações e horários informados._`;
    return text;
  };

  // Open WhatsApp with formatted prescription
  const handleSendWhatsApp = () => {
    const text = formatPrescriptionForWhatsApp();
    if (!text) {
      alert('Adicione pelo menos um medicamento à receita antes de enviar.');
      return;
    }
    const encoded = encodeURIComponent(text);
    window.open(`https://api.whatsapp.com/send?text=${encoded}`, '_blank');
  };

  // Apply a full clinical kit with 1 click
  const handleApplyClinicalKit = (kit: typeof clinicalKits[0]) => {
    const newPrescriptionItems: PrescriptionItem[] = kit.items.map((kitItem, idx) => {
      let itemName = kitItem.name;
      let itemPresentation = kitItem.quantity;
      let itemInstructions = kitItem.instructions;
      let itemDoseCalculatedText = '';

      if (hasWeight && kitItem.pediaDrugKey) {
        if (kitItem.pediaDrugKey === 'dipirona_gotas') {
          const drops = Math.min(Math.round(patientWeight), 40);
          itemName = 'Dipirona Sódica 500mg/mL gotas (Novalgina)';
          itemPresentation = '1 frasco (20 mL)';
          itemInstructions = `Administrar ${drops} gotas via oral de 6 em 6 horas se dor ou febre (máx 4x ao dia).`;
          itemDoseCalculatedText = `${drops} gotas`;
        } else if (kitItem.pediaDrugKey === 'paracetamol_gotas') {
          const drops = Math.min(Math.round(patientWeight), 35);
          itemName = 'Paracetamol 200mg/mL gotas (Tylenol Bebê/Criança)';
          itemPresentation = '1 frasco (15 mL)';
          itemInstructions = `Administrar ${drops} gotas via oral de 6 em 6 horas se dor ou febre.`;
          itemDoseCalculatedText = `${drops} gotas`;
        } else if (kitItem.pediaDrugKey === 'ibuprofeno_100') {
          const drops = Math.min(Math.round(patientWeight), 40);
          itemName = 'Ibuprofeno 100mg/mL suspensão gotas (Alivium)';
          itemPresentation = '1 frasco (20 mL)';
          itemInstructions = `Administrar ${drops} gotas via oral de 8 em 8 horas após as refeições por 3 dias.`;
          itemDoseCalculatedText = `${drops} gotas`;
        } else if (kitItem.pediaDrugKey === 'amoxicilina_susp') {
          const mlPerDose = parseFloat(((patientWeight * 50) / 3 / 50).toFixed(1));
          itemName = 'Amoxicilina 250mg/5mL pó para suspensão oral (Amoxil)';
          itemPresentation = '1 frasco (150 mL)';
          itemInstructions = `Administrar ${mlPerDose} mL via oral de 8 em 8 horas durante 10 dias consecutivos.`;
          itemDoseCalculatedText = `${mlPerDose} mL`;
        } else if (kitItem.pediaDrugKey === 'prednisolona_sol') {
          const mlPerDose = parseFloat(((patientWeight * 1) / 3).toFixed(1));
          itemName = 'Fosfato Sódico de Prednisolona 3mg/mL solução oral (Prelone)';
          itemPresentation = '1 frasco (60 mL)';
          itemInstructions = `Administrar ${mlPerDose} mL via oral 1 vez ao dia, pela manhã, por 5 dias.`;
          itemDoseCalculatedText = `${mlPerDose} mL`;
        }
      }

      return {
        id: `kit-item-${Date.now()}-${idx}-${Math.random().toString(36).substr(2, 4)}`,
        name: itemName,
        presentation: itemPresentation,
        route: kitItem.route,
        quantity: itemPresentation,
        doseCalculatedText: itemDoseCalculatedText,
        frequencyText: itemInstructions,
        scheduleInterval: '8/8h',
        scheduleTimes: generateScheduleTimes('8/8h'),
        instructions: itemInstructions,
        isContinuous: false,
        isSpecialControl: Boolean((kitItem as any).isSpecial),
        calculatedFromWeight: hasWeight ? patientWeight : undefined
      };
    });

    onUpdateItems([...items, ...newPrescriptionItems]);
    setItemAddedToast(true);
    setTimeout(() => setItemAddedToast(false), 2500);
  };

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6 pb-20">
      
      {/* Top Mobile View Switcher */}
      <div className="flex md:hidden items-center justify-between p-1 rounded-xl bg-slate-200 dark:bg-navy-900 border border-slate-300 dark:border-navy-700">
        <button
          onClick={() => setMobileSection('composer')}
          className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
            mobileSection === 'composer'
              ? 'bg-navy-800 text-white shadow-tactile-btn'
              : 'text-slate-600 dark:text-slate-400'
          }`}
        >
          Prescrever Medicamentos
        </button>
        <button
          onClick={() => setMobileSection('preview')}
          className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
            mobileSection === 'preview'
              ? 'bg-navy-800 text-white shadow-tactile-btn'
              : 'text-slate-600 dark:text-slate-400'
          }`}
        >
          Visualizar Receita ({items.length})
        </button>
      </div>

      {/* Main Grid: Left Controls & Right A4 Simulation */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        
        {/* LEFT COLUMN: Composer, Calculator, Search and Quick Picks */}
        <div className={`xl:col-span-7 space-y-5 ${mobileSection === 'preview' ? 'hidden md:block' : 'block'}`}>
          
          {/* Card 1: Busca Rápida de Medicamentos (370+ RENAME / SUS / Referência) - TOPO PRIORITÁRIO */}
          <section className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-700 shadow-tactile dark:shadow-tactile-navy space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-navy-800 text-cream-50 dark:bg-navy-700 dark:text-cream-50 flex items-center justify-center font-bold border border-slate-200 dark:border-navy-600 shrink-0">
                  <Search className="w-4 h-4 text-amber-400" strokeWidth={1.75} />
                </div>
                <div>
                  <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-900 dark:text-cream-50">
                    Prescrição Rápida de Medicamentos
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                    Catálogo com 370+ fármacos do SUS, RENAME e Referência (Adulto & Pediátrico)
                  </p>
                </div>
              </div>
            </div>

            {/* Category Filter Chips */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1.5 custom-scrollbar fade-scroll-x">
              {[
                { id: 'all', label: 'Todos' },
                { id: 'analgesicos', label: 'Sintomáticos & AINEs' },
                { id: 'antibioticos', label: 'Antibióticos' },
                { id: 'cardio', label: 'Cardio & HAS' },
                { id: 'diabetes', label: 'Diabetes & Endócrino' },
                { id: 'respiratorio', label: 'Respiratório' },
                { id: 'gastro', label: 'Gastroenterologia' },
                { id: 'snc', label: 'SNC & Psiquiatria' }
              ].map(cat => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 transition active:scale-95 cursor-pointer shadow-tactile-sm ${
                    activeCategory === cat.id
                      ? 'bg-navy-800 dark:bg-navy-700 text-white'
                      : 'bg-slate-100 dark:bg-navy-800 hover:bg-slate-200 dark:hover:bg-navy-700 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Search Input with Instant Autocomplete */}
            <div className="relative">
              <label htmlFor="med-search-input" className="flex items-center gap-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                <span className="w-4 h-4 rounded-full bg-navy-800 dark:bg-cream-100 text-white dark:text-navy-950 text-[9px] font-black flex items-center justify-center shrink-0">1</span>
                Buscar Fármaco, Princípio Ativo ou Nome Comercial
              </label>
              <div className="relative">
                <input
                  id="med-search-input"
                  type="text"
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setShowSuggestions(true);
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  placeholder="Ex: Dipirona (Novalgina), Losartana, Amoxicilina, Omeprazol, Sertralina..."
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-300 dark:border-navy-700 text-sm font-semibold focus:ring-2 focus:ring-sky-500 outline-none text-slate-900 dark:text-slate-100"
                />
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                {searchTerm && (
                  <button
                    type="button"
                    onClick={() => setSearchTerm('')}
                    className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-200 cursor-pointer"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Suggestions Dropdown (Instant, No Blocker) */}
              {showSuggestions && searchSuggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 max-h-64 overflow-y-auto rounded-xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-700 shadow-tactile-navy z-30 divide-y divide-slate-100 dark:divide-navy-800">
                  {searchSuggestions.map(med => (
                    <div
                      key={med.id}
                      onClick={() => handleSelectMedication(med)}
                      className="p-3 hover:bg-sky-50 dark:hover:bg-navy-800 cursor-pointer flex items-center justify-between gap-2 transition"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-bold text-slate-900 dark:text-cream-50 truncate">
                          {med.name}
                        </p>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                          {med.defaultPosology}
                        </p>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded-md font-bold bg-slate-100 dark:bg-navy-800 text-sky-600 dark:text-sky-400 shrink-0">
                        {med.route}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Pills (1-Click Shortcuts) */}
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 mr-1">
                Atalhos Rápidos:
              </span>
              {quickMedChips.map((chip, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectByQuery(chip.query)}
                  className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-navy-800 hover:bg-sky-50 dark:hover:bg-sky-950/40 hover:border-sky-500/40 border border-slate-200 dark:border-navy-700 text-xs font-semibold text-slate-700 dark:text-slate-300 transition active:scale-95 cursor-pointer"
                >
                  {chip.label}
                </button>
              ))}
            </div>

            {/* Form de Edição e Adição Direta */}
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-navy-800 space-y-3">
              <div>
                <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  <span className="w-4 h-4 rounded-full bg-navy-800 dark:bg-cream-100 text-white dark:text-navy-950 text-[9px] font-black flex items-center justify-center shrink-0">2</span>
                  Confirme o Medicamento *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={selectedMedName}
                    onChange={(e) => setSelectedMedName(e.target.value)}
                    placeholder="Preenchido ao escolher acima — ou digite livremente aqui"
                    className={`w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-navy-900 border text-sm font-bold text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-amber-500/50 outline-none transition-colors ${
                      selectedMedName.trim()
                        ? 'border-emerald-400 dark:border-emerald-500/60'
                        : 'border-slate-300 dark:border-navy-700'
                    }`}
                  />
                  {selectedMedName.trim() && (
                    <Check className="w-4 h-4 text-emerald-500 absolute right-3.5 top-1/2 -translate-y-1/2" strokeWidth={2.5} />
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-12 gap-2.5">
                <div className="sm:col-span-4">
                  <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                    Via de Administração
                  </label>
                  <select
                    value={selectedRoute}
                    onChange={(e) => setSelectedRoute(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white dark:bg-navy-900 border border-slate-300 dark:border-navy-700 text-xs font-semibold outline-none text-slate-900 dark:text-slate-100"
                  >
                    <option value="Uso Oral">Uso Oral</option>
                    <option value="Uso Tópico">Uso Tópico</option>
                    <option value="Uso Inalatória">Uso Inalatória</option>
                    <option value="Uso Nasal">Uso Nasal</option>
                    <option value="Uso Oftálmico">Uso Oftálmico</option>
                    <option value="Uso Otológico">Uso Otológico</option>
                    <option value="Uso Retal">Uso Retal</option>
                    <option value="Uso Sublingual">Uso Sublingual</option>
                    <option value="Uso Intramuscular">Uso Intramuscular</option>
                    <option value="Uso Intravenoso">Uso Intravenoso</option>
                    <option value="Uso Subcutâneo">Uso Subcutâneo</option>
                  </select>
                </div>

                <div className="sm:col-span-4">
                  <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                    Quantidade / Apresentação
                  </label>
                  <input
                    type="text"
                    value={selectedQuantity}
                    onChange={(e) => setSelectedQuantity(e.target.value)}
                    placeholder="Ex: 1 caixa, 2 frascos"
                    className="w-full px-3 py-2 rounded-xl bg-white dark:bg-navy-900 border border-slate-300 dark:border-navy-700 text-xs font-semibold outline-none text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div className="sm:col-span-4 flex items-center pt-5">
                  <label className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedIsSpecial}
                      onChange={(e) => setSelectedIsSpecial(e.target.checked)}
                      className="w-4 h-4 rounded text-amber-600 focus:ring-amber-500"
                    />
                    <span>Receita de Controle Especial</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                  Instruções de Uso / Posologia *
                </label>
                <textarea
                  rows={2}
                  value={selectedPosology}
                  onChange={(e) => setSelectedPosology(e.target.value)}
                  placeholder="Ex: Tomar 1 comprimido via oral de 8 em 8 horas após as refeições por 5 dias..."
                  className="w-full px-3 py-2 rounded-xl bg-white dark:bg-navy-900 border border-slate-300 dark:border-navy-700 text-xs font-medium outline-none text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-amber-500/50"
                />
              </div>

              {/* Posology Shortcuts */}
              <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                <span className="text-[10px] font-bold text-slate-400 mr-1">Atalhos de Posologia:</span>
                {posologyShortcuts.map((ps, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setSelectedPosology(ps.text)}
                    className="px-2 py-0.5 rounded-lg bg-slate-200 dark:bg-navy-800 hover:bg-cream-200 dark:hover:bg-navy-700 text-[11px] font-semibold text-slate-700 dark:text-slate-300 transition active:scale-95 cursor-pointer shadow-tactile-sm"
                  >
                    {ps.label}
                  </button>
                ))}
              </div>

              {/* Add Button */}
              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={handleAddMedicationToPrescription}
                  className="btn-tactile-primary w-full sm:w-auto min-h-[44px] px-6 py-2.5 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition active:scale-95 cursor-pointer"
                >
                  <Plus className="w-4 h-4" strokeWidth={2} />
                  <span>Adicionar à Receita</span>
                </button>
              </div>
            </div>
          </section>

          {/* Card 2: Kits Rápidos de Plantão & Visita Domiciliar (Com Toggle Recolhível) */}
          <section className="rounded-2xl bg-white dark:bg-navy-900 border border-cream-300/80 dark:border-navy-700 shadow-tactile dark:shadow-tactile-navy overflow-hidden transition-all">
            {/* Header Accordion Bar */}
            <div 
              onClick={toggleKits}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleKits();
                }
              }}
              role="button"
              tabIndex={0}
              aria-expanded={showKits}
              className="p-4 sm:p-5 flex items-center justify-between cursor-pointer select-none hover:bg-slate-50 dark:hover:bg-navy-800/60 transition-colors focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-navy-900/10 dark:bg-cream-100/15 text-navy-900 dark:text-cream-100 flex items-center justify-center font-bold border border-navy-900/20 dark:border-cream-100/25 shrink-0">
                  <Sparkles className="w-4 h-4" strokeWidth={1.75} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-navy-900 dark:text-cream-50">
                      Kits Rápidos de Plantão & Visita Domiciliar
                    </h3>
                    <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-md bg-navy-900/10 text-navy-900 dark:bg-cream-100/15 dark:text-cream-100 border border-navy-900/20 dark:border-cream-100/25">
                      {clinicalKits.length} Kits
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                    {showKits 
                      ? 'Carregue o combo terapêutico completo em 1 clique (combos pré-calculados)' 
                      : 'Clique para expandir e selecionar combos de prescrição rápida'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 hidden sm:inline">
                  {showKits ? 'Recolher' : 'Expandir'}
                </span>
                <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-navy-800 flex items-center justify-center text-slate-500 dark:text-slate-300 transition-transform duration-200">
                  {showKits ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </div>
            </div>

            {/* Kits Content (Visible when expanded) */}
            {showKits && (
              <div className="p-4 sm:p-5 pt-0 sm:pt-0 border-t border-slate-100 dark:border-navy-800 animate-tab-fade">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-3">
                  {clinicalKits.map(kit => (
                    <button
                      key={kit.id}
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleApplyClinicalKit(kit);
                      }}
                      className="p-3 rounded-xl border bg-slate-50 dark:bg-navy-800 hover:border-navy-800/50 dark:hover:border-cream-100/50 border-slate-200 dark:border-navy-700 text-left transition active:scale-95 cursor-pointer shadow-tactile-sm group flex flex-col justify-between"
                      title="Clique para adicionar todo o combo de medicamentos à receita"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-1 mb-1">
                          <span className="text-xs font-bold text-navy-900 dark:text-cream-50 truncate group-hover:text-navy-700 dark:group-hover:text-cream-200">
                            {kit.name}
                          </span>
                          <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-navy-900/10 text-navy-900 dark:bg-cream-100/15 dark:text-cream-100 shrink-0">
                            {kit.items.length} fármacos
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-2">
                          {kit.description}
                        </p>
                      </div>
                      <div className="mt-2 pt-1.5 border-t border-slate-200 dark:border-navy-700/60 flex items-center justify-between text-[10px] font-bold text-navy-900 dark:text-cream-100">
                        <span>{kit.badge}</span>
                        <span className="group-hover:translate-x-0.5 transition-transform">Inserir Kit +</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Card 3: Assistente de Doses Pediátricas Inteligente (Gotas / mL - Com Toggle Recolhível) */}
          <section className="rounded-2xl border transition-all bg-white dark:bg-navy-900 border-cream-300/80 dark:border-navy-700 shadow-tactile dark:shadow-tactile-navy overflow-hidden">
            {/* Header Accordion Bar */}
            <div 
              onClick={togglePediaCalc}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  togglePediaCalc();
                }
              }}
              role="button"
              tabIndex={0}
              aria-expanded={showPediaCalc}
              className="p-4 sm:p-5 flex items-center justify-between cursor-pointer select-none hover:bg-slate-50 dark:hover:bg-navy-800/60 transition-colors focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-navy-900/10 dark:bg-cream-100/15 text-navy-900 dark:text-cream-100 flex items-center justify-center font-bold border border-navy-900/20 dark:border-cream-100/25 shrink-0">
                  <Calculator className="w-4 h-4" strokeWidth={1.75} />
                </div>
                <div>
                  <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-navy-900 dark:text-cream-50">
                    Calculadora Pediátrica Rápida (Gotas / mL)
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                    {hasWeight 
                      ? `Cálculo automático ajustado para ${patientWeight} kg` 
                      : 'Informe o peso do paciente para cálculo instantâneo'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                {/* Weight Indicator Button */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenPatientModal();
                  }}
                  className="px-3 py-1.5 rounded-xl bg-navy-900/10 hover:bg-navy-900/20 dark:bg-cream-100/15 dark:hover:bg-cream-100/25 border border-navy-900/20 dark:border-cream-100/25 text-navy-900 dark:text-cream-100 text-xs font-bold flex items-center gap-1.5 transition active:scale-95 cursor-pointer shadow-tactile-sm"
                  title="Clique para alterar o peso do paciente"
                >
                  <Scale className="w-3.5 h-3.5" strokeWidth={1.75} />
                  <span>{hasWeight ? `${patientWeight} kg` : 'Definir Peso'}</span>
                </button>

                <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-navy-800 flex items-center justify-center text-slate-500 dark:text-slate-300">
                  {showPediaCalc ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </div>
            </div>

            {/* Pedia Content (Visible when expanded) */}
            {showPediaCalc && (
              <div className="p-4 sm:p-5 pt-0 sm:pt-0 border-t border-slate-100 dark:border-navy-800 animate-tab-fade space-y-3">
                {/* Quick Pediatric Drug Buttons */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 mb-1">
                  {[
                    { id: 'dipirona_gotas', name: 'Dipirona Gotas', sub: '500mg/mL (1 gts/kg)' },
                    { id: 'paracetamol_gotas', name: 'Paracetamol Gotas', sub: '200mg/mL (1 gts/kg)' },
                    { id: 'ibuprofeno_100', name: 'Ibuprofeno 100mg/mL', sub: 'Gotas (1 gts/kg)' },
                    { id: 'amoxicilina_susp', name: 'Amox 250mg/5mL', sub: '50mg/kg/dia 8/8h' },
                    { id: 'prednisolona_sol', name: 'Prednisolona 3mg/mL', sub: '1mg/kg/dia pela manhã' },
                    { id: 'azitromicina_susp', name: 'Azitro 200mg/5mL', sub: '10mg/kg/dia (5 dias)' },
                    { id: 'cefalexina_susp', name: 'Cefalexina 250mg/5mL', sub: '50mg/kg/dia 6/6h' },
                    { id: 'sulfametoxazol_susp', name: 'SMZ+TMP Suspensão', sub: '40+8mg/kg/dia 12/12h' }
                  ].map(drug => (
                    <button
                      key={drug.id}
                      type="button"
                      onClick={() => handleCalculatePedia(drug.id)}
                      className={`p-2.5 rounded-xl border text-left transition-all active:scale-95 cursor-pointer shadow-tactile-sm ${
                        selectedPediaDrugKey === drug.id
                          ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 shadow-tactile-navy dark:shadow-tactile-cream border border-navy-800 dark:border-white/30 font-bold'
                          : 'bg-slate-50 dark:bg-navy-800 hover:border-navy-800/40 dark:hover:border-cream-200/40 border-slate-200 dark:border-navy-700 text-slate-800 dark:text-slate-100'
                      }`}
                    >
                      <p className="text-xs font-bold truncate">{drug.name}</p>
                      <p className={`text-[10px] truncate ${selectedPediaDrugKey === drug.id ? 'text-cream-200 dark:text-navy-800 font-semibold' : 'text-slate-500 dark:text-slate-400'}`}>
                        {drug.sub}
                      </p>
                    </button>
                  ))}
                </div>

                {/* Dynamic Calculation Result Box */}
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-navy-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 shadow-tactile-inset">
                  <div className="space-y-0.5 min-w-0 flex-1">
                    {calculatedPediaResult ? (
                      <>
                        <p className="text-xs font-bold text-slate-900 dark:text-cream-50">
                          {calculatedPediaResult.name}
                        </p>
                        <p className="text-[11px] text-navy-900 dark:text-cream-100 font-semibold">
                          Dose para {patientWeight} kg: {calculatedPediaResult.calculatedDrops ? `${calculatedPediaResult.calculatedDrops} gotas` : `${calculatedPediaResult.calculatedMl} mL`}
                          <span className="text-slate-500 dark:text-slate-400 font-normal ml-1">
                            ({calculatedPediaResult.instructions})
                          </span>
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="text-xs font-bold text-slate-700 dark:text-slate-300">
                          {hasWeight
                            ? 'Selecione um medicamento pediátrico acima para cálculo instantâneo.'
                            : 'Informe o peso do paciente acima para ativar o cálculo de doses pediátricas.'}
                        </p>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Conversão automática em gotas ou volume em mL conforme protocolos pediátricos.
                        </p>
                      </>
                    )}
                  </div>

                  <button
                    type="button"
                    disabled={!calculatedPediaResult}
                    onClick={handleApplyPediaDose}
                    className="btn-tactile-primary px-4 py-2 rounded-xl disabled:opacity-40 disabled:cursor-not-allowed font-bold text-xs transition active:scale-95 shrink-0 flex items-center gap-1.5 cursor-pointer"
                  >
                    <Plus className="w-4 h-4" strokeWidth={2} />
                    <span>Inserir na Receita</span>
                  </button>
                </div>
              </div>
            )}
          </section>

          {/* Card 3: Lista de Medicamentos Prescritos na Receita */}
          <section className="p-5 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-700 shadow-tactile dark:shadow-tactile-navy space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 dark:text-cream-50">
                  Medicamentos Prescritos
                </h3>
                <span className="px-2 py-0.5 rounded-full text-xs font-extrabold bg-navy-800 dark:bg-navy-700 text-white">
                  {items.length}
                </span>
              </div>

              {items.length > 0 && (
                <button
                  type="button"
                  onClick={onClearPrescription}
                  className="text-xs font-semibold text-rose-500 hover:text-rose-600 flex items-center gap-1 cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" strokeWidth={1.75} />
                  <span>Limpar Receita</span>
                </button>
              )}
            </div>

            {items.length === 0 ? (
              <div className="p-8 text-center rounded-xl bg-slate-50 dark:bg-navy-950 border border-dashed border-slate-300 dark:border-navy-800 text-slate-400 text-xs italic">
                Nenhum medicamento adicionado ainda. Use a busca acima, clique nos atalhos ou utilize a calculadora pediátrica.
              </div>
            ) : (
              <div className="space-y-2.5">
                {items.map((it, idx) => (
                  <div
                    key={it.id}
                    className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-navy-800 flex items-start justify-between gap-3 shadow-tactile-sm"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="w-5 h-5 rounded-full bg-navy-800 dark:bg-navy-700 text-white text-[10px] font-black flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-cream-50 truncate">
                          {it.name}
                        </h4>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-200 dark:bg-navy-800 text-slate-700 dark:text-slate-300">
                          {it.route} • {it.quantity}
                        </span>
                        {it.isSpecialControl && (
                          <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                            Controle Especial
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-700 dark:text-slate-300 pl-7 leading-relaxed font-medium">
                        {it.instructions}
                      </p>
                    </div>

                    {/* Action buttons (Move Up, Move Down, Delete) */}
                    <div className="flex items-center gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => handleMoveItem(idx, 'up')}
                        disabled={idx === 0}
                        className="p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-navy-800 disabled:opacity-30 text-slate-500"
                        title="Mover para cima"
                      >
                        <ChevronUp className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleMoveItem(idx, 'down')}
                        disabled={idx === items.length - 1}
                        className="p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-navy-800 disabled:opacity-30 text-slate-500"
                        title="Mover para baixo"
                      >
                        <ChevronDown className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(it.id)}
                        className="p-1 rounded-lg hover:bg-rose-100 dark:hover:bg-rose-950/40 text-slate-400 hover:text-rose-500 transition"
                        title="Remover medicamento"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Quick Actions Footer */}
            {items.length > 0 && (
              <div className="pt-3 border-t border-slate-200 dark:border-navy-800 flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleSendWhatsApp}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-tactile-btn transition active:scale-95 cursor-pointer"
                    title="Enviar a receita completa diretamente para o WhatsApp do paciente"
                  >
                    <Send className="w-3.5 h-3.5" strokeWidth={2} />
                    <span>Enviar no WhatsApp</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleCopyText}
                    className="px-3.5 py-2 rounded-xl border border-slate-300 dark:border-navy-700 bg-white dark:bg-navy-800 hover:bg-slate-50 dark:hover:bg-navy-700 text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5 transition active:scale-95 cursor-pointer shadow-tactile-sm"
                  >
                    {copiedSuccess ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedSuccess ? 'Copiado!' : 'Copiar Texto'}</span>
                  </button>
                </div>

                <button
                  type="button"
                  onClick={onNavigateToPrint}
                  className="px-4 py-2 rounded-xl bg-navy-800 dark:bg-navy-700 hover:bg-navy-900 text-white text-xs font-bold shadow-tactile-btn flex items-center gap-2 transition active:scale-95 cursor-pointer"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Visualizar PDF A4</span>
                </button>
              </div>
            )}
          </section>
        </div>

        {/* RIGHT COLUMN: Real-Time A4 Document Simulation (Tactile Sheet) */}
        <div className={`xl:col-span-5 space-y-4 ${mobileSection === 'composer' ? 'hidden md:block' : 'block'}`}>
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300">
                Visualização em Tempo Real (A4)
              </h3>
            </div>
            <button
              type="button"
              onClick={onNavigateToPrint}
              className="text-xs font-bold text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>Abrir tela cheia</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Printable Simulated A4 Sheet */}
          <div className="prescription-sheet p-6 sm:p-7 rounded-2xl bg-white text-slate-900 border border-slate-300 shadow-tactile-lg min-h-[560px] flex flex-col justify-between text-left relative overflow-hidden transition-all">
            <div>
              {/* Document Header */}
              <div className="border-b-2 border-slate-900 pb-3 mb-4 text-center">
                <h2 className="text-base font-bold uppercase tracking-wide text-slate-900">
                  {doctor?.name || 'Dr. Médico Não Configurado'}
                </h2>
                <p className="text-xs font-semibold text-slate-700">
                  {doctor?.specialty || 'Clínica Médica'} • CRM {doctor?.crm ? `${doctor.crm}/${doctor?.crmState || 'SP'}` : 'Não informado'} {doctor?.rqe ? `• RQE ${doctor.rqe}` : ''}
                </p>
                {doctor?.clinicName && (
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {doctor.clinicName} {doctor?.address ? `• ${doctor.address}` : ''} {doctor?.phone ? `• Tel: ${doctor.phone}` : ''}
                  </p>
                )}
              </div>

              {/* Patient Info Bar */}
              <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 mb-4 flex flex-wrap justify-between items-center text-xs text-slate-800">
                <div>
                  <span className="font-bold text-slate-500">Paciente:</span>
                  <span className="font-bold text-slate-900 ml-1">
                    {patientName || 'Não identificado'}
                  </span>
                </div>
                <div className="flex gap-3 text-[11px] text-slate-600 font-medium">
                  {patient?.ageText && <span>Idade: {patient.ageText}</span>}
                  {hasWeight && <span className="font-bold text-emerald-700">Peso: {patientWeight} kg</span>}
                </div>
              </div>

              {/* Document Title */}
              <div className="text-center mb-4">
                <h3 className="serif-title text-sm font-bold uppercase tracking-widest text-slate-800 border-b border-slate-200 pb-1 inline-block">
                  Receituário Médico
                </h3>
              </div>

              {/* Prescription Body Items */}
              {items.length === 0 ? (
                <div className="py-16 text-center text-slate-400 italic text-xs">
                  Nenhum medicamento inserido na receita.
                </div>
              ) : (
                <div className="space-y-4 text-xs text-slate-800 leading-relaxed">
                  {items.map((it, idx) => (
                    <div key={it.id} className="mb-3">
                      <div className="flex justify-between items-baseline font-bold text-slate-900">
                        <span>{idx + 1}. {it.name} ({it.route})</span>
                        <span className="text-[11px] font-semibold text-slate-600">{it.quantity}</span>
                      </div>
                      <p className="text-slate-700 pl-4 mt-0.5 leading-relaxed">
                        {it.instructions}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Document Footer (Date, Place & Signature Line) */}
            <div className="pt-6 mt-6 border-t border-slate-200 text-center space-y-3">
              <p className="text-[11px] text-slate-600">
                {doctor?.cityState || 'Brasil'}, {new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' })}
              </p>
              
              {doctor?.showSignature !== false && (
                <div className="pt-3 max-w-[240px] mx-auto border-t border-dashed border-slate-400">
                  <p className="text-xs font-bold text-slate-900">
                    {doctor?.name || 'Dr(a). Médico(a)'}
                  </p>
                  <p className="text-[10px] text-slate-600">
                    CRM: {doctor?.crm ? `${doctor.crm}/${doctor?.crmState || 'SP'}` : '------'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              type="button"
              onClick={onNavigateToPrint}
              className="btn-tactile-primary w-full py-2.5 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition active:scale-95 cursor-pointer"
            >
              <Printer className="w-4 h-4" />
              <span>Imprimir / PDF A4</span>
            </button>

            <button
              type="button"
              onClick={handleSendWhatsApp}
              disabled={items.length === 0}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-tactile-btn transition active:scale-95 cursor-pointer"
            >
              <Send className="w-4 h-4" strokeWidth={2} />
              <span>Enviar no WhatsApp</span>
            </button>
          </div>
        </div>

      </div>

      {/* Item Added Toast Alert */}
      {itemAddedToast && (
        <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-emerald-600 text-white text-xs font-bold flex items-center gap-2 shadow-tactile-lg animate-in fade-in slide-in-from-bottom-3 duration-200">
          <Check className="w-4 h-4" />
          <span>Medicamento inserido na receita com sucesso!</span>
        </div>
      )}

    </div>
  );
};
