import React, { useState, useEffect, useMemo } from 'react';
import {
  X,
  Pill,
  Check,
  Scale,
  Plus,
  AlertTriangle,
  Clock,
  Sparkles,
  Info,
  Search,
  ArrowLeftRight
} from 'lucide-react';
import { Patient, PrescriptionItem, PediatricMedication } from '../types';
import { BaseMedicationGroup, MedicationOption } from '../utils/medicationCatalog';
import { calculatePediatricDose, generateScheduleTimes } from '../utils/doseCalculator';
import { normalizeText, calculateStringSimilarity } from '../utils/fuzzySearch';

interface MedicationPresentationModalProps {
  isOpen: boolean;
  onClose: () => void;
  medicationGroup: BaseMedicationGroup | null;
  patient: Patient;
  onOpenPatientModal?: () => void;
  onOpenMedicationSearchModal?: () => void;
  onChangeMedicationGroup?: (group: BaseMedicationGroup) => void;
  onConfirmAdd: (item: PrescriptionItem) => void;
  darkMode: boolean;
}

export const MedicationPresentationModal: React.FC<MedicationPresentationModalProps> = ({
  isOpen,
  onClose,
  medicationGroup,
  patient,
  onOpenPatientModal,
  onOpenMedicationSearchModal,
  onChangeMedicationGroup,
  onConfirmAdd,
  darkMode
}) => {
  const patientWeight = patient?.weightKg ?? 0;
  const hasWeight = patientWeight > 0;
  const patientName = patient?.name || 'Paciente sem nome';

  // Sub-filtro interno das apresentações (se tiver adulto e pediátrico)
  const [activeTab, setActiveTab] = useState<'all' | 'adult' | 'pediatric'>('all');
  const [presentationSearch, setPresentationSearch] = useState('');

  // Apresentação selecionada dentro do modal
  const [selectedOption, setSelectedOption] = useState<MedicationOption | null>(null);

  // Campos do formulário de personalização
  const [customPosology, setCustomPosology] = useState('');
  const [customQuantity, setCustomQuantity] = useState('');
  const [customRoute, setCustomRoute] = useState('Oral');
  const [customFrequency, setCustomFrequency] = useState('8/8h');
  const [customDays, setCustomDays] = useState<number>(5);
  const [isSpecialControl, setIsSpecialControl] = useState(false);

  // Edição rápida de peso inline no modal
  const [inlineWeight, setInlineWeight] = useState<string>(hasWeight ? String(patientWeight) : '');
  const [showWeightEdit, setShowWeightEdit] = useState(false);

  // Efeito ao abrir o modal ou mudar o grupo selecionado
  useEffect(() => {
    if (isOpen && medicationGroup) {
      setPresentationSearch('');
      // Determina a aba padrão com base no perfil do paciente
      if (hasWeight && patientWeight <= 40 && medicationGroup.hasPediatric) {
        setActiveTab('pediatric');
      } else if (medicationGroup.hasAdult) {
        setActiveTab('all');
      } else {
        setActiveTab('all');
      }

      // Seleciona a primeira opção mais apropriada
      const initialOption = (hasWeight && patientWeight <= 40 && medicationGroup.hasPediatric)
        ? medicationGroup.options.find(o => o.isPediatric) || medicationGroup.options[0]
        : medicationGroup.options.find(o => !o.isPediatric) || medicationGroup.options[0];

      if (initialOption) {
        applyOption(initialOption, hasWeight ? patientWeight : Number(inlineWeight) || 0);
      }
    }
  }, [isOpen, medicationGroup, patientWeight, hasWeight]);

  // Tecla ESC para fechar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Aplica uma opção selecionada aos campos do formulário
  const applyOption = (opt: MedicationOption, currentWeight: number) => {
    setSelectedOption(opt);
    setCustomRoute(opt.route || 'Oral');
    setCustomFrequency(opt.defaultFrequency || '8/8h');
    setCustomQuantity(opt.defaultQuantity || (opt.isPediatric ? '1 frasco' : '1 caixa'));
    setCustomDays(opt.defaultDays || 5);
    setIsSpecialControl(opt.isSpecialControl);

    if (opt.isPediatric && opt.pediatricMed) {
      if (currentWeight > 0) {
        const calc = calculatePediatricDose(opt.pediatricMed, currentWeight);
        setCustomPosology(calc.instructionsText || calc.formattedPrescriptionText);
      } else {
        setCustomPosology(opt.posology || opt.observations || 'Uso pediátrico conforme orientação médica.');
      }
    } else {
      setCustomPosology(opt.posology);
    }
  };

  // Recalcula dose se o peso inline for alterado
  const handleInlineWeightChange = (newWeightStr: string) => {
    setInlineWeight(newWeightStr);
    const w = parseFloat(newWeightStr.replace(',', '.'));
    if (!isNaN(w) && w > 0 && selectedOption?.isPediatric && selectedOption.pediatricMed) {
      const calc = calculatePediatricDose(selectedOption.pediatricMed, w);
      setCustomPosology(calc.instructionsText || calc.formattedPrescriptionText);
    }
  };

  // Opções filtradas pela aba ativa e busca difusa interna de apresentações
  const filteredOptions = useMemo(() => {
    if (!medicationGroup) return [];
    let opts = medicationGroup.options;

    if (activeTab === 'adult') {
      opts = opts.filter(o => !o.isPediatric);
    } else if (activeTab === 'pediatric') {
      opts = opts.filter(o => o.isPediatric);
    }

    const q = normalizeText(presentationSearch);
    if (!q) return opts;

    return opts.filter(o => {
      const text = normalizeText(`${o.name} ${o.presentation} ${o.pharmaceuticalForm} ${o.concentration} ${o.route} ${o.posology}`);
      if (text.includes(q)) return true;
      const words = text.split(/\s+/);
      return words.some(w => calculateStringSimilarity(w, q) >= 0.7);
    });
  }, [medicationGroup, activeTab, presentationSearch]);


  // Confirma e adiciona a prescrição
  const handleConfirm = () => {
    if (!selectedOption || !medicationGroup) return;

    const currentW = hasWeight ? patientWeight : parseFloat(inlineWeight.replace(',', '.')) || undefined;
    const finalWeight = (selectedOption.isPediatric && currentW && currentW > 0) ? currentW : undefined;

    const item: PrescriptionItem = {
      id: `item-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      name: selectedOption.name,
      presentation: selectedOption.presentation,
      route: customRoute.trim() || 'Oral',
      quantity: customQuantity.trim() || (selectedOption.isPediatric ? '1 frasco' : '1 caixa'),
      doseCalculatedText: '',
      frequencyText: customPosology.trim(),
      scheduleInterval: customFrequency,
      scheduleTimes: generateScheduleTimes(customFrequency),
      durationDays: customDays > 0 ? customDays : undefined,
      instructions: customPosology.trim() || 'Tomar conforme orientação médica.',
      isContinuous: customFrequency === 'Uso Contínuo',
      isSpecialControl: isSpecialControl,
      calculatedFromWeight: finalWeight
    };

    onConfirmAdd(item);
    onClose();
  };

  // Adição direta em 1 toque de uma opção específica
  const handleQuickAddOption = (opt: MedicationOption, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!medicationGroup) return;

    const currentW = hasWeight ? patientWeight : parseFloat(inlineWeight.replace(',', '.')) || undefined;
    let posText = opt.posology;
    let finalWeight: number | undefined = undefined;

    if (opt.isPediatric && opt.pediatricMed && currentW && currentW > 0) {
      const calc = calculatePediatricDose(opt.pediatricMed, currentW);
      posText = calc.instructionsText || calc.formattedPrescriptionText;
      finalWeight = currentW;
    }

    const item: PrescriptionItem = {
      id: `item-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      name: opt.name,
      presentation: opt.presentation,
      route: opt.route || 'Oral',
      quantity: opt.defaultQuantity || (opt.isPediatric ? '1 frasco' : '1 caixa'),
      doseCalculatedText: '',
      frequencyText: posText,
      scheduleInterval: opt.defaultFrequency || '8/8h',
      scheduleTimes: generateScheduleTimes(opt.defaultFrequency || '8/8h'),
      durationDays: opt.defaultDays || 5,
      instructions: posText,
      isContinuous: opt.defaultFrequency === 'Uso Contínuo',
      isSpecialControl: opt.isSpecialControl,
      calculatedFromWeight: finalWeight
    };

    onConfirmAdd(item);
    onClose();
  };

  if (!isOpen || !medicationGroup) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-xs isolate animate-fadeIn">
      {/* Container do Painel/Modal */}
      <div
        className="w-full max-w-2xl max-h-[92vh] rounded-2xl border flex flex-col shadow-tactile-lg overflow-hidden"
        style={{
          backgroundColor: darkMode ? '#0E1420' : '#FFFFFF',
          borderColor: darkMode ? 'rgba(255,255,255,0.12)' : '#E3D7BD',
          boxShadow: darkMode ? '0 24px 50px -8px rgba(0,0,0,0.85), inset 0 1px 0 rgba(255,255,255,0.1)' : '0 20px 40px -8px rgba(20,32,50,0.18), inset 0 1px 0 rgba(255,255,255,0.95)'
        }}
      >
        {/* CABEÇALHO DO MODAL */}
        <div
          className="p-4 sm:p-5 border-b flex-shrink-0 relative space-y-3"
          style={{
            backgroundColor: darkMode ? '#141E2C' : '#F8F4EC',
            borderColor: darkMode ? 'rgba(255,255,255,0.08)' : '#E3D7BD'
          }}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 min-w-0">
              <div className="p-2.5 rounded-xl bg-navy-900/10 dark:bg-cream-100/15 text-navy-900 dark:text-cream-100 flex items-center justify-center flex-shrink-0 mt-0.5 font-bold">
                <Pill className="w-5 h-5" strokeWidth={2} />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-extrabold text-base sm:text-lg tracking-tight truncate text-navy-900 dark:text-cream-50">
                    {medicationGroup.baseName}
                  </h3>
                  {medicationGroup.isSpecialControl && (
                    <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/25">
                      Controle Especial
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium truncate mt-0.5">
                  {medicationGroup.activeIngredient} • <span className="font-bold text-sky-600 dark:text-sky-400">{medicationGroup.category}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 flex-shrink-0">
              {onOpenMedicationSearchModal && (
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    onOpenMedicationSearchModal();
                  }}
                  className="text-[11px] font-bold px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 bg-sky-500/10 hover:bg-sky-500/20 text-sky-600 dark:text-sky-300 border-sky-500/30 transition-all cursor-pointer"
                  title="Trocar medicamento usando busca inteligente"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Trocar Fármaco</span>
                </button>
              )}

              <button
                type="button"
                onClick={onClose}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-500/15 transition-colors cursor-pointer"
                title="Fechar (Esc)"
              >
                <X className="w-4 h-4" strokeWidth={2} />
              </button>
            </div>
          </div>

          {/* BARRA DO PACIENTE COM ATALHO DE PESO */}
          <div
            className="p-2.5 rounded-xl border flex items-center justify-between gap-2 flex-wrap text-xs font-semibold"
            style={{
              backgroundColor: darkMode ? '#182030' : '#F1F5F9',
              borderColor: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.06)'
            }}
          >
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-medium">Paciente:</span>
              <span className="font-bold" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                {patientName}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {hasWeight ? (
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25 font-bold text-[11px]">
                  <Scale className="w-3.5 h-3.5" strokeWidth={2} />
                  <span>{patientWeight} kg (Doses calculadas ativas)</span>
                </div>
              ) : (
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] text-amber-600 dark:text-amber-400 font-medium">Sem peso:</span>
                  {showWeightEdit ? (
                    <div className="flex items-center gap-1">
                      <input
                        type="text"
                        value={inlineWeight}
                        onChange={(e) => handleInlineWeightChange(e.target.value)}
                        placeholder="kg"
                        className="w-16 px-2 py-0.5 text-xs rounded border tactile-input font-bold"
                        autoFocus
                      />
                      <button
                        type="button"
                        onClick={() => setShowWeightEdit(false)}
                        className="text-[10px] px-2 py-0.5 bg-emerald-600 text-white rounded font-bold"
                      >
                        OK
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setShowWeightEdit(true)}
                      className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 hover:bg-amber-500/30 cursor-pointer transition-colors"
                    >
                      + Informar Peso
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* CONTROLES DE FILTRO E BUSCA DE APRESENTAÇÃO */}
          <div className="flex items-center justify-between gap-2 flex-wrap pt-0.5">
            {/* ABAS SE HOUVER OPÇÕES ADULTAS E PEDIÁTRICAS */}
            {medicationGroup.hasAdult && medicationGroup.hasPediatric ? (
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setActiveTab('all')}
                  className={`text-xs font-bold px-3 py-1.5 rounded-xl border transition-all cursor-pointer ${
                    activeTab === 'all'
                      ? 'bg-sky-600 text-white border-sky-500 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-slate-500/10'
                  }`}
                >
                  Todas ({medicationGroup.options.length})
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('adult')}
                  className={`text-xs font-bold px-3 py-1.5 rounded-xl border transition-all cursor-pointer ${
                    activeTab === 'adult'
                      ? 'bg-sky-600 text-white border-sky-500 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-slate-500/10'
                  }`}
                >
                  Adulto ({medicationGroup.options.filter(o => !o.isPediatric).length})
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('pediatric')}
                  className={`text-xs font-bold px-3 py-1.5 rounded-xl border transition-all cursor-pointer ${
                    activeTab === 'pediatric'
                      ? 'bg-emerald-600 text-white border-emerald-500 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-slate-500/10'
                  }`}
                >
                  Pediátrico ({medicationGroup.options.filter(o => o.isPediatric).length})
                </button>
              </div>
            ) : <div />}

            {/* BUSCA RÁPIDA DE APRESENTAÇÃO */}
            <div className="relative flex-1 min-w-[200px] max-w-xs ml-auto">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={presentationSearch}
                onChange={(e) => setPresentationSearch(e.target.value)}
                placeholder="Filtrar apresentações..."
                className="w-full pl-8 pr-7 py-1.5 text-xs rounded-xl border font-medium focus:outline-none focus:ring-1 focus:ring-sky-500/50"
                style={{
                  backgroundColor: darkMode ? '#182030' : '#FFFFFF',
                  borderColor: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.1)',
                  color: darkMode ? '#F1F5F9' : '#0F172A'
                }}
              />
              {presentationSearch && (
                <button
                  type="button"
                  onClick={() => setPresentationSearch('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* CORPO DO MODAL - ROLÁVEL */}
        <div className="p-4 sm:p-5 overflow-y-auto space-y-4 flex-1">
          {/* PASSO 1: SELEÇÃO DA APRESENTAÇÃO */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                1. Escolha a Apresentação & Concentração:
              </label>
              <span className="text-[11px] text-slate-400 font-semibold">
                {filteredOptions.length} {filteredOptions.length === 1 ? 'disponível' : 'disponíveis'}
              </span>
            </div>

            {filteredOptions.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-400 space-y-2 border border-dashed rounded-xl p-4">
                <p>Nenhuma apresentação encontrada para "{presentationSearch}".</p>
                <button
                  type="button"
                  onClick={() => setPresentationSearch('')}
                  className="text-xs text-sky-600 dark:text-sky-400 font-bold hover:underline"
                >
                  Limpar filtro de apresentações
                </button>
              </div>
            ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {filteredOptions.map((opt) => {
                const isSelected = selectedOption?.id === opt.id;
                return (
                  <div
                    key={opt.id}
                    onClick={() => applyOption(opt, hasWeight ? patientWeight : Number(inlineWeight) || 0)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col justify-between gap-2 relative group ${
                      isSelected
                        ? 'border-sky-500 bg-sky-500/10 ring-2 ring-sky-500/20 shadow-sm'
                        : darkMode
                        ? 'bg-slate-800/40 hover:bg-slate-800/80 border-slate-700/60'
                        : 'bg-slate-50 hover:bg-slate-100 border-slate-200'
                    }`}
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="font-bold text-xs sm:text-sm" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                          {opt.presentation}
                        </div>
                        {opt.isPediatric ? (
                          <span className="text-[9px] font-extrabold px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25 flex-shrink-0">
                            Pediátrico
                          </span>
                        ) : (
                          <span className="text-[9px] font-extrabold px-2 py-0.5 rounded bg-sky-500/15 text-sky-700 dark:text-sky-400 border border-sky-500/25 flex-shrink-0">
                            Adulto
                          </span>
                        )}
                      </div>

                      {/* Nome comercial ou forma farmacêutica */}
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5">
                        {opt.name}
                      </div>

                      {/* Dose calculada ou posologia rápida */}
                      {opt.isPediatric && opt.calculatedDoseBadge && (
                        <div className="mt-1.5 text-[11px] font-bold text-emerald-700 dark:text-emerald-300 flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-emerald-500" />
                          <span>Dose calculada: {opt.calculatedDoseBadge}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t text-[10px] text-slate-400"
                      style={{ borderColor: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.06)' }}
                    >
                      <span>Uso {opt.route} • {opt.defaultFrequency}</span>
                      <button
                        type="button"
                        onClick={(e) => handleQuickAddOption(opt, e)}
                        className="px-2 py-1 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold inline-flex items-center gap-1 shadow-xs cursor-pointer active:scale-95 transition-all"
                        title="Adicionar direto à receita"
                      >
                        <Plus className="w-3 h-3" strokeWidth={2.5} />
                        <span>Adicionar Direto</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
            )}
          </div>

          {/* PASSO 2: AJUSTE FINO DA POSOLOGIA E QUANTIDADE (OPCIONAL) */}
          {selectedOption && (
            <div
              className="p-4 rounded-xl border space-y-3.5"
              style={{
                backgroundColor: darkMode ? '#182030' : '#F8FAFC',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
              }}
            >
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 flex items-center gap-1.5">
                  <Info className="w-4 h-4" />
                  <span>2. Personalizar Posologia & Instruções:</span>
                </label>
                <span className="text-[11px] text-slate-400">
                  {selectedOption.presentation}
                </span>
              </div>

              {/* Posologia Textarea */}
              <div>
                <textarea
                  rows={2}
                  value={customPosology}
                  onChange={(e) => setCustomPosology(e.target.value)}
                  placeholder="Instruções de uso para o paciente..."
                  className="w-full p-3 rounded-xl text-xs font-medium focus:outline-none tactile-input leading-relaxed text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
                />
              </div>

              {/* Grid: Quantidade, Via, Frequência, Duração */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-2.5">
                <div>
                  <label className="block text-[11px] font-bold text-slate-400 mb-1">
                    Quantidade
                  </label>
                  <input
                    type="text"
                    value={customQuantity}
                    onChange={(e) => setCustomQuantity(e.target.value)}
                    placeholder="Ex: 1 caixa, 1 frasco"
                    className="w-full p-2.5 min-h-[40px] rounded-xl text-xs font-semibold focus:outline-none tactile-input text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-400 mb-1">
                    Via
                  </label>
                  <select
                    value={customRoute}
                    onChange={(e) => setCustomRoute(e.target.value)}
                    className="w-full p-2.5 min-h-[40px] rounded-xl text-xs font-semibold focus:outline-none tactile-input text-slate-900 dark:text-slate-100 cursor-pointer"
                  >
                    <option value="Oral">Oral</option>
                    <option value="Tópica">Tópica</option>
                    <option value="Inalatória">Inalatória</option>
                    <option value="Oftálmica">Oftálmica</option>
                    <option value="Otológica">Otológica</option>
                    <option value="Nasal">Nasal</option>
                    <option value="Injetável">Injetável</option>
                    <option value="Sublingual">Sublingual</option>
                    <option value="Retal">Retal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-400 mb-1">
                    Frequência
                  </label>
                  <select
                    value={customFrequency}
                    onChange={(e) => setCustomFrequency(e.target.value)}
                    className="w-full p-2.5 min-h-[40px] rounded-xl text-xs font-semibold focus:outline-none tactile-input text-slate-900 dark:text-slate-100 cursor-pointer"
                  >
                    <option value="4/4h">4/4h</option>
                    <option value="6/6h">6/6h</option>
                    <option value="8/8h">8/8h</option>
                    <option value="12/12h">12/12h</option>
                    <option value="24/24h">24/24h (1x/dia)</option>
                    <option value="Dose Única">Dose Única</option>
                    <option value="Uso Contínuo">Uso Contínuo</option>
                    <option value="S.O.S">Se necessário (S.O.S)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-400 mb-1">
                    Duração (dias)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="90"
                    value={customDays}
                    onChange={(e) => setCustomDays(parseInt(e.target.value) || 1)}
                    className="w-full p-2.5 min-h-[40px] rounded-xl text-xs font-semibold focus:outline-none tactile-input text-slate-900 dark:text-slate-100"
                  />
                </div>
              </div>

              {/* Controle Especial Checkbox */}
              <label className="flex items-center gap-2 pt-1 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={isSpecialControl}
                  onChange={(e) => setIsSpecialControl(e.target.checked)}
                  className="w-4 h-4 rounded text-sky-600 focus:ring-sky-500 cursor-pointer"
                />
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Receituário de Controle Especial (Portaria 344/98 / Antimicrobiano)
                </span>
              </label>
            </div>
          )}
        </div>

        {/* RODAPÉ DO MODAL */}
        <div
          className="p-4 border-t flex items-center justify-between gap-3 flex-shrink-0"
          style={{
            backgroundColor: darkMode ? '#141E2C' : '#F8F4EC',
            borderColor: darkMode ? 'rgba(255,255,255,0.08)' : '#E3D7BD'
          }}
        >
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 min-h-[42px] rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 cursor-pointer transition-colors"
          >
            Cancelar
          </button>

          <button
            type="button"
            disabled={!selectedOption}
            onClick={handleConfirm}
            className="btn-tactile-primary px-5 py-2.5 min-h-[44px] rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 cursor-pointer active:scale-95 disabled:opacity-40 transition-all shadow-sm"
          >
            <Plus className="w-4 h-4" strokeWidth={2.5} />
            <span>Adicionar ao Receituário</span>
          </button>
        </div>
      </div>
    </div>
  );
};
