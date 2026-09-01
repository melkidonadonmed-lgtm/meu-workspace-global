import React, { useState, useEffect, useRef } from 'react';
import { User, Check, X, Eraser } from 'lucide-react';
import { Patient } from '../types';

interface PatientModalProps {
  darkMode: boolean;
  patient: Patient;
  onSavePatient: (patient: Patient) => void;
  onClearPatient?: () => void;
  onClose: () => void;
}

export const PatientModal: React.FC<PatientModalProps> = ({
  darkMode,
  patient,
  onSavePatient,
  onClearPatient,
  onClose
}) => {
  const nameInputRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState<Patient>({
    id: patient?.id || 'pat-' + Date.now(),
    name: patient?.name || '',
    weightKg: patient?.weightKg ?? 0,
    weightCalcEnabled: patient?.weightCalcEnabled ?? false,
    ageText: patient?.ageText || '',
    birthDate: patient?.birthDate || '',
    gender: patient?.gender || 'male',
    documentNumber: patient?.documentNumber || '',
    motherName: patient?.motherName || '',
    phone: patient?.phone || '',
    allergies: patient?.allergies || [],
    notes: patient?.notes || ''
  });

  // Acessibilidade WCAG 2.1: Foco inicial e listener da tecla Escape
  useEffect(() => {
    nameInputRef.current?.focus();
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleClear = () => {
    const emptyPat: Patient = {
      id: 'pat-' + Date.now(),
      name: '',
      weightKg: 0,
      weightCalcEnabled: false,
      ageText: '',
      birthDate: '',
      gender: 'male',
      documentNumber: '',
      motherName: '',
      phone: '',
      allergies: [],
      notes: ''
    };
    setFormData(emptyPat);
    if (onClearPatient) {
      onClearPatient();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSavePatient(formData);
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs isolate animate-tab-fade"
      role="dialog"
      aria-modal="true"
      aria-labelledby="patient-modal-title"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-md rounded-2xl border overflow-hidden shadow-tactile-lg isolate transition-all"
        style={{
          backgroundColor: darkMode ? '#0E1420' : '#FFFFFF',
          borderColor: darkMode ? 'rgba(255,255,255,0.12)' : '#E3D7BD',
          boxShadow: darkMode ? '0 24px 50px -8px rgba(0,0,0,0.85), inset 0 1px 0 rgba(255,255,255,0.1)' : '0 20px 40px -8px rgba(20,32,50,0.18), inset 0 1px 0 rgba(255,255,255,0.95)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          className="p-4 border-b flex items-center justify-between" 
          style={{ 
            borderColor: darkMode ? 'rgba(255,255,255,0.08)' : '#E3D7BD',
            backgroundColor: darkMode ? '#141E2C' : '#F8F4EC'
          }}
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-navy-900/10 dark:bg-cream-100/15 text-navy-900 dark:text-cream-100 flex items-center justify-center font-bold">
              <User className="w-4 h-4" strokeWidth={2} />
            </div>
            <h3 id="patient-modal-title" className="font-bold text-sm sm:text-base text-navy-900 dark:text-cream-50">
              Dados do Paciente
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar modal de dados do paciente"
            className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 cursor-pointer active:scale-95 transition-all"
          >
            <X className="w-5 h-5" strokeWidth={1.75} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-3.5">
          <div>
            <label htmlFor="patient-modal-name" className="block text-xs font-bold uppercase text-slate-400 mb-1">
              Nome do Paciente ou Identificação
            </label>
            <input
              ref={nameInputRef}
              id="patient-modal-name"
              type="text"
              autoComplete="name"
              enterKeyHint="next"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Ex: Maria Silva, Leito 04, Visita Domiciliar..."
              className="w-full p-3 min-h-[44px] rounded-xl border text-xs font-semibold focus:outline-none tactile-input"
              style={{
                backgroundColor: 'var(--surface-inset)',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)',
                color: darkMode ? '#F4F7FC' : '#0B132B'
              }}
            />
          </div>

          {/* Toggle de cálculo de dose por peso */}
          <div
            className="p-3 rounded-xl border flex items-center justify-between gap-3 transition-colors"
            style={{
              backgroundColor: formData.weightCalcEnabled
                ? (darkMode ? 'rgba(6, 78, 59, 0.25)' : 'rgba(236, 253, 245, 0.9)')
                : (darkMode ? 'var(--surface-inset)' : 'var(--surface-inset)'),
              borderColor: formData.weightCalcEnabled
                ? (darkMode ? 'rgba(52, 211, 153, 0.4)' : 'rgba(16, 185, 129, 0.4)')
                : (darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)')
            }}
          >
            <div className="min-w-0">
              <span className="text-xs font-bold block" style={{ color: darkMode ? '#F4F7FC' : '#0B132B' }}>
                Cálculo de Dose por Peso (Pediátrico)
              </span>
              <span className="text-[11px] text-slate-400 block">
                {formData.weightCalcEnabled ? 'Ativado: calcula gotas e mL/kg automaticamente' : 'Desativado: modo adulto / doses padrão'}
              </span>
            </div>

            <button
              type="button"
              role="switch"
              aria-checked={formData.weightCalcEnabled}
              onClick={() => setFormData({ ...formData, weightCalcEnabled: !formData.weightCalcEnabled })}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                formData.weightCalcEnabled ? 'bg-emerald-600' : 'bg-slate-400 dark:bg-slate-700'
              }`}
            >
              <span
                aria-hidden="true"
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out ${
                  formData.weightCalcEnabled ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="patient-modal-weight" className="block text-xs font-bold uppercase text-slate-400 mb-1">
                Peso (kg) {formData.weightCalcEnabled ? '*' : '(opcional)'}
              </label>
              <div className="relative">
                <input
                  id="patient-modal-weight"
                  type="number"
                  step="0.1"
                  min="0.5"
                  max="200"
                  required={formData.weightCalcEnabled}
                  inputMode="decimal"
                  enterKeyHint="next"
                  value={formData.weightKg || ''}
                  onChange={(e) => setFormData({ ...formData, weightKg: parseFloat(e.target.value) || 0 })}
                  placeholder={formData.weightCalcEnabled ? "Ex: 14.5" : "Opcional"}
                  className="w-full p-3 min-h-[44px] rounded-xl border text-xs font-bold focus:outline-none tactile-input text-emerald-700 dark:text-emerald-400"
                  style={{
                    backgroundColor: 'var(--surface-inset)',
                    borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)'
                  }}
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">kg</span>
              </div>
            </div>

            <div>
              <label htmlFor="patient-modal-age" className="block text-xs font-bold uppercase text-slate-400 mb-1">
                Idade / Nasc.
              </label>
              <input
                id="patient-modal-age"
                type="text"
                enterKeyHint="next"
                value={formData.birthDate || formData.ageText || ''}
                onChange={(e) => setFormData({ ...formData, birthDate: e.target.value, ageText: e.target.value })}
                placeholder="Ex: 35 anos ou 2 anos..."
                className="w-full p-3 min-h-[44px] rounded-xl border text-xs font-medium focus:outline-none tactile-input"
                style={{
                  backgroundColor: 'var(--surface-inset)',
                  borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)',
                  color: darkMode ? '#F4F7FC' : '#0B132B'
                }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="patient-modal-doc" className="block text-xs font-bold uppercase text-slate-400 mb-1">
                Documento (CPF / RG / Certidão)
              </label>
              <input
                id="patient-modal-doc"
                type="text"
                enterKeyHint="next"
                value={formData.documentNumber || ''}
                onChange={(e) => setFormData({ ...formData, documentNumber: e.target.value })}
                placeholder="Ex: 542.189.708-44"
                className="w-full p-3 min-h-[44px] rounded-xl border text-xs font-medium focus:outline-none tactile-input"
                style={{
                  backgroundColor: 'var(--surface-inset)',
                  borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)',
                  color: darkMode ? '#F4F7FC' : '#0B132B'
                }}
              />
            </div>

            <div>
              <label htmlFor="patient-modal-phone" className="block text-xs font-bold uppercase text-slate-400 mb-1">
                Telefone / Responsável
              </label>
              <input
                id="patient-modal-phone"
                type="tel"
                autoComplete="tel"
                inputMode="tel"
                enterKeyHint="next"
                value={formData.phone || ''}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="(11) 98765-4321"
                className="w-full p-3 min-h-[44px] rounded-xl border text-xs font-medium focus:outline-none tactile-input"
                style={{
                  backgroundColor: 'var(--surface-inset)',
                  borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)',
                  color: darkMode ? '#F4F7FC' : '#0B132B'
                }}
              />
            </div>
          </div>

          <div>
            <label htmlFor="patient-modal-allergies" className="block text-xs font-bold uppercase text-slate-400 mb-1">
              Alergias Conhecidas (Medicamentosas ou Alimentares)
            </label>
            <input
              id="patient-modal-allergies"
              type="text"
              enterKeyHint="done"
              value={formData.allergies?.join(', ') || ''}
              onChange={(e) => setFormData({ ...formData, allergies: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
              placeholder="Ex: Penicilina, Dipirona, AINEs, Frutos do mar..."
              className="w-full p-3 min-h-[44px] rounded-xl border text-xs font-medium focus:outline-none tactile-input text-rose-700 dark:text-rose-400"
              style={{
                backgroundColor: 'var(--surface-inset)',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)'
              }}
            />
          </div>

          <div className="pt-3 border-t flex items-center justify-between gap-2" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : '#E3D7BD' }}>
            <button
              type="button"
              onClick={handleClear}
              className="px-3.5 py-2.5 min-h-[44px] rounded-xl text-xs font-bold text-navy-900 dark:text-cream-100 hover:bg-navy-900/10 dark:hover:bg-cream-100/10 transition-all flex items-center gap-1.5 cursor-pointer active:scale-95"
              title="Limpar todos os campos para digitar novo paciente"
            >
              <Eraser className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
              <span>Limpar</span>
            </button>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2.5 min-h-[44px] rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 cursor-pointer active:scale-95 transition-all"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="btn-tactile-primary px-5 py-2.5 min-h-[44px] text-xs font-bold flex items-center gap-1.5 cursor-pointer active:scale-95"
              >
                <Check className="w-4 h-4" strokeWidth={2} />
                <span>Salvar Paciente</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
