import React, { useState, useRef, useEffect } from 'react';
import { Search, X, Check, Tag, Sparkles, Filter, AlertCircle, ChevronDown } from 'lucide-react';
import { 
  CIDItem, 
  CID_CATEGORIES, 
  CIDCategoryType, 
  searchCID10, 
  COMMON_CID10 
} from '../data/cidCatalog';

interface CidSearchBarProps {
  darkMode: boolean;
  selectedCode?: string;
  selectedDescription?: string;
  onSelectCid: (cid: { code: string; description: string; category?: string }) => void;
  onClearCid?: () => void;
  label?: string;
  placeholder?: string;
  showQuickChips?: boolean;
  allowCustomEntry?: boolean;
  variant?: 'certificate' | 'referral';
  onAppendCid?: (cid: { code: string; description: string }) => void;
}

export const CidSearchBar: React.FC<CidSearchBarProps> = ({
  darkMode,
  selectedCode = '',
  selectedDescription = '',
  onSelectCid,
  onClearCid,
  label = 'Buscador de Diagnóstico & Código CID-10',
  placeholder = 'Digite o diagnóstico ou código (ex: Asma, Lombalgia, J00, Dengue, A09, Cefaleia, ITU)...',
  showQuickChips = true,
  allowCustomEntry = true,
  variant = 'certificate',
  onAppendCid
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<CIDCategoryType>('Todos');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const results = searchCID10(searchTerm, selectedCategory);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item: CIDItem) => {
    onSelectCid({
      code: item.code,
      description: item.description,
      category: item.category
    });
    setSearchTerm('');
    setIsOpen(false);
  };

  const handleAppend = (item: CIDItem, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onAppendCid) {
      onAppendCid({
        code: item.code,
        description: item.description
      });
    } else {
      handleSelect(item);
    }
  };

  const handleCustomSubmit = () => {
    if (!searchTerm.trim()) return;
    const cleanTerm = searchTerm.trim();
    // Try to detect if first word is a CID code like "J00" or "M54.5"
    const codeMatch = cleanTerm.match(/^([A-Z][0-9]{2}(?:\.[0-9]{1,2})?)\s*[-:]?\s*(.*)$/i);
    if (codeMatch) {
      onSelectCid({
        code: codeMatch[1].toUpperCase(),
        description: codeMatch[2] || cleanTerm
      });
    } else {
      onSelectCid({
        code: cleanTerm.length <= 6 && /^[a-z0-9.]+$/i.test(cleanTerm) ? cleanTerm.toUpperCase() : 'CID',
        description: cleanTerm
      });
    }
    setSearchTerm('');
    setIsOpen(false);
  };

  // Top quick suggestions
  const quickPicks: CIDItem[] = [
    { code: 'J00', description: 'Nasofaringite (Resfriado)', category: 'Respiratório' },
    { code: 'J06.9', description: 'IVAS', category: 'Respiratório' },
    { code: 'A09', description: 'Gastroenterite / Diarreia', category: 'Digestivo' },
    { code: 'M54.5', description: 'Lombalgia', category: 'Osteomuscular' },
    { code: 'A90', description: 'Dengue clássico', category: 'Infecciosas' },
    { code: 'J03.9', description: 'Amigdalite aguda', category: 'Respiratório' },
    { code: 'N39.0', description: 'ITU (Infecção urinária)', category: 'Geniturinário' },
    { code: 'F41.1', description: 'Ansiedade (TAG)', category: 'Saúde Mental' },
    { code: 'R51', description: 'Cefaleia', category: 'Sintomas' },
    { code: 'Z76.0', description: 'Receita repetição', category: 'Admin' }
  ];

  const accentColor = variant === 'referral' ? 'emerald' : 'sky';

  return (
    <div ref={containerRef} className="space-y-2.5">
      {/* Label and Helper Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <label className="text-xs font-bold uppercase tracking-wide flex items-center gap-1.5" style={{ color: darkMode ? '#94A3B8' : '#475569' }}>
          <Search className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
          <span>{label}</span>
        </label>
        <span className="text-[11px] font-medium text-slate-400">
          Pesquisa inteligente por código ou termo diagnóstico
        </span>
      </div>

      {/* Selected CID Visual Summary Card (if present and in single selection mode) */}
      {selectedCode && (
        <div 
          className="p-3 rounded-xl border flex items-start justify-between gap-3 transition-all animate-fadeIn"
          style={{
            backgroundColor: darkMode ? '#161A21' : '#F0F7FF',
            borderColor: darkMode ? 'rgba(56, 142, 230, 0.3)' : 'rgba(15, 98, 146, 0.25)'
          }}
        >
          <div className="flex items-start gap-2.5 min-w-0">
            <span 
              className={`px-2.5 py-1 rounded-lg text-xs font-black tracking-wider flex-shrink-0 ${
                variant === 'referral'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-sky-700 dark:bg-sky-600 text-white shadow-sm'
              }`}
            >
              {selectedCode}
            </span>
            <div className="min-w-0">
              <p className="text-xs sm:text-sm font-bold truncate leading-tight" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                {selectedDescription || 'Diagnóstico selecionado'}
              </p>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Código CID-10 preenchido automaticamente no documento
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 flex-shrink-0">
            <button
              type="button"
              onClick={() => {
                setIsOpen(true);
                inputRef.current?.focus();
              }}
              className="text-[11px] font-bold px-2.5 py-1 rounded-lg border hover:bg-slate-500/10 cursor-pointer transition-colors"
              style={{
                borderColor: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.1)',
                color: darkMode ? '#93C5FD' : '#0369A1'
              }}
            >
              Trocar
            </button>

            {onClearCid && (
              <button
                type="button"
                onClick={onClearCid}
                title="Remover CID selecionado"
                className="p-1 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main Search Input & Trigger Box */}
      <div className="relative">
        <div className="relative flex items-center">
          <div className="absolute left-3 pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className="w-full pl-9 pr-20 py-2.5 rounded-xl border text-xs sm:text-sm font-medium focus:outline-none focus:ring-2 focus:ring-sky-500/40 tactile-input transition-all"
            style={{
              backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--surface-card)',
              borderColor: isOpen 
                ? (darkMode ? '#388EE6' : '#0F6292') 
                : (darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.1)'),
              color: darkMode ? '#F1F5F9' : '#0F172A'
            }}
          />

          <div className="absolute right-2 flex items-center gap-1">
            {searchTerm && (
              <button
                type="button"
                onClick={() => {
                  setSearchTerm('');
                  inputRef.current?.focus();
                }}
                className="p-1 rounded-md text-slate-400 hover:text-slate-200 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="p-1 rounded-md text-slate-400 hover:text-slate-200 cursor-pointer"
              title="Abrir catálogo completo"
            >
              <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>

        {/* Dropdown Floating Results Panel */}
        {isOpen && (
          <div 
            className="absolute z-30 top-full left-0 right-0 mt-1.5 rounded-2xl border shadow-2xl overflow-hidden animate-slideDown"
            style={{
              backgroundColor: darkMode ? 'var(--surface-card)' : 'var(--surface-card)',
              borderColor: darkMode ? 'rgba(255,255,255,0.12)' : 'rgba(15,23,42,0.12)',
              boxShadow: darkMode 
                ? '0 20px 30px -10px rgba(0,0,0,0.8), 0 0 1px 1px rgba(255,255,255,0.05)'
                : '0 20px 30px -10px rgba(15,23,42,0.15), 0 0 1px 1px rgba(15,23,42,0.05)'
            }}
          >
            {/* Category Filter Pills in Dropdown Header */}
            <div 
              className="p-2 border-b overflow-x-auto flex items-center gap-1.5 scrollbar-none"
              style={{
                backgroundColor: darkMode ? 'var(--surface-inset)' : '#FAF7F1',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
              }}
            >
              <div className="flex items-center gap-1 text-[10px] font-bold uppercase text-slate-400 pl-1 pr-1 flex-shrink-0">
                <Filter className="w-3 h-3" />
                <span>Filtro:</span>
              </div>

              {CID_CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`text-[11px] px-2.5 py-1 rounded-lg font-semibold whitespace-nowrap transition-all cursor-pointer ${
                    selectedCategory === cat
                      ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 font-bold shadow-tactile-navy dark:shadow-tactile-cream'
                      : darkMode
                      ? 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
                      : 'bg-white text-slate-600 hover:bg-slate-200/70 border border-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* List Results */}
            <div className="max-h-64 sm:max-h-72 overflow-y-auto divide-y divide-slate-500/10">
              {results.length > 0 ? (
                results.map((item) => {
                  const isCurrent = selectedCode.toUpperCase() === item.code.toUpperCase();
                  return (
                    <div
                      key={item.code}
                      onClick={() => handleSelect(item)}
                      className={`p-2.5 sm:p-3 flex items-center justify-between gap-3 cursor-pointer transition-colors group ${
                        isCurrent 
                          ? (darkMode ? 'bg-sky-950/40' : 'bg-sky-50') 
                          : 'hover:bg-slate-500/10'
                      }`}
                    >
                      <div className="flex items-start gap-2.5 min-w-0">
                        <span 
                          className={`px-2 py-0.5 rounded-md font-mono font-bold text-xs flex-shrink-0 ${
                            isCurrent
                              ? 'bg-sky-600 text-white'
                              : darkMode
                              ? 'bg-slate-800 text-sky-400 group-hover:bg-sky-900/50 group-hover:text-sky-300'
                              : 'bg-sky-100 text-sky-800 group-hover:bg-sky-200'
                          }`}
                        >
                          {item.code}
                        </span>

                        <div className="min-w-0">
                          <p className="text-xs sm:text-sm font-semibold leading-snug" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                            {item.description}
                          </p>
                          {item.keywords && item.keywords.length > 0 && (
                            <p className="text-[10px] text-slate-400 truncate mt-0.5">
                              Termos: {item.keywords.slice(0, 3).join(', ')}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-500/10 text-slate-400 hidden sm:inline-block">
                          {item.category}
                        </span>

                        {onAppendCid && (
                          <button
                            type="button"
                            onClick={(e) => handleAppend(item, e)}
                            className="text-[10px] font-bold px-2 py-1 rounded bg-emerald-600/20 text-emerald-500 hover:bg-emerald-600 hover:text-white transition-colors cursor-pointer"
                            title="Inserir na hipótese"
                          >
                            + Inserir
                          </button>
                        )}

                        {isCurrent && (
                          <span className="text-sky-600 dark:text-sky-400">
                            <Check className="w-4 h-4" />
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="p-6 text-center space-y-3">
                  <p className="text-xs text-slate-400">
                    Nenhum código CID-10 encontrado para "<span className="font-semibold text-slate-200">{searchTerm}</span>".
                  </p>

                  {allowCustomEntry && searchTerm && (
                    <button
                      type="button"
                      onClick={handleCustomSubmit}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow cursor-pointer active:scale-95 transition-all"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Usar diagnóstico digitado "{searchTerm}"</span>
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Footer summary & manual action */}
            <div 
              className="p-2.5 border-t text-[11px] flex items-center justify-between text-slate-400"
              style={{
                backgroundColor: darkMode ? 'var(--surface-inset)' : '#FAF7F1',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
              }}
            >
              <span>{results.length} resultados no catálogo</span>

              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:underline cursor-pointer"
              >
                Fechar catálogo
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Quick Picks / Top Diagnósticos Bar */}
      {showQuickChips && (
        <div className="space-y-1.5 pt-0.5">
          <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            <Tag className="w-3 h-3 text-sky-500" />
            <span>Diagnósticos Mais Frequentes (1 clique):</span>
          </div>

          <div className="flex items-center gap-1.5 flex-wrap">
            {quickPicks.map((pick) => {
              const isSelected = selectedCode.toUpperCase() === pick.code.toUpperCase();
              return (
                <button
                  key={pick.code}
                  type="button"
                  onClick={() => onSelectCid({ code: pick.code, description: pick.description, category: pick.category })}
                  className={`text-[11px] px-2.5 py-1 rounded-lg border font-medium transition-all cursor-pointer active:scale-95 flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-sky-700 text-white border-sky-600 font-bold shadow-xs'
                      : darkMode
                      ? 'bg-slate-800/60 text-slate-300 border-slate-700/60 hover:bg-slate-700 hover:text-white'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-sky-50 hover:border-sky-300'
                  }`}
                  title={`${pick.code} - ${pick.description}`}
                >
                  <span className="font-mono font-bold text-sky-500 dark:text-sky-400 text-[10px]">{pick.code}</span>
                  <span className="truncate max-w-[150px]">{pick.description.split('(')[0].trim()}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
