import React, { useState } from 'react';
import { 
  FileEdit, 
  Calculator, 
  FlaskConical, 
  Award, 
  Share2, 
  Download, 
  Users, 
  Stethoscope, 
  HeartPulse, 
  ChevronLeft, 
  ChevronRight, 
  X, 
  Trash2, 
  UserX, 
  RotateCcw, 
  Pencil, 
  Sun, 
  Moon, 
  UserPlus, 
  UserCheck 
} from 'lucide-react';
import { ActiveTab, DoctorProfile, Patient } from '../types';
import { ConfirmationModal } from './ConfirmationModal';

interface SidebarProps {
  darkMode: boolean;
  onToggleDarkMode?: () => void;
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  isOpen: boolean;
  onToggleOpen: () => void;
  onClose?: () => void;
  doctor?: DoctorProfile;
  patient?: Patient;
  prescriptionCount?: number;
  selectedExamsCount?: number;
  onOpenDoctorModal?: () => void;
  onOpenPatientModal?: () => void;
  onClearPrescription?: () => void;
  onClearPatient?: () => void;
  onResetAll?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  darkMode,
  onToggleDarkMode,
  activeTab,
  onSelectTab,
  isOpen,
  onToggleOpen,
  onClose,
  doctor,
  patient,
  prescriptionCount = 0,
  selectedExamsCount = 0,
  onOpenDoctorModal,
  onOpenPatientModal,
  onClearPrescription,
  onClearPatient,
  onResetAll
}) => {
  const patientWeight = patient?.weightKg && patient.weightKg > 0 ? patient.weightKg : 0;
  const hasPatient = Boolean(patient?.name?.trim());
  const patientName = patient?.name?.trim() || '';
  const hasDoctor = Boolean(doctor?.name?.trim());

  // Estado do Modal de Confirmação HITL para Ações Destrutivas
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    title: string;
    description: string;
    confirmLabel: string;
    variant: 'danger' | 'warning';
    onConfirm: () => void;
  }>({
    isOpen: false,
    title: '',
    description: '',
    confirmLabel: 'Confirmar',
    variant: 'danger',
    onConfirm: () => {}
  });

  const handleTriggerClearPrescription = () => {
    setConfirmModal({
      isOpen: true,
      title: 'Zerar Receita Atual?',
      description: 'Esta ação removerá todos os medicamentos prescritos na receita atual. Os dados do paciente e exames serão preservados.',
      confirmLabel: 'Zerar Receita',
      variant: 'danger',
      onConfirm: () => {
        onClearPrescription?.();
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
      }
    });
  };

  const handleTriggerClearPatient = () => {
    setConfirmModal({
      isOpen: true,
      title: 'Limpar Dados do Paciente?',
      description: 'Esta ação resetará o nome, peso, idade e dados cadastrais do paciente em atendimento.',
      confirmLabel: 'Limpar Paciente',
      variant: 'danger',
      onConfirm: () => {
        onClearPatient?.();
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
      }
    });
  };

  const handleTriggerResetAll = () => {
    setConfirmModal({
      isOpen: true,
      title: 'Iniciar Novo Atendimento Completo?',
      description: 'Esta ação limpará todas as receitas, os exames selecionados e os dados cadastrais do paciente atual para iniciar uma nova consulta do zero.',
      confirmLabel: 'Iniciar Novo Atendimento',
      variant: 'warning',
      onConfirm: () => {
        onResetAll?.();
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
      }
    });
  };

  const primaryNavItems = [
    {
      id: 'prescription' as ActiveTab,
      label: 'Receitas Médicas',
      shortLabel: 'Receitas',
      icon: FileEdit,
      badge: prescriptionCount > 0 ? `${prescriptionCount}` : undefined
    },
    {
      id: 'pediatric_calc' as ActiveTab,
      label: 'Calculadora Pediátrica',
      shortLabel: 'Doses',
      icon: Calculator,
      badge: patientWeight > 0 ? `${patientWeight}kg` : undefined
    },
    {
      id: 'exams' as ActiveTab,
      label: 'Exames',
      fullLabel: 'Solicitação de Exames',
      shortLabel: 'Exames',
      icon: FlaskConical,
      badge: selectedExamsCount > 0 ? `${selectedExamsCount}` : undefined
    },
    {
      id: 'certificate' as ActiveTab,
      label: 'Atestados',
      fullLabel: 'Atestados (padrão CFM)',
      shortLabel: 'Atestado',
      icon: Award
    },
    {
      id: 'referral' as ActiveTab,
      label: 'Encaminhamentos',
      shortLabel: 'Encam.',
      icon: Share2
    },
    {
      id: 'protocols' as ActiveTab,
      label: 'Protocolos Clínicos',
      shortLabel: 'Protocolos',
      icon: HeartPulse
    },
    {
      id: 'print_preview' as ActiveTab,
      label: 'Exportar & Baixar PDF',
      shortLabel: 'Exportar',
      icon: Download
    }
  ];

  const renderNavButton = (item: { id: ActiveTab; label: string; fullLabel?: string; shortLabel: string; icon: React.ElementType; badge?: string }) => {
    const Icon = item.icon;
    const isActive = activeTab === item.id;

    if (!isOpen) {
      return (
        <button
          key={item.id}
          id={`nav-btn-${item.id}`}
          type="button"
          onClick={() => onSelectTab(item.id)}
          aria-current={isActive ? 'page' : undefined}
          className={`w-full h-14 mx-auto rounded-xl flex flex-col items-center justify-center gap-0.5 px-1 transition-all cursor-pointer group active:scale-95 focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none relative ${
            isActive
              ? 'bg-navy-950 text-cream-50 border border-white/20 shadow-tactile-navy dark:bg-cream-100 dark:text-navy-950 dark:border-white/30 dark:shadow-tactile-cream font-extrabold'
              : 'text-slate-300 hover:bg-white/10 hover:text-white'
          }`}
          title={item.fullLabel || item.label}
        >
          <Icon
            className={`w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110 ${
              isActive ? 'text-cream-50 dark:text-navy-950' : 'text-slate-400 group-hover:text-cream-100 dark:group-hover:text-cream-300'
            }`}
            strokeWidth={isActive ? 2.2 : 1.75}
          />
          <span className={`text-[8px] font-bold leading-none truncate max-w-full ${
            isActive ? 'text-cream-50 dark:text-navy-950' : 'text-slate-400 group-hover:text-cream-100'
          }`}>
            {item.shortLabel}
          </span>
          {item.badge && (
            <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-white/25 text-white dark:bg-navy-950 dark:text-cream-100 text-[9px] font-black flex items-center justify-center shadow-sm border border-white/20 dark:border-navy-800">
              {item.badge}
            </span>
          )}
        </button>
      );
    }

    return (
      <button
        key={item.id}
        id={`nav-btn-${item.id}`}
        type="button"
        onClick={() => onSelectTab(item.id)}
        aria-current={isActive ? 'page' : undefined}
        className={`w-full min-h-[44px] flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer group active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none ${
          isActive
            ? 'bg-navy-950 text-cream-50 border border-white/20 shadow-tactile-navy dark:bg-cream-100 dark:text-navy-950 dark:border-white/30 dark:shadow-tactile-cream font-extrabold'
            : 'text-slate-300 hover:bg-white/5 hover:text-white'
        }`}
        title={item.label}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <Icon 
            className={`w-4 h-4 flex-shrink-0 transition-transform group-hover:scale-110 ${
              isActive ? 'text-cream-50 dark:text-navy-950' : 'text-slate-400 group-hover:text-cream-100 dark:group-hover:text-cream-300'
            }`} 
            strokeWidth={isActive ? 2.2 : 1.75} 
          />
          <span className="truncate">
            {item.label}
          </span>
        </div>
        {item.badge && (
          <span 
            className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded-full flex-shrink-0 ml-1.5 ${
              isActive ? 'bg-white/20 text-cream-50 dark:bg-navy-900 dark:text-cream-100' : 'bg-white/10 text-slate-300'
            }`}
          >
            {item.badge}
          </span>
        )}
      </button>
    );
  };

  return (
    <>
      {/* Overlay Backdrop on Mobile */}
      {isOpen && (
        <div 
          onClick={onClose || onToggleOpen}
          aria-label="Fechar menu lateral"
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs lg:hidden transition-opacity cursor-pointer"
        />
      )}

      <aside
        id="prescmed-sidebar"
        aria-label="Menu Lateral de Navegação"
        className={`fixed lg:sticky top-[68px] sm:top-[72px] left-0 h-[calc(100dvh-68px)] sm:h-[calc(100dvh-72px)] z-40 flex flex-col flex-shrink-0 transition-all duration-300 no-print rounded-r-2xl lg:rounded-2xl border ${
          isOpen ? 'w-64 sm:w-72 shadow-tactile-navy' : 'w-0 lg:w-[72px] overflow-hidden'
        }`}
        style={{
          backgroundColor: darkMode ? '#0A0F18' : '#142032',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.1)',
          boxShadow: darkMode
            ? '0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.08)'
            : '0 14px 32px rgba(10, 17, 28, 0.35), inset 0 1px 0 rgba(255,255,255,0.15)'
        }}
      >
        <div className={`overflow-y-auto flex-1 custom-scrollbar ${
          isOpen ? 'p-3 space-y-4' : 'py-3 px-2 space-y-3 flex flex-col items-center'
        }`}>
          
          {/* Mobile Header with Close Button */}
          <div className="flex items-center justify-between pb-2 border-b border-white/10 lg:hidden">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-400">
              Menu de Navegação
            </span>
            <button
              onClick={onClose || onToggleOpen}
              aria-label="Fechar menu lateral"
              className="w-10 h-10 min-w-[40px] min-h-[40px] rounded-lg flex items-center justify-center text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Doctor Profile Badge */}
          {isOpen ? (
            <div
              onClick={onOpenDoctorModal}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onOpenDoctorModal?.();
                }
              }}
              role="button"
              tabIndex={0}
              className="p-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all cursor-pointer group active:scale-95 shadow-tactile-inset focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none min-h-[44px]"
              title="Clique para editar CRM e dados profissionais"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-navy-950 text-cream-100 border border-white/15 dark:bg-cream-100 dark:text-navy-950 dark:border-white/25 flex items-center justify-center font-black text-xs shadow-tactile-btn shrink-0">
                  CRM
                </div>
                <div className="overflow-hidden min-w-0 flex-1">
                  <p className="text-xs font-bold truncate text-cream-50">
                    {hasDoctor ? doctor?.name : 'Configurar Médico'}
                  </p>
                  <p className="text-[10px] text-slate-400 font-medium truncate">
                    {hasDoctor 
                      ? `CRM: ${doctor?.crm}/${doctor?.crmState || 'SP'} ${doctor?.rqe ? '• RQE ' + doctor.rqe : ''}` 
                      : 'Toque para preencher'}
                  </p>
                </div>
              </div>
              <button 
                type="button"
                className="mt-2 w-full py-1.5 min-h-[36px] text-[10px] font-bold text-cream-100 hover:text-white dark:text-navy-900 dark:hover:text-navy-950 text-center rounded-lg bg-white/10 hover:bg-white/20 dark:bg-cream-100 dark:hover:bg-white border border-white/10 dark:border-white/20 transition cursor-pointer shadow-tactile-sm"
              >
                Editar Perfil Médico
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenDoctorModal}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onOpenDoctorModal?.();
                }
              }}
              className="w-11 h-11 mx-auto rounded-xl bg-navy-950 text-cream-100 border border-white/15 dark:bg-cream-100 dark:text-navy-950 dark:border-white/25 hover:bg-navy-900 dark:hover:bg-white font-black text-xs flex items-center justify-center shadow-tactile-btn transition-all active:scale-95 cursor-pointer focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none"
              title={hasDoctor ? `Dr(a). ${doctor?.name} (CRM: ${doctor?.crm}/${doctor?.crmState})` : 'Configurar CRM / Perfil Médico'}
              aria-label="Perfil do Médico"
            >
              CRM
            </button>
          )}

          {/* Navigation Items */}
          <div className={isOpen ? 'w-full' : 'w-full flex flex-col items-center'}>
            {isOpen && (
              <p className="text-[9px] font-extrabold uppercase tracking-widest text-slate-400 px-2 mb-1.5">
                Navegação Principal
              </p>
            )}
            <nav className={isOpen ? 'space-y-1' : 'space-y-2 w-full flex flex-col items-center'}>
              {primaryNavItems.map(renderNavButton)}
            </nav>
          </div>

          {/* Active Patient Badge */}
          {isOpen ? (
            <div
              onClick={onOpenPatientModal}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onOpenPatientModal?.();
                }
              }}
              role="button"
              tabIndex={0}
              className="p-2.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all cursor-pointer group active:scale-95 shadow-tactile-inset focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none min-h-[44px]"
              title="Clique para editar paciente"
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">
                  <Users className="w-3.5 h-3.5" />
                </div>
                <div className="overflow-hidden min-w-0 flex-1">
                  <p className="text-[9px] font-extrabold uppercase tracking-wider text-slate-400">
                    Paciente em Atendimento
                  </p>
                  <p className="text-xs font-bold truncate text-white">
                    {hasPatient ? patientName : 'Não identificado'}
                  </p>
                  <p className="text-[10px] font-semibold text-emerald-400">
                    {patientWeight > 0 ? `${patientWeight} kg` : 'Sem peso'} {patient?.ageText ? `• ${patient.ageText}` : ''}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenPatientModal}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onOpenPatientModal?.();
                }
              }}
              className="w-11 h-11 mx-auto rounded-xl bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30 flex items-center justify-center transition-all active:scale-95 cursor-pointer focus-visible:ring-2 focus-visible:ring-emerald-500 outline-none shadow-tactile-sm"
              title={hasPatient ? `Paciente: ${patientName} (${patientWeight ? patientWeight + 'kg' : 'sem peso'})` : 'Definir / Identificar Paciente'}
              aria-label="Dados do Paciente"
            >
              <Users className="w-5 h-5" />
            </button>
          )}

          {/* Quick Actions (Limpeza / Novo Atendimento) */}
          {isOpen && (
            <div className="space-y-1.5 pt-2 border-t border-white/10">
              <p className="text-[9px] font-extrabold uppercase tracking-widest text-slate-400 px-2 mb-1">
                Ações Rápidas
              </p>
              
              {/* Zerar Receita */}
              <button
                type="button"
                onClick={handleTriggerClearPrescription}
                className="w-full min-h-[44px] flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-rose-400 hover:bg-rose-500/10 transition cursor-pointer focus-visible:ring-2 focus-visible:ring-rose-500 outline-none"
              >
                <Trash2 className="w-4 h-4 shrink-0 text-rose-400/80" />
                <span>Zerar Receita Atual</span>
              </button>

              {/* Limpar Paciente */}
              <button
                type="button"
                onClick={handleTriggerClearPatient}
                className="w-full min-h-[44px] flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-rose-400 hover:bg-rose-500/10 transition cursor-pointer focus-visible:ring-2 focus-visible:ring-rose-500 outline-none"
              >
                <UserX className="w-4 h-4 shrink-0 text-rose-400/80" />
                <span>Limpar Paciente</span>
              </button>

              {/* Novo Atendimento */}
              <button
                type="button"
                onClick={handleTriggerResetAll}
                className="w-full min-h-[44px] flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-sky-300 hover:text-sky-200 hover:bg-sky-500/10 dark:text-cream-100 dark:hover:text-white dark:hover:bg-white/10 transition cursor-pointer focus-visible:ring-2 focus-visible:ring-sky-500 dark:focus-visible:ring-cream-100 outline-none"
              >
                <RotateCcw className="w-4 h-4 shrink-0 text-sky-300 dark:text-cream-200" />
                <span>Novo Atendimento Completo</span>
              </button>
            </div>
          )}

          {/* Toggle Collapse on Desktop */}
          <div className="hidden lg:block pt-2 border-t border-white/10 w-full">
            <button
              type="button"
              onClick={onToggleOpen}
              className={`min-h-[40px] py-1.5 rounded-xl text-xs font-bold text-slate-400 hover:text-white hover:bg-white/10 flex items-center transition cursor-pointer active:scale-95 ${
                isOpen ? 'w-full justify-center gap-1.5 px-3' : 'w-11 h-11 mx-auto justify-center'
              }`}
              title={isOpen ? 'Recolher Menu Lateral' : 'Expandir Menu Lateral'}
            >
              {isOpen ? (
                <>
                  <ChevronLeft className="w-4 h-4" />
                  <span>Recolher Menu</span>
                </>
              ) : (
                <ChevronRight className="w-5 h-5" />
              )}
            </button>
          </div>

        </div>
      </aside>

      {/* Modal de Confirmação Zero-Trust HITL */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        title={confirmModal.title}
        description={confirmModal.description}
        confirmLabel={confirmModal.confirmLabel}
        variant={confirmModal.variant}
        darkMode={darkMode}
        onConfirm={confirmModal.onConfirm}
        onCancel={() => setConfirmModal(prev => ({ ...prev, isOpen: false }))}
      />
    </>
  );
};
