import React, { useState, useMemo } from 'react';
import { 
  Calculator, 
  Search, 
  Plus, 
  Check, 
  Scale, 
  AlertTriangle, 
  ArrowRight,
  Clock
} from 'lucide-react';
import { PEDIATRIC_MEDICATIONS } from '../data/pediatricMeds';
import { PediatricMedication, PrescriptionItem, Patient } from '../types';
import { calculatePediatricDose } from '../utils/doseCalculator';

interface PediatricCalculatorProps {
  darkMode: boolean;
  patient: Patient;
  onUpdatePatientWeight: (weight: number) => void;
  onAddPrescriptionItem: (item: PrescriptionItem) => void;
  onNavigateToPrescription: () => void;
}

export const PediatricCalculator: React.FC<PediatricCalculatorProps> = ({
  darkMode,
  patient,
  onUpdatePatientWeight,
  onAddPrescriptionItem,
  onNavigateToPrescription
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('Todos');
  const [addedMedsMap, setAddedMedsMap] = useState<{ [id: string]: boolean }>({});

  const patientWeight = patient?.weightKg && patient.weightKg > 0 ? patient.weightKg : 0;
  const patientName = patient?.name?.trim() || 'Não identificado';

  const categories = useMemo(() => {
    const list = Array.from(new Set(PEDIATRIC_MEDICATIONS.map(m => m.category)));
    return ['Todos', ...list];
  }, []);

  const weightPresets = [
    { label: 'RN (3.5 kg)', weight: 3.5 },
    { label: '6m (8 kg)', weight: 8 },
    { label: '1 ano (10 kg)', weight: 10 },
    { label: '2 anos (12 kg)', weight: 12 },
    { label: '3 anos (15 kg)', weight: 15 },
    { label: '5 anos (20 kg)', weight: 20 },
    { label: '8 anos (25 kg)', weight: 25 },
    { label: '10 anos (32 kg)', weight: 32 },
    { label: '12 anos (40 kg)', weight: 40 }
  ];

  const filteredMedications = useMemo(() => {
    return PEDIATRIC_MEDICATIONS.filter(med => {
      const matchCategory = selectedCategory === 'Todos' || med.category === selectedCategory;
      const matchSearch = 
        med.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.presentation.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.observations.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.category.toLowerCase().includes(searchTerm.toLowerCase());
      return matchCategory && matchSearch;
    });
  }, [selectedCategory, searchTerm]);

  const handleAddMedication = (med: PediatricMedication) => {
    const calc = calculatePediatricDose(med, patientWeight);

    let doseText = '';
    if (med.unitType === 'drops' && calc.calculatedDrops !== undefined) {
      doseText = `${calc.calculatedDrops} gotas (${calc.volumeText})`;
    } else if (med.unitType === 'fixed') {
      doseText = med.doseCustomLabel || 'Conforme orientação';
    } else {
      doseText = `${calc.volumeText} (${calc.rawDoseText})`;
    }

    const newItem: PrescriptionItem = {
      id: `presc-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      name: med.name,
      presentation: med.presentation,
      route: med.route,
      quantity: '1 frasco',
      doseCalculatedText: doseText,
      frequencyText: med.frequency,
      scheduleInterval: med.frequency.includes('6/6') ? '6/6h' : med.frequency.includes('8/8') ? '8/8h' : med.frequency.includes('12/12') ? '12/12h' : '24/24h',
      scheduleTimes: [],
      durationDays: med.defaultDays || 5,
      instructions: calc.formattedPrescriptionText,
      isContinuous: false,
      calculatedFromWeight: patientWeight
    };

    onAddPrescriptionItem(newItem);

    // Visual feedback
    setAddedMedsMap(prev => ({ ...prev, [med.id]: true }));
    setTimeout(() => {
      setAddedMedsMap(prev => ({ ...prev, [med.id]: false }));
    }, 1800);
  };

  return (
    <div id="pediatric-calculator-section" className="w-full max-w-full space-y-4 sm:space-y-5">
      {/* Top Controller: Weight Hero Tactile Card */}
      <div 
        className="tactile-card p-4 sm:p-5 rounded-2xl relative overflow-hidden w-full"
        style={{
          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
        }}
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 sm:gap-6">
          {/* Left: Info */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
              <span 
                className="p-2 rounded-xl text-white flex-shrink-0"
                style={{
                  backgroundColor: darkMode ? '#155730' : '#15803D',
                  border: '1px solid rgba(255, 255, 255, 0.12)'
                }}
              >
                <Calculator className="w-5 h-5 text-slate-100" strokeWidth={1.75} />
              </span>
              <h2 className="text-lg sm:text-xl font-bold tracking-tight" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                Calculadora de Doses Pediátricas
              </h2>
            </div>
            <p className="text-xs sm:text-sm font-medium leading-relaxed" style={{ color: darkMode ? '#8E9CAE' : '#64748B' }}>
              Ajuste o peso de <span className="text-sky-700 dark:text-sky-400 font-semibold">{patientName}</span> para recalcular doses em mg, volume (mL) e gotas instantaneamente com teto de segurança.
            </p>
          </div>

          {/* Right: Interactive Weight Stepper & Display (Ergonomic & Touch-friendly) */}
          <div 
            className="flex items-center justify-between sm:justify-center gap-1 sm:gap-2 p-2 sm:p-2.5 rounded-2xl border w-full lg:w-auto flex-shrink-0 tactile-flat"
            style={{
              backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--bg-app)',
              borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
            }}
          >
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => onUpdatePatientWeight(Math.max(1, +(patientWeight - 1).toFixed(1)))}
                className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-xl font-extrabold text-sm flex items-center justify-center transition-all cursor-pointer tactile-btn-secondary active:scale-95"
                style={{
                  backgroundColor: darkMode ? 'var(--surface-card)' : 'var(--surface-card)',
                  color: darkMode ? '#F4F7FC' : '#0B132B'
                }}
                title="Diminuir 1 kg"
              >
                -1
              </button>
              <button
                type="button"
                onClick={() => onUpdatePatientWeight(Math.max(1, +(patientWeight - 0.5).toFixed(1)))}
                className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-xl font-bold text-xs flex items-center justify-center transition-all cursor-pointer tactile-btn-secondary active:scale-95"
                style={{
                  backgroundColor: darkMode ? 'var(--surface-card)' : 'var(--surface-card)',
                  color: darkMode ? '#94A3B8' : '#526071'
                }}
                title="Diminuir 0.5 kg"
              >
                -0.5
              </button>
            </div>

            <div className="px-3 text-center min-w-[90px] sm:min-w-[110px]">
              <span className="text-[9px] font-extrabold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 block">
                PESO ATUAL
              </span>
              <div className="flex items-baseline justify-center gap-1">
                <input
                  type="number"
                  min="0.5"
                  max="120"
                  step="0.5"
                  value={patientWeight}
                  onChange={(e) => onUpdatePatientWeight(parseFloat(e.target.value) || 1)}
                  className="w-16 sm:w-20 font-black text-2xl text-center bg-transparent border-b-2 border-emerald-600 dark:border-emerald-500 focus:outline-none focus:border-sky-500"
                  style={{ color: darkMode ? '#388EE6' : '#0F5E94' }}
                />
                <span className="text-xs font-extrabold text-emerald-700 dark:text-emerald-400">kg</span>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => onUpdatePatientWeight(Math.min(120, +(patientWeight + 0.5).toFixed(1)))}
                className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-xl font-bold text-xs flex items-center justify-center transition-all cursor-pointer tactile-btn-secondary active:scale-95"
                style={{
                  backgroundColor: darkMode ? 'var(--surface-card)' : 'var(--surface-card)',
                  color: darkMode ? '#94A3B8' : '#526071'
                }}
                title="Aumentar 0.5 kg"
              >
                +0.5
              </button>
              <button
                type="button"
                onClick={() => onUpdatePatientWeight(Math.min(120, +(patientWeight + 1).toFixed(1)))}
                className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-xl font-extrabold text-sm flex items-center justify-center transition-all cursor-pointer tactile-btn-secondary active:scale-95"
                style={{
                  backgroundColor: darkMode ? 'var(--surface-card)' : 'var(--surface-card)',
                  color: darkMode ? '#F4F7FC' : '#0B132B'
                }}
                title="Aumentar 1 kg"
              >
                +1
              </button>
            </div>
          </div>
        </div>

        {/* Quick Weight Range Presets */}
        <div className="mt-3.5 pt-3.5 border-t flex items-center gap-2 overflow-x-auto pb-1 max-w-full" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)' }}>
          <span className="text-xs font-bold whitespace-nowrap text-slate-400 flex items-center gap-1 flex-shrink-0">
            <Scale className="w-4 h-4 text-sky-500" strokeWidth={2} /> Faixas:
          </span>
          {weightPresets.map((p) => (
            <button
              key={p.label}
              type="button"
              onClick={() => onUpdatePatientWeight(p.weight)}
              className={`text-xs px-3.5 py-2 min-h-[44px] rounded-xl border font-bold whitespace-nowrap transition-all cursor-pointer flex-shrink-0 active:scale-95 ${
                patientWeight === p.weight
                  ? 'bg-emerald-600 text-white border-emerald-400 shadow-md shadow-emerald-600/25'
                  : darkMode
                  ? 'bg-slate-800/80 text-slate-300 border-slate-700/80 hover:bg-slate-700 hover:text-white'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-2.5 items-stretch sm:items-center justify-between">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" strokeWidth={1.75} />
          <input
            type="text"
            placeholder="Buscar medicamento ou apresentação (ex: Paracetamol, Amoxicilina, Dipirona, Ondansetrona)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 min-h-[44px] rounded-xl text-xs font-medium focus:outline-none transition-all tactile-input"
          />
        </div>

        {/* View Prescription Action Button */}
        <button
          onClick={onNavigateToPrescription}
          className="tactile-btn-primary px-5 py-3 min-h-[44px] flex items-center justify-center gap-2 text-xs font-bold cursor-pointer whitespace-nowrap active:scale-95"
        >
          <span>Ir para Receita</span>
          <ArrowRight className="w-4 h-4" strokeWidth={2.2} />
        </button>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar fade-scroll-x">
        {categories.map((cat) => {
          const isSelected = selectedCategory === cat;
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`text-xs font-bold px-3.5 py-2 min-h-[44px] rounded-xl whitespace-nowrap transition-all cursor-pointer border active:scale-95 ${
                isSelected
                  ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                  : darkMode
                  ? 'bg-slate-800/80 text-slate-300 border-slate-700/80 hover:bg-slate-700/90'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Medications Table / Cards Container */}
      <div 
        className="tactile-card rounded-2xl overflow-hidden"
      >
        <div className="p-3.5 sm:p-4 border-b flex items-center justify-between" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)' }}>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600 dark:bg-emerald-400" />
            <h3 className="font-bold text-xs sm:text-sm" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
              Tabela de Medicamentos Calculados ({filteredMedications.length} itens)
            </h3>
          </div>
          <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">
            Dose base: {patientWeight} kg
          </span>
        </div>

        {/* Desktop Table View */}
        <div className="hidden lg:block overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr 
                className="font-bold uppercase tracking-wider text-[10px] border-b"
                style={{
                  backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--bg-app)',
                  borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)',
                  color: darkMode ? '#8E9CAE' : '#64748B'
                }}
              >
                <th className="py-3 px-4">Medicamento / Apresentação</th>
                <th className="py-3 px-3">Concentração</th>
                <th className="py-3 px-3">Dose Padrão</th>
                <th className="py-3 px-3 bg-emerald-500/10 border-x border-emerald-500/15">Dose Calculada</th>
                <th className="py-3 px-3 bg-emerald-500/10">Volume (mL)</th>
                <th className="py-3 px-3 bg-emerald-500/10 border-r border-emerald-500/15">Gotas</th>
                <th className="py-3 px-4">Posologia / Observações</th>
                <th className="py-3 px-4 text-right">Ação</th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(15, 23, 42, 0.05)' }}>
              {filteredMedications.map((med) => {
                const calc = calculatePediatricDose(med, patientWeight);
                const isAdded = addedMedsMap[med.id];

                return (
                  <tr 
                    key={med.id}
                    className={`transition-colors hover:bg-slate-500/5 ${isAdded ? 'bg-emerald-500/10' : ''}`}
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-xs" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                        {med.name}
                      </div>
                      <div className="text-[11px] text-sky-700 dark:text-sky-400 font-medium">{med.presentation}</div>
                      <span className="inline-block mt-0.5 text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-slate-500/10 text-slate-500 dark:text-slate-400">
                        {med.category}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold" style={{ color: darkMode ? '#CBD5E1' : '#334155' }}>
                      {med.concentrationMgPerMl > 0 ? `${med.concentrationMgPerMl} mg/mL` : '-'}
                    </td>
                    <td className="py-3 px-3" style={{ color: darkMode ? '#8E9CAE' : '#64748B' }}>
                      {med.standardDoseMgKg > 0 ? `${med.standardDoseMgKg} mg/kg` : 'Dose Fixa'}
                      {med.maxDoseMg > 0 && (
                        <div className="text-[10px] text-amber-700 dark:text-amber-400">Máx {med.maxDoseMg} mg</div>
                      )}
                    </td>
                    <td className="py-3 px-3 bg-emerald-500/[0.04] border-x border-emerald-500/10">
                      <div className="font-black text-sm text-sky-700 dark:text-sky-400">
                        {calc.rawDoseText}
                      </div>
                      {calc.isMaxDoseReached && (
                        <span className="text-[9px] font-bold text-amber-700 dark:text-amber-400 flex items-center gap-0.5">
                          <AlertTriangle className="w-2.5 h-2.5" strokeWidth={1.75} /> Teto Máx
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 bg-emerald-500/[0.04]">
                      <span className="font-black text-sm text-emerald-700 dark:text-emerald-400">
                        {calc.volumeText}
                      </span>
                    </td>
                    <td className="py-3 px-3 bg-emerald-500/[0.04] border-r border-emerald-500/10">
                      <span className={`font-black text-sm ${calc.dropsText !== '-' ? 'text-amber-700 dark:text-amber-400' : 'text-slate-400'}`}>
                        {calc.dropsText}
                      </span>
                    </td>
                    <td className="py-3 px-4 max-w-xs">
                      <div className="font-medium text-xs line-clamp-2" style={{ color: darkMode ? '#CBD5E1' : '#475569' }}>
                        {med.frequency}
                      </div>
                      <div className="text-[10px] text-slate-400 line-clamp-1 italic mt-0.5">
                        {med.observations}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        type="button"
                        onClick={() => handleAddMedication(med)}
                        className={`px-3 py-1.5 rounded-xl font-semibold text-xs transition-all cursor-pointer flex items-center gap-1.5 ml-auto ${
                          isAdded
                            ? 'bg-emerald-700 text-white'
                            : 'tactile-btn-primary'
                        }`}
                      >
                        {isAdded ? (
                          <>
                            <Check className="w-3.5 h-3.5" strokeWidth={1.75} />
                            <span>Adicionado</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" strokeWidth={1.75} />
                            <span>Prescrever</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Mobile / Tablet Cards View */}
        <div className="lg:hidden divide-y" style={{ borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)' }}>
          {filteredMedications.map((med) => {
            const calc = calculatePediatricDose(med, patientWeight);
            const isAdded = addedMedsMap[med.id];

            return (
              <div 
                key={med.id} 
                className={`p-3.5 sm:p-4 space-y-3 transition-colors ${isAdded ? 'bg-emerald-500/10' : ''}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-[9px] uppercase font-bold px-2 py-0.5 rounded bg-slate-500/10 text-slate-500 dark:text-slate-400 border border-slate-500/20">
                      {med.category}
                    </span>
                    <h4 className="font-bold text-sm mt-1" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                      {med.name}
                    </h4>
                    <p className="text-xs font-semibold text-sky-700 dark:text-sky-400">{med.presentation}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleAddMedication(med)}
                    className={`px-3 py-2 rounded-xl font-semibold text-xs flex items-center gap-1.5 ${
                      isAdded ? 'bg-emerald-700 text-white' : 'tactile-btn-primary'
                    }`}
                  >
                    {isAdded ? <Check className="w-4 h-4" strokeWidth={1.75} /> : <Plus className="w-4 h-4" strokeWidth={1.75} />}
                    <span>{isAdded ? 'Adicionado' : 'Prescrever'}</span>
                  </button>
                </div>

                {/* Calculation Badges Grid */}
                <div 
                  className="grid grid-cols-3 gap-2 p-2.5 rounded-xl border tactile-flat"
                  style={{
                    backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--bg-app)',
                    borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
                  }}
                >
                  <div className="text-center">
                    <span className="text-[9px] font-bold text-slate-400 uppercase block">Dose (mg)</span>
                    <span className="text-xs font-bold text-sky-700 dark:text-sky-400">{calc.rawDoseText}</span>
                  </div>
                  <div className="text-center border-x" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)' }}>
                    <span className="text-[9px] font-bold text-slate-400 uppercase block">Volume (mL)</span>
                    <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400">{calc.volumeText}</span>
                  </div>
                  <div className="text-center">
                    <span className="text-[9px] font-bold text-slate-400 uppercase block">Gotas</span>
                    <span className={`text-xs font-bold ${calc.dropsText !== '-' ? 'text-amber-700 dark:text-amber-400' : 'text-slate-400'}`}>
                      {calc.dropsText}
                    </span>
                  </div>
                </div>

                <div className="text-xs space-y-1">
                  <div className="font-semibold flex items-center gap-1.5" style={{ color: darkMode ? '#CBD5E1' : '#334155' }}>
                    <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" strokeWidth={1.75} />
                    <span>{med.frequency}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 italic">
                    {med.observations}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
