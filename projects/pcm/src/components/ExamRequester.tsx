import React, { useState, useMemo } from 'react';
import { 
  FlaskConical, 
  Search, 
  Check, 
  Plus, 
  Trash2, 
  Download, 
  Sparkles, 
  FileCheck
} from 'lucide-react';
import { ExamItem, Patient } from '../types';
import { EXAM_CATALOG, EXAM_PACKAGES, ExamPackage } from '../data/examCatalog';

interface ExamRequesterProps {
  darkMode: boolean;
  patient: Patient;
  selectedExams: ExamItem[];
  onUpdateSelectedExams?: (exams: ExamItem[]) => void;
  onUpdateExams?: (exams: ExamItem[]) => void;
  clinicalIndication: string;
  onUpdateClinicalIndication: (text: string) => void;
  onNavigateToPrint: () => void;
}

export const ExamRequester: React.FC<ExamRequesterProps> = ({
  darkMode,
  patient,
  selectedExams = [],
  onUpdateSelectedExams,
  onUpdateExams,
  clinicalIndication,
  onUpdateClinicalIndication,
  onNavigateToPrint
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('Todos');
  const [customExamName, setCustomExamName] = useState('');

  const updateExams = onUpdateSelectedExams || onUpdateExams || (() => {});

  const categories = useMemo(() => {
    const list = Array.from(new Set(EXAM_CATALOG.map(e => e.category)));
    return ['Todos', ...list];
  }, []);

  const isExamSelected = (id: string) => {
    return selectedExams.some(e => e.id === id);
  };

  const toggleExam = (exam: ExamItem) => {
    if (isExamSelected(exam.id)) {
      updateExams(selectedExams.filter(e => e.id !== exam.id));
    } else {
      updateExams([...selectedExams, { ...exam, selected: true }]);
    }
  };

  const applyPackage = (pkg: ExamPackage) => {
    const newExams = [...selectedExams];
    pkg.examIds.forEach(id => {
      const found = EXAM_CATALOG.find(e => e.id === id);
      if (found && !newExams.some(e => e.id === id)) {
        newExams.push({ ...found, selected: true });
      }
    });
    updateExams(newExams);
  };

  const handleAddCustomExam = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customExamName.trim()) return;

    const newCustomExam: ExamItem = {
      id: `custom-exam-${Date.now()}`,
      category: 'Personalizado',
      name: customExamName.trim(),
      selected: true,
      urgency: 'routine'
    };

    updateExams([...selectedExams, newCustomExam]);
    setCustomExamName('');
  };

  const filteredCatalog = useMemo(() => {
    return EXAM_CATALOG.filter(exam => {
      const matchCat = selectedCategory === 'Todos' || exam.category === selectedCategory;
      const matchSearch = exam.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          exam.category.toLowerCase().includes(searchTerm.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [selectedCategory, searchTerm]);

  return (
    <div id="exam-requester-section" className="space-y-4 sm:space-y-5">
      {/* Top Header Card */}
      <div 
        className="tactile-card p-4 sm:p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4"
        style={{
          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
        }}
      >
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-xl flex items-center justify-center text-white"
            style={{
              backgroundColor: darkMode ? '#854D0E' : '#B45309',
              border: '1px solid rgba(255, 255, 255, 0.12)'
            }}
          >
            <FlaskConical className="w-5 h-5 text-slate-100" strokeWidth={1.75} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                Solicitação de Exames Complementares
              </h2>
              <span className="text-[11px] px-2 py-0.5 rounded-md bg-navy-900/10 text-navy-900 dark:bg-cream-100/15 dark:text-cream-100 border border-navy-900/20 dark:border-cream-100/25 font-semibold">
                {selectedExams.length} selecionado(s)
              </span>
            </div>
            <p className="text-xs font-medium mt-0.5" style={{ color: darkMode ? '#8E9CAE' : '#64748B' }}>
              Paciente: <span className="text-navy-900 dark:text-cream-100 font-semibold">{patient?.name?.trim() || 'Não identificado'}</span> • Selecione exames individuais ou painéis rápidos.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onNavigateToPrint}
          disabled={selectedExams.length === 0}
          className="tactile-btn-success px-4 py-2 text-xs sm:text-sm font-semibold flex items-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <Download className="w-4 h-4" strokeWidth={1.75} />
          <span>Visualizar & Baixar PDF ({selectedExams.length})</span>
        </button>
      </div>

      {/* Quick Clinical Packages */}
      <div 
        className="tactile-card p-3.5 sm:p-4 rounded-2xl"
        style={{
          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
        }}
      >
        <div className="flex items-center gap-1.5 mb-2.5">
          <Sparkles className="w-4 h-4 text-navy-900 dark:text-cream-200" strokeWidth={1.75} />
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
            Painéis & Pacotes Clínicos:
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {EXAM_PACKAGES.map((pkg) => (
            <button
              key={pkg.id}
              type="button"
              onClick={() => applyPackage(pkg)}
              className="p-3 rounded-xl border text-left transition-all cursor-pointer hover:border-slate-400 dark:hover:border-slate-600 flex flex-col justify-between group tactile-flat"
              style={{
                backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--bg-app)',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
              }}
            >
              <div>
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="font-bold text-xs" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                    {pkg.name}
                  </span>
                  <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-slate-200/60 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {pkg.badge}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2">
                  {pkg.description}
                </p>
              </div>
              <div className="mt-2 text-[11px] font-semibold text-sky-700 dark:text-sky-400 flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                <Plus className="w-3 h-3" strokeWidth={1.75} /> Incluir {pkg.examIds.length} exames
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Clinical Indication */}
      <div 
        className="tactile-card p-3.5 sm:p-4 rounded-2xl"
        style={{
          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
        }}
      >
        <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1.5">
          Indicação Clínica / Hipótese Diagnóstica (Para o Laboratório / Convênio)
        </label>
        <input
          type="text"
          value={clinicalIndication}
          onChange={(e) => onUpdateClinicalIndication(e.target.value)}
          placeholder="Ex: Investigação de síndrome febril aguda a esclarecer, controle de rotina, etc."
          className="w-full p-3 rounded-xl text-xs font-medium focus:outline-none tactile-input"
        />
      </div>

      {/* Main Grid: Catalog Left & Selected Exams Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5">
        {/* Left 2 Cols: Exam Catalog Matrix */}
        <div className="lg:col-span-2 space-y-3">
          {/* Search and Category Filters */}
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" strokeWidth={1.75} />
              <input
                type="text"
                placeholder="Buscar exame (ex: Hemograma, PCR, Dengue, Ureia, Raio-X, ECG)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs font-medium focus:outline-none tactile-input"
              />
            </div>

            <form onSubmit={handleAddCustomExam} className="flex gap-2">
              <input
                type="text"
                placeholder="Adicionar exame avulso..."
                value={customExamName}
                onChange={(e) => setCustomExamName(e.target.value)}
                className="p-2.5 rounded-xl text-xs font-medium focus:outline-none tactile-input w-44"
              />
              <button
                type="submit"
                className="tactile-btn-primary px-4 py-2.5 rounded-xl text-xs font-bold"
              >
                +
              </button>
            </form>
          </div>

          {/* Category Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar fade-scroll-x">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`text-xs font-bold px-3.5 py-2 min-h-[44px] rounded-xl whitespace-nowrap border transition-all cursor-pointer active:scale-95 ${
                  selectedCategory === cat
                    ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                    : darkMode
                    ? 'bg-slate-800/80 text-slate-300 border-slate-700/80 hover:bg-slate-700'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Exams Grid */}
          <div 
            className="tactile-card p-3 rounded-2xl max-h-[520px] overflow-y-auto space-y-1.5 divide-y"
            style={{
              backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
              borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
            }}
          >
            {filteredCatalog.map((exam) => {
              const selected = isExamSelected(exam.id);

              return (
                <div
                  key={exam.id}
                  onClick={() => toggleExam(exam)}
                  className={`pt-1.5 flex items-center justify-between p-2 rounded-xl cursor-pointer transition-all ${
                    selected 
                      ? 'bg-navy-900/10 dark:bg-cream-100/10 border border-navy-900/30 dark:border-cream-100/30' 
                      : 'hover:bg-slate-500/5'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                    <div 
                      className={`w-4.5 h-4.5 rounded-md border flex items-center justify-center transition-all ${
                        selected ? 'bg-navy-900 dark:bg-cream-100 border-navy-900 dark:border-cream-100 text-white dark:text-navy-950' : 'border-slate-400'
                      }`}
                    >
                      {selected && <Check className="w-3 h-3 stroke-[2.5]" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-semibold text-xs truncate" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                        {exam.name}
                      </div>
                      <span className="text-[10px] text-slate-400 font-medium">{exam.category}</span>
                    </div>
                  </div>

                  {exam.urgency === 'urgent' && (
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-rose-500/15 text-rose-700 dark:text-rose-300 border border-rose-500/20">
                      Urgência
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Selected Items Tray */}
        <div 
          className="tactile-card p-3.5 sm:p-4 rounded-2xl flex flex-col h-fit space-y-3"
          style={{
            backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
            borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
          }}
        >
          <div className="flex items-center justify-between border-b pb-2.5" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)' }}>
            <h3 className="font-bold text-xs sm:text-sm flex items-center gap-2" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
              <FileCheck className="w-4 h-4 text-emerald-700 dark:text-emerald-400" strokeWidth={1.75} />
              Exames no Pedido ({selectedExams.length})
            </h3>
            {selectedExams.length > 0 && (
              <button
                type="button"
                onClick={() => onUpdateSelectedExams([])}
                className="text-[11px] font-semibold text-rose-700 dark:text-rose-400 hover:underline cursor-pointer"
              >
                Limpar
              </button>
            )}
          </div>

          {selectedExams.length === 0 ? (
            <div className="p-6 text-center text-slate-400 text-xs">
              Nenhum exame selecionado ainda. Clique nos exames ao lado ou em um dos pacotes para incluir.
            </div>
          ) : (
            <div className="space-y-1.5 max-h-[380px] overflow-y-auto">
              {selectedExams.map((exam, index) => (
                <div 
                  key={exam.id}
                  className="p-2 rounded-xl border flex items-center justify-between gap-2 tactile-flat"
                  style={{
                    backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--bg-app)',
                    borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
                  }}
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-semibold truncate" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                      {index + 1}. {exam.name}
                    </div>
                    <span className="text-[9px] text-navy-900 dark:text-cream-100 font-medium">{exam.category}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => toggleExam(exam)}
                    className="text-slate-400 hover:text-rose-600 p-1 cursor-pointer"
                    title="Remover"
                  >
                    <Trash2 className="w-3.5 h-3.5" strokeWidth={1.75} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {selectedExams.length > 0 && (
            <div className="pt-2 border-t" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)' }}>
              <button
                type="button"
                onClick={onNavigateToPrint}
                className="tactile-btn-success w-full py-2.5 text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer"
              >
                <Download className="w-4 h-4" strokeWidth={1.75} />
                <span>Gerar & Baixar PDF</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
