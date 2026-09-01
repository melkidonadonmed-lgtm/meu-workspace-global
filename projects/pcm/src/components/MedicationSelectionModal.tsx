import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Search,
  X,
  Pill,
  Check,
  Scale,
  Sparkles,
  Layers,
  ArrowRight,
  Filter,
  Tag,
  AlertTriangle,
  Info,
  SlidersHorizontal,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import { Patient, PrescriptionItem } from '../types';
import { BaseMedicationGroup, MedicationOption, getAllMedicationGroups } from '../utils/medicationCatalog';
import {
  searchMedicationsFuzzy,
  THERAPEUTIC_CLASSES,
  FuzzySearchResult
} from '../utils/fuzzySearch';

interface MedicationSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectGroup: (group: BaseMedicationGroup) => void;
  patient: Patient;
  darkMode: boolean;
  initialSearchQuery?: string;
  initialFilter?: 'todos' | 'pediatric' | 'adult' | 'special';
}

export const MedicationSelectionModal: React.FC<MedicationSelectionModalProps> = ({
  isOpen,
  onClose,
  onSelectGroup,
  patient,
  darkMode,
  initialSearchQuery = '',
  initialFilter = 'todos'
}) => {
  const [searchTerm, setSearchTerm] = useState(initialSearchQuery);
  const [typeFilter, setTypeFilter] = useState<'todos' | 'pediatric' | 'adult' | 'special'>(initialFilter);
  const [selectedTherapeuticClass, setSelectedTherapeuticClass] = useState<string>('todos');
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const listContainerRef = useRef<HTMLDivElement>(null);

  const patientWeight = patient?.weightKg ?? 0;
  const hasWeight = patientWeight > 0;
  const patientName = patient?.name || 'Paciente sem nome';

  // Carrega todos os grupos de medicamentos base sincronizados com o paciente
  const allGroups = useMemo(() => {
    return getAllMedicationGroups(patient);
  }, [patient]);

  // Executa a busca difusa avançada com pontuação de relevância e classes terapêuticas
  const searchResults: FuzzySearchResult[] = useMemo(() => {
    return searchMedicationsFuzzy(allGroups, searchTerm, typeFilter, selectedTherapeuticClass);
  }, [allGroups, searchTerm, typeFilter, selectedTherapeuticClass]);

  // Efeito ao abrir modal: focar no input e resetar estados
  useEffect(() => {
    if (isOpen) {
      setSearchTerm(initialSearchQuery);
      setTypeFilter(initialFilter);
      setSelectedTherapeuticClass('todos');
      setSelectedIndex(0);

      // Pequeno timeout para garantir foco após render
      setTimeout(() => {
        searchInputRef.current?.focus();
        if (initialSearchQuery) {
          searchInputRef.current?.select();
        }
      }, 50);
    }
  }, [isOpen, initialSearchQuery, initialFilter]);

  // Reset index quando resultados mudam
  useEffect(() => {
    setSelectedIndex(0);
  }, [searchResults.length, searchTerm, typeFilter, selectedTherapeuticClass]);

  // Atalhos de teclado (ESC, Setas Cima/Baixo, Enter)
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, Math.max(0, searchResults.length - 1)));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter' && searchResults.length > 0) {
        e.preventDefault();
        const selected = searchResults[selectedIndex];
        if (selected) {
          onSelectGroup(selected.group);
          onClose();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, searchResults, selectedIndex, onSelectGroup, onClose]);

  // Rola o item selecionado para a visão
  useEffect(() => {
    if (listContainerRef.current) {
      const selectedElem = listContainerRef.current.querySelector(`[data-index="${selectedIndex}"]`);
      if (selectedElem) {
        selectedElem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  if (!isOpen) return null;

  // Filtros rápidos de classes terapêuticas mais populares
  const popularClasses = [
    { id: 'todos', label: 'Todas as Classes' },
    ...THERAPEUTIC_CLASSES.map(tc => ({ id: tc.canonicalCategory, label: tc.displayName }))
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/60 backdrop-blur-xs isolate animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="medication-search-modal-title"
    >
      <div
        className="w-full max-w-3xl max-h-[92vh] rounded-2xl border flex flex-col shadow-tactile-lg overflow-hidden transition-all"
        style={{
          backgroundColor: darkMode ? '#0E1420' : '#FFFFFF',
          borderColor: darkMode ? 'rgba(255,255,255,0.12)' : '#E3D7BD',
          boxShadow: darkMode ? '0 24px 50px -8px rgba(0,0,0,0.85), inset 0 1px 0 rgba(255,255,255,0.1)' : '0 20px 40px -8px rgba(20,32,50,0.18), inset 0 1px 0 rgba(255,255,255,0.95)'
        }}
      >
        {/* CABEÇALHO DO MODAL */}
        <div
          className="p-4 sm:p-5 border-b flex-shrink-0 space-y-3"
          style={{
            backgroundColor: darkMode ? '#141E2C' : '#F8F4EC',
            borderColor: darkMode ? 'rgba(255,255,255,0.08)' : '#E3D7BD'
          }}
        >
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2.5 rounded-xl bg-navy-900/10 dark:bg-cream-100/15 text-navy-900 dark:text-cream-100 flex items-center justify-center flex-shrink-0 font-bold">
                <Pill className="w-5 h-5" strokeWidth={2} />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3
                    id="medication-search-modal-title"
                    className="font-extrabold text-base sm:text-lg tracking-tight truncate"
                    style={{ color: darkMode ? '#F1F5F9' : '#0B132B' }}
                  >
                    Buscador Inteligente de Medicamentos
                  </h3>
                  <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-navy-900/10 text-navy-900 dark:bg-cream-100/15 dark:text-cream-100 border border-navy-900/20 dark:border-cream-100/25">
                    Fuzzy Search • {allGroups.length} Fármacos
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium truncate mt-0.5">
                  Busca tolerante por nome parcial, classe terapêutica, princípio ativo ou sintomas
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-500/15 transition-colors cursor-pointer flex-shrink-0"
              title="Fechar modal (Esc)"
            >
              <X className="w-4 h-4" strokeWidth={2} />
            </button>
          </div>

          {/* BARRA DE PESQUISA FUZZY */}
          <div className="relative">
            <div className="relative flex items-center">
              <Search
                className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-navy-900 dark:text-cream-100 pointer-events-none"
                strokeWidth={2}
              />
              <input
                ref={searchInputRef}
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por nome parcial (ex: dipr, amox, parac, losart), classe (ex: antibiotico, febre, dor, asma) ou marca..."
                className="w-full pl-11 pr-24 py-3.5 rounded-xl border text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-sky-500/40 tactile-input transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                style={{
                  backgroundColor: darkMode ? '#182030' : '#FFFFFF',
                  borderColor: darkMode ? 'rgba(255, 255, 255, 0.15)' : '#E3D7BD',
                  color: darkMode ? '#F1F5F9' : '#0F172A'
                }}
              />
              <div className="absolute right-2.5 flex items-center gap-1.5">
                {searchTerm && (
                  <button
                    type="button"
                    onClick={() => {
                      setSearchTerm('');
                      searchInputRef.current?.focus();
                    }}
                    className="p-1 rounded-md text-slate-400 hover:text-slate-200 cursor-pointer"
                    title="Limpar busca"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                <span className="hidden sm:inline-block text-[10px] font-mono px-1.5 py-0.5 rounded border border-slate-500/20 text-slate-400 bg-slate-500/5">
                  ↵ Enter
                </span>
              </div>
            </div>
          </div>

          {/* CHIPS DE FILTRO DE TIPO: TODOS / PEDIÁTRICO / ADULTO / CONTROLE ESPECIAL */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5 scrollbar-none fade-scroll-x">
            {[
              { id: 'todos', label: 'Todos' },
              { id: 'pediatric', label: 'Pediátricos (Dose/kg)' },
              { id: 'adult', label: 'Adultos' },
              { id: 'special', label: 'Controle Especial' }
            ].map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setTypeFilter(f.id as any)}
                className={`text-[11px] font-bold px-3 py-1.5 rounded-xl whitespace-nowrap transition-all cursor-pointer border ${
                  typeFilter === f.id
                    ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                    : darkMode
                    ? 'bg-slate-800/80 text-slate-300 border-slate-700/80 hover:bg-slate-700'
                    : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
                }`}
              >
                {f.label}
              </button>
            ))}

            {hasWeight && (
              <div className="ml-auto flex items-center gap-1 text-[11px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-xl whitespace-nowrap flex-shrink-0">
                <Scale className="w-3.5 h-3.5" />
                <span>{patientName.split(' ')[0]}: {patientWeight} kg</span>
              </div>
            )}
          </div>

          {/* FILTRO DE CLASSE TERAPÊUTICA / CATEGORIA */}
          <div className="flex items-center gap-1 overflow-x-auto pb-0.5 scrollbar-none text-xs fade-scroll-x">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1 pr-1 flex-shrink-0">
              <Tag className="w-3 h-3 text-sky-500" />
              <span>Classe:</span>
            </span>

            {popularClasses.map((pc) => {
              const isSelected = selectedTherapeuticClass === pc.id;
              return (
                <button
                  key={pc.id}
                  type="button"
                  onClick={() => setSelectedTherapeuticClass(pc.id)}
                  className={`text-[10px] font-semibold px-2.5 py-1 rounded-lg border whitespace-nowrap transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-sky-700 text-white border-sky-600 font-bold shadow-xs'
                      : darkMode
                      ? 'bg-slate-800/60 text-slate-300 border-slate-700/60 hover:bg-slate-700 hover:text-white'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {pc.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* LISTA DE RESULTADOS RANQUEADOS POR RELEVÂNCIA FUZZY */}
        <div
          ref={listContainerRef}
          className="p-3 sm:p-4 overflow-y-auto space-y-2.5 flex-1 max-h-[500px]"
        >
          {searchResults.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs space-y-3">
              <Pill className="w-10 h-10 mx-auto text-slate-300 dark:text-slate-600" strokeWidth={1.5} />
              <div>
                <p className="font-bold text-sm text-slate-600 dark:text-slate-300">
                  Nenhum fármaco encontrado para "{searchTerm}"
                </p>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Tente digitar partes do nome (ex: "dipr", "amox", "parac"), a classe (ex: "antibiotico", "dor", "febre") ou limpe os filtros.
                </p>
              </div>

              <div className="flex items-center justify-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setSearchTerm('');
                    setTypeFilter('todos');
                    setSelectedTherapeuticClass('todos');
                  }}
                  className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-500/10 hover:bg-slate-500/20 text-slate-600 dark:text-slate-300 transition-colors cursor-pointer"
                >
                  Limpar todos os filtros
                </button>
              </div>
            </div>
          ) : (
            searchResults.map((res, index) => {
              const isSelected = index === selectedIndex;
              const group = res.group;

              return (
                <div
                  key={group.id}
                  data-index={index}
                  onClick={() => {
                    onSelectGroup(group);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 group relative ${
                    isSelected
                      ? 'border-sky-500 bg-sky-500/10 ring-2 ring-sky-500/25 shadow-md'
                      : darkMode
                      ? 'bg-slate-800/40 hover:bg-slate-800/80 border-slate-700/60'
                      : 'bg-slate-50 hover:bg-slate-100 border-slate-200'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    {/* Linha 1: Nome do Medicamento + Badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className="font-bold text-xs sm:text-sm tracking-tight"
                        style={{ color: darkMode ? '#F1F5F9' : '#0B132B' }}
                      >
                        {group.baseName}
                      </span>

                      {group.hasPediatric && (
                        <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25">
                          Pediátrico
                        </span>
                      )}
                      {group.hasAdult && (
                        <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-sky-500/15 text-sky-700 dark:text-sky-400 border border-sky-500/25">
                          Adulto
                        </span>
                      )}
                      {group.isSpecialControl && (
                        <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/25">
                          Controle Especial
                        </span>
                      )}
                    </div>

                    {/* Linha 2: Princípio Ativo e Classe Terapêutica */}
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5 truncate">
                      {group.activeIngredient} • <span className="font-bold text-sky-600 dark:text-sky-400">{group.category}</span>
                    </div>

                    {/* Linha 3: Marcas comerciais (se houver) */}
                    {group.tradeNames.length > 0 && (
                      <div className="text-[10px] text-slate-400 font-medium mt-0.5 truncate">
                        Marcas: {group.tradeNames.join(', ')}
                      </div>
                    )}

                    {/* Linha 4: Motivo do match fuzzy + quantidade de apresentações */}
                    <div className="flex items-center gap-2 flex-wrap mt-1.5">
                      {searchTerm && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-sky-500/15 text-sky-700 dark:text-sky-300 flex items-center gap-1">
                          <Sparkles className="w-2.5 h-2.5 text-sky-500" />
                          <span>{res.matchedHighlight}</span>
                        </span>
                      )}

                      <span className="text-[10px] font-semibold text-slate-400 flex items-center gap-1">
                        <Layers className="w-3 h-3" />
                        <span>{group.options.length} {group.options.length === 1 ? 'apresentação' : 'apresentações'}</span>
                      </span>
                    </div>
                  </div>

                  {/* Botão de Escolher Apresentação */}
                  <div className="flex items-center gap-2 self-end sm:self-center flex-shrink-0">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectGroup(group);
                        onClose();
                      }}
                      className="btn-tactile-primary px-3.5 py-2 min-h-[38px] rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer transition-all active:scale-95 shadow-sm"
                    >
                      <span>Apresentações</span>
                      <ArrowRight className="w-3.5 h-3.5" strokeWidth={2.5} />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* RODAPÉ DO MODAL COM DICAS E ATALHOS */}
        <div
          className="p-3.5 sm:p-4 border-t flex items-center justify-between gap-3 flex-shrink-0 text-xs text-slate-400"
          style={{
            backgroundColor: darkMode ? '#141E2C' : '#F8F4EC',
            borderColor: darkMode ? 'rgba(255,255,255,0.08)' : '#E3D7BD'
          }}
        >
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              {searchResults.length} {searchResults.length === 1 ? 'medicamento encontrado' : 'medicamentos encontrados'}
            </span>
            {searchTerm && (
              <span className="hidden sm:inline text-[11px] text-sky-600 dark:text-sky-400">
                (classificados por pontuação de busca difusa)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 min-h-[36px] rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 cursor-pointer transition-colors"
            >
              Fechar (Esc)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
