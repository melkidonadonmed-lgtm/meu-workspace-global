import React, { useEffect, useRef } from 'react';
import { AlertTriangle, X, Check } from 'lucide-react';

export interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  darkMode: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  description,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  variant = 'danger',
  darkMode,
  onConfirm,
  onCancel
}) => {
  const confirmButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Foco no botão de confirmação e listener de Escape
      confirmButtonRef.current?.focus();
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onCancel();
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  const isDanger = variant === 'danger';

  return (
    <div 
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-tab-fade"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      aria-describedby="confirm-modal-desc"
      onClick={onCancel}
    >
      <div 
        className="w-full max-w-md rounded-2xl p-6 relative border shadow-tactile-lg isolate transition-all"
        style={{
          backgroundColor: darkMode ? '#0E1420' : '#FFFFFF',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.12)' : '#E3D7BD',
          boxShadow: darkMode 
            ? '0 24px 50px -8px rgba(0, 0, 0, 0.85), inset 0 1px 0 rgba(255,255,255,0.1)' 
            : '0 20px 40px -8px rgba(20, 32, 50, 0.18), inset 0 1px 0 rgba(255,255,255,0.95)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-4">
          <div 
            className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 border ${
              isDanger 
                ? 'bg-rose-500/15 text-rose-500 border-rose-500/30' 
                : 'bg-navy-900/10 text-navy-900 dark:bg-cream-100/15 dark:text-cream-100 border-navy-900/20 dark:border-cream-100/25'
            }`}
          >
            <AlertTriangle className="w-6 h-6" />
          </div>

          <div className="flex-1 min-w-0">
            <h3 
              id="confirm-modal-title" 
              className="text-base font-bold text-navy-900 dark:text-cream-50"
            >
              {title}
            </h3>
            <p 
              id="confirm-modal-desc" 
              className="mt-1.5 text-xs sm:text-sm leading-relaxed text-slate-600 dark:text-slate-300"
            >
              {description}
            </p>
          </div>

          <button
            onClick={onCancel}
            aria-label="Fechar modal de confirmação"
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-slate-200 dark:border-white/10">
          <button
            type="button"
            onClick={onCancel}
            className="min-h-[44px] px-4 py-2 text-xs sm:text-sm font-semibold rounded-xl border border-slate-300 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/5 text-slate-700 dark:text-slate-300 transition-all cursor-pointer"
          >
            {cancelLabel}
          </button>

          <button
            ref={confirmButtonRef}
            type="button"
            onClick={onConfirm}
            className={`min-h-[44px] px-5 py-2 text-xs sm:text-sm font-bold rounded-xl shadow-tactile-btn flex items-center gap-2 cursor-pointer transition-all active:scale-95 ${
              isDanger 
                ? 'bg-rose-600 hover:bg-rose-700 active:bg-rose-800 text-white' 
                : 'bg-navy-900 hover:bg-navy-950 text-white dark:bg-cream-100 dark:hover:bg-white dark:text-navy-950'
            }`}
          >
            <Check className="w-4 h-4" />
            <span>{confirmLabel}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
