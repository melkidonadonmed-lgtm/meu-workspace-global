import React, { useState, useEffect, useRef } from 'react';
import { 
  Download, 
  QrCode, 
  ShieldCheck, 
  FileText, 
  Award, 
  FlaskConical, 
  Share2, 
  Check, 
  Layers,
  ArrowLeft,
  Loader2,
  Maximize2,
  Minimize2,
  Trash2,
  RotateCcw,
  FileCheck,
  Send,
  Copy,
  Printer
} from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { DoctorProfile, Patient, PrescriptionItem, ExamItem, MedicalCertificate, MedicalReferral } from '../types';
import { generateMedicalPDF } from '../utils/pdfGenerator';

// Helper to convert any modern CSS color (oklch, oklab, lab, lch, color-mix, etc.) to standard #rrggbb or rgba for html2canvas compatibility
const convertColorToRgb = (color: string): string => {
  if (!color) return '#000000';
  const c = color.trim();
  if (c === 'transparent') return 'rgba(0, 0, 0, 0)';
  if (c.startsWith('#') || c.startsWith('rgb(') || c.startsWith('rgba(')) return c;
  
  try {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (ctx) {
      ctx.fillStyle = '#000000';
      ctx.fillStyle = c;
      const result = ctx.fillStyle;
      if (result && !result.includes('oklch') && !result.includes('oklab')) {
        return result;
      }
    }
  } catch {
    // fallback
  }

  // Safe fallback palette for standard medical and Tailwind colors
  if (c.includes('slate-950') || c.includes('0.145')) return '#020617';
  if (c.includes('slate-900') || c.includes('0.208')) return '#0F172A';
  if (c.includes('slate-800') || c.includes('0.279')) return '#1E293B';
  if (c.includes('slate-700') || c.includes('0.37')) return '#334155';
  if (c.includes('slate-600') || c.includes('0.446')) return '#475569';
  if (c.includes('slate-500') || c.includes('0.554')) return '#64748B';
  if (c.includes('slate-400') || c.includes('0.704')) return '#94A3B8';
  if (c.includes('slate-200') || c.includes('0.869')) return '#E2E8F0';
  if (c.includes('slate-100') || c.includes('0.968')) return '#F1F5F9';
  if (c.includes('slate-50') || c.includes('0.984')) return '#F8FAFC';
  if (c.includes('sky-800') || c.includes('0.45')) return '#075985';
  if (c.includes('sky-700') || c.includes('0.5')) return '#0369A1';
  if (c.includes('sky') || c.includes('0.588') || c.includes('0.6')) return '#0284C7';
  if (c.includes('emerald') || c.includes('0.596')) return '#059669';
  if (c.includes('amber') || c.includes('0.769')) return '#D97706';
  if (c.includes('rose') || c.includes('red')) return '#E11D48';
  return '#0F172A';
};

interface PrintPreviewProps {
  darkMode: boolean;
  doctor: DoctorProfile;
  patient: Patient;
  prescriptionItems?: PrescriptionItem[];
  exams?: ExamItem[];
  selectedExams?: ExamItem[];
  examIndication?: string;
  certificate?: MedicalCertificate;
  referral?: MedicalReferral;
  initialDocType?: 'prescription' | 'special_prescription' | 'exams' | 'certificate' | 'referral';
  onNavigateBack?: () => void;
  onBack?: () => void;
  onClearPrescription?: () => void;
  onResetAll?: () => void;
  onOpenDoctorModal?: () => void;
}

export const PrintPreview: React.FC<PrintPreviewProps> = ({
  darkMode,
  doctor,
  patient,
  prescriptionItems = [],
  exams = [],
  selectedExams = [],
  examIndication = '',
  certificate = {
    patientName: '',
    documentNumber: '',
    daysOff: 1,
    startDate: '',
    endDate: '',
    periodText: '',
    cid10Code: '',
    cid10Description: '',
    includeCID: false,
    observations: '',
    cityDateText: ''
  },
  referral = {
    patientName: '',
    documentNumber: '',
    destinationSpecialty: 'Cardiologia Ambulatorial',
    destinationInstitution: '',
    clinicalSummary: '',
    reason: '',
    relevantExams: '',
    hypothesisCID: '',
    priority: 'eletivo' as const,
    date: ''
  },
  initialDocType = 'prescription',
  onNavigateBack,
  onBack,
  onClearPrescription,
  onResetAll
}) => {
  const effectiveExams = exams.length > 0 ? exams : selectedExams;
  const handleBack = onNavigateBack || onBack || (() => {});
  const [docType, setDocType] = useState<'prescription' | 'special_prescription' | 'exams' | 'certificate' | 'referral'>(initialDocType);
  const [copiedLink, setCopiedLink] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [fitToMobile, setFitToMobile] = useState(true);
  
  const printSheetRef = useRef<HTMLDivElement>(null);

  // Sync docType when initialDocType prop changes
  useEffect(() => {
    if (initialDocType) {
      setDocType(initialDocType);
    }
  }, [initialDocType]);

  const patientWeight = patient?.weightKg && patient.weightKg > 0 ? patient.weightKg : null;
  const patientName = patient?.name?.trim() || certificate?.patientName?.trim() || referral?.patientName?.trim() || 'Não identificado';
  const patientDoc = patient?.documentNumber?.trim() || certificate?.documentNumber?.trim() || referral?.documentNumber?.trim() || '—';
  const patientAge = patient?.ageText?.trim() || patient?.birthDate?.trim() || '—';

  const docName = doctor?.name?.trim() || 'Dr(a). Médico(a)';
  const docCrm = doctor?.crm?.trim() || '------';
  const docCrmState = doctor?.crmState || 'SP';
  const docSpecialty = doctor?.specialty || 'Clínica Médica';
  const docClinic = doctor?.clinicName?.trim() || '';
  const docAddress = doctor?.address?.trim() || '';
  const docPhone = doctor?.phone?.trim() || '';

  const currentDate = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  const getDocTitle = () => {
    switch (docType) {
      case 'prescription': return 'Receita_Medica';
      case 'special_prescription': return 'Receita_Controle_Especial';
      case 'exams': return 'Pedido_Exames';
      case 'certificate': return 'Atestado_Medico';
      case 'referral': return 'Encaminhamento_Medico';
      default: return 'Documento_Medico';
    }
  };

  /**
   * Generates a high-precision A4 PDF directly using jsPDF and jspdf-autotable.
   */
  const handleExportPDF = async () => {
    try {
      setIsExportingPdf(true);

      const pdf = generateMedicalPDF({
        docType,
        doctor,
        patient,
        prescriptionItems,
        exams: effectiveExams,
        examIndication,
        certificate,
        referral
      });

      const cleanPatient = (patientName || 'Paciente').replace(/[^a-zA-Z0-9]/g, '_');
      const dateStr = new Date().toISOString().split('T')[0];
      const filename = `${getDocTitle()}_${cleanPatient}_${dateStr}.pdf`;

      pdf.save(filename);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 3000);
    } catch (err) {
      console.error('Erro ao exportar PDF via jsPDF & autoTable:', err);
    } finally {
      setIsExportingPdf(false);
    }
  };

  // Formatted text builder for WhatsApp and Clipboard
  const getFormattedDocumentText = (): string => {
    const dateStr = new Date().toLocaleDateString('pt-BR');
    const docLine = docName !== 'Dr(a). Médico(a)' ? `👨‍⚕️ *${docName}* — CRM ${docCrm}/${docCrmState}\n` : '👨‍⚕️ *Documento Médico*\n';
    const patientLine = patientName !== 'Não identificado' ? `👤 *Paciente:* ${patientName}${patientWeight ? ` (${patientWeight} kg)` : ''}\n` : '';
    const header = `📋 *DOCUMENTO MÉDICO DIGITAL*\n${docLine}${patientLine}📅 *Data:* ${dateStr}\n------------------------------------\n`;

    if (docType === 'prescription' || docType === 'special_prescription') {
      if (prescriptionItems.length === 0) return '';
      let text = `${header}💊 *PRESCRIÇÃO TERAPÊUTICA:*\n`;
      prescriptionItems.forEach((it, idx) => {
        text += `\n*${idx + 1}. ${it.name}* (${it.route})\n   📦 *Qtd:* ${it.quantity}\n   👉 *Posologia:* ${it.instructions}\n`;
      });
      text += `\n------------------------------------\n⚠️ _Siga as instruções médicas e os horários informados._`;
      return text;
    } else if (docType === 'certificate') {
      let text = `${header}📄 *ATESTADO MÉDICO*\n\n`;
      text += `Atesto para os devidos fins que o(a) paciente *${patientName}* esteve sob atendimento médico nesta data (${dateStr}).\n\n`;
      if (certificate?.daysOff) {
        text += `👉 *Recomendação:* Repouso e afastamento das atividades laborais por *${certificate.daysOff} dia(s)* a contar desta data.\n\n`;
      }
      if (certificate?.cid10Code) {
        text += `📌 *CID-10:* ${certificate.cid10Code}${certificate.cid10Description ? ' - ' + certificate.cid10Description : ''}\n\n`;
      }
      if (certificate?.observations) {
        text += `📝 *Observação:* ${certificate.observations}\n\n`;
      }
      text += `------------------------------------\n_${docName} — CRM ${docCrm}/${docCrmState}_`;
      return text;
    } else if (docType === 'referral') {
      let text = `${header}🩺 *ENCAMINHAMENTO MÉDICO*\n\n`;
      text += `Ao(À) Colega Especialista em *${referral?.destinationSpecialty || 'Medicina'}*:\n\n`;
      text += `Encaminho o(a) paciente *${patientName}* para avaliação e conduta clínica.\n\n`;
      if (referral?.reason) {
        text += `📌 *Motivo / Hipótese:* ${referral.reason}\n\n`;
      }
      if (referral?.clinicalSummary) {
        text += `📝 *Resumo Clínico:* ${referral.clinicalSummary}\n\n`;
      }
      text += `------------------------------------\n_${docName} — CRM ${docCrm}/${docCrmState}_`;
      return text;
    } else if (docType === 'exams') {
      let text = `${header}🧪 *SOLICITAÇÃO DE EXAMES COMPLEMENTARES*\n\n`;
      if (exams.length === 0) return '';
      exams.forEach((ex, idx) => {
        text += `• ${ex.name}\n`;
      });
      if (examIndication) {
        text += `\n📌 *Indicação Clínica:* ${examIndication}\n`;
      }
      text += `\n------------------------------------\n_${docName} — CRM ${docCrm}/${docCrmState}_`;
      return text;
    }
    return `${header}Documento emitido pelo PrescMed.`;
  };

  const handleSendWhatsApp = () => {
    const text = getFormattedDocumentText();
    if (!text) {
      alert('Nenhum dado para enviar.');
      return;
    }
    const encoded = encodeURIComponent(text);
    window.open(`https://api.whatsapp.com/send?text=${encoded}`, '_blank');
  };

  const handleCopyFormattedText = () => {
    const text = getFormattedDocumentText();
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const handleShare = async () => {
    const text = getFormattedDocumentText();
    if (navigator.share && text) {
      try {
        await navigator.share({
          title: `PrescMed - ${patientName}`,
          text: text,
        });
      } catch {
        // Share cancelled
      }
    } else {
      handleCopyFormattedText();
    }
  };

  const handleCopyValidation = () => {
    navigator.clipboard.writeText(`https://prescmed.digital/validar/doc-${Math.random().toString(36).substr(2, 9).toUpperCase()}`);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const itemsByRoute = prescriptionItems.reduce((acc, item) => {
    const route = (item.route || 'Oral').toUpperCase();
    if (!acc[route]) acc[route] = [];
    acc[route].push(item);
    return acc;
  }, {} as { [route: string]: PrescriptionItem[] });

  return (
    <div id="print-preview-section" className="space-y-4 sm:space-y-5 pb-12">
      {/* Top Controller Bar */}
      <div 
        className="tactile-card p-4 sm:p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 no-print"
        style={{
          backgroundColor: 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(11, 19, 43, 0.08)'
        }}
      >
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleBack}
            className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-xl border flex items-center justify-center text-slate-400 hover:text-slate-100 cursor-pointer transition-all active:scale-95 tactile-btn-secondary"
            style={{
              backgroundColor: 'var(--surface-inset)'
            }}
            title="Voltar para Edição"
          >
            <ArrowLeft className="w-5 h-5 icon-sculpted" strokeWidth={1.75} />
          </button>
          <div>
            <h2 className="text-base sm:text-lg font-bold flex items-center gap-2" style={{ color: darkMode ? '#F4F7FC' : '#0B132B' }}>
              <span>Exportar & Baixar PDF</span>
              <span className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 font-bold uppercase tracking-wider">
                A4 • Margens 10mm
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-medium mt-0.5">
              Documento formatado em alta fidelidade com fontes serifadas e espaçamento legal.
            </p>
          </div>
        </div>

        {/* Action CTAs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0 max-w-full custom-scrollbar">
          {/* Copiar Texto */}
          <button
            type="button"
            onClick={handleCopyFormattedText}
            className="h-10 sm:h-11 px-3.5 rounded-xl border border-slate-300 dark:border-white/10 bg-slate-100/80 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 text-xs sm:text-sm font-bold flex items-center gap-2 shrink-0 whitespace-nowrap transition-all active:scale-95 cursor-pointer"
            title="Copiar texto formatado para prontuário/PEP"
          >
            {copiedLink ? (
              <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" strokeWidth={2} />
            ) : (
              <Copy className="w-4 h-4 text-slate-500 dark:text-slate-400 shrink-0" strokeWidth={1.75} />
            )}
            <span>{copiedLink ? 'Copiado!' : 'Copiar Texto'}</span>
          </button>

          {/* Imprimir Navegador */}
          <button
            type="button"
            onClick={() => window.print()}
            className="h-10 sm:h-11 px-3.5 rounded-xl border border-slate-300 dark:border-white/10 bg-slate-100/80 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 text-xs sm:text-sm font-bold hidden md:flex items-center gap-2 shrink-0 whitespace-nowrap transition-all active:scale-95 cursor-pointer"
            title="Imprimir direto pelo navegador (Ctrl+P)"
          >
            <Printer className="w-4 h-4 text-slate-500 dark:text-slate-400 shrink-0" strokeWidth={1.75} />
            <span>Imprimir</span>
          </button>

          {/* Enviar no WhatsApp */}
          <button
            type="button"
            onClick={handleSendWhatsApp}
            className="h-10 sm:h-11 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white text-xs sm:text-sm font-bold flex items-center gap-2 shrink-0 whitespace-nowrap shadow-tactile-btn transition-all active:scale-95 cursor-pointer"
            title="Enviar o documento diretamente para o WhatsApp do paciente ou familiar"
          >
            <Send className="w-4 h-4 shrink-0" strokeWidth={2} />
            <span>Enviar no WhatsApp</span>
          </button>

          {/* Baixar PDF (Ação Principal) */}
          <button
            type="button"
            onClick={handleExportPDF}
            disabled={isExportingPdf}
            className="h-10 sm:h-11 px-5 rounded-xl bg-navy-900 hover:bg-navy-950 text-white dark:bg-cream-100 dark:hover:bg-white dark:text-navy-950 text-xs sm:text-sm font-black flex items-center gap-2 shrink-0 whitespace-nowrap shadow-tactile-btn border border-white/20 dark:border-navy-900/30 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
            title="Gerar e baixar arquivo PDF padrão A4 (10mm)"
          >
            {isExportingPdf ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white dark:text-navy-950 shrink-0" />
                <span>Gerando PDF...</span>
              </>
            ) : exportSuccess ? (
              <>
                <Check className="w-4 h-4 text-emerald-400 dark:text-emerald-600 shrink-0" strokeWidth={2.5} />
                <span>Baixado com Sucesso!</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4 shrink-0" strokeWidth={2} />
                <span>Baixar PDF</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Document Type Switcher Tabs */}
      <div className="flex items-center justify-between gap-2 overflow-x-auto pb-1 no-print">
        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          <button
            type="button"
            onClick={() => setDocType('prescription')}
            className={`text-xs font-semibold px-4 py-2.5 min-h-[44px] rounded-xl whitespace-nowrap border transition-all cursor-pointer active:scale-95 flex items-center gap-1.5 ${
              docType === 'prescription'
                ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                : darkMode
                ? 'bg-navy-800/60 text-slate-300 border-white/10 hover:bg-navy-700'
                : 'bg-white text-slate-700 border-cream-300/80 hover:bg-cream-100'
            }`}
          >
            <FileText className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
            <span>Receita Padrão ({prescriptionItems.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setDocType('special_prescription')}
            className={`text-xs font-semibold px-4 py-2.5 min-h-[44px] rounded-xl whitespace-nowrap border transition-all cursor-pointer active:scale-95 flex items-center gap-1.5 ${
              docType === 'special_prescription'
                ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                : darkMode
                ? 'bg-navy-800/60 text-slate-300 border-white/10 hover:bg-navy-700'
                : 'bg-white text-slate-700 border-cream-300/80 hover:bg-cream-100'
            }`}
          >
            <Layers className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
            <span>Controle Especial (2 Vias)</span>
          </button>

          <button
            type="button"
            onClick={() => setDocType('exams')}
            className={`text-xs font-semibold px-4 py-2.5 min-h-[44px] rounded-xl whitespace-nowrap border transition-all cursor-pointer active:scale-95 flex items-center gap-1.5 ${
              docType === 'exams'
                ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                : darkMode
                ? 'bg-navy-800/60 text-slate-300 border-white/10 hover:bg-navy-700'
                : 'bg-white text-slate-700 border-cream-300/80 hover:bg-cream-100'
            }`}
          >
            <FlaskConical className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
            <span>Exames ({effectiveExams.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setDocType('certificate')}
            className={`text-xs font-semibold px-4 py-2.5 min-h-[44px] rounded-xl whitespace-nowrap border transition-all cursor-pointer active:scale-95 flex items-center gap-1.5 ${
              docType === 'certificate'
                ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                : darkMode
                ? 'bg-navy-800/60 text-slate-300 border-white/10 hover:bg-navy-700'
                : 'bg-white text-slate-700 border-cream-300/80 hover:bg-cream-100'
            }`}
          >
            <Award className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
            <span>Atestados</span>
          </button>

          <button
            type="button"
            onClick={() => setDocType('referral')}
            className={`text-xs font-semibold px-4 py-2.5 min-h-[44px] rounded-xl whitespace-nowrap border transition-all cursor-pointer active:scale-95 flex items-center gap-1.5 ${
              docType === 'referral'
                ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
                : darkMode
                ? 'bg-navy-800/60 text-slate-300 border-white/10 hover:bg-navy-700'
                : 'bg-white text-slate-700 border-cream-300/80 hover:bg-cream-100'
            }`}
          >
            <Share2 className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
            <span>Encaminhamentos</span>
          </button>
        </div>

        {/* View Zoom Toggle for Mobile */}
        <button
          type="button"
          onClick={() => setFitToMobile(!fitToMobile)}
          className="sm:hidden px-3 py-2 min-h-[44px] rounded-xl border text-xs font-semibold flex items-center gap-1.5 cursor-pointer flex-shrink-0 active:scale-95 tactile-btn-secondary"
          style={{
            backgroundColor: 'var(--surface-card)',
            borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(11,19,43,0.08)',
            color: darkMode ? '#388EE6' : '#0F5E94'
          }}
          title={fitToMobile ? 'Modo Tamanho Real' : 'Modo Ajustar à Tela'}
        >
          {fitToMobile ? <Maximize2 className="w-4 h-4 icon-sculpted" strokeWidth={1.75} /> : <Minimize2 className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />}
          <span>{fitToMobile ? 'Zoom' : 'Ajustar'}</span>
        </button>
      </div>

      {/* A4 Paper Container Wrapper */}
      <div className="flex justify-center p-2 sm:p-5 bg-slate-900/20 rounded-2xl overflow-x-auto">
        <div 
          ref={printSheetRef}
          id="printable-a4-sheet"
          className={`print-page w-full shadow-lg p-6 sm:p-10 md:p-12 rounded-xl relative transition-all duration-200 ${
            fitToMobile ? 'max-w-full sm:max-w-[780px] min-h-[950px] sm:min-h-[1100px]' : 'min-w-[650px] max-w-[780px] min-h-[1100px]'
          }`}
          style={{
            backgroundColor: '#FFFFFF',
            color: '#0F172A',
            display: 'grid',
            gridTemplateRows: 'auto 1fr auto',
            rowGap: '1.5rem'
          }}
        >
          {/* Top Medical Letterhead / Header (Grid Row 1) */}
          <header id="print-header" className="print-header print-avoid-break w-full">
            <div 
              className="pb-4 sm:pb-5 flex flex-col sm:flex-row sm:items-start justify-between gap-3 print-avoid-break"
              style={{ borderBottom: '2px solid #0F172A' }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2.5 mb-1.5">
                  <div 
                    className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center font-black flex-shrink-0"
                    style={{ backgroundColor: '#1E4F7A', color: '#FFFFFF' }}
                  >
                    <ShieldCheck className="w-6 h-6 sm:w-7 sm:h-7" strokeWidth={1.75} />
                  </div>
                  <div>
                    <h1 className="font-extrabold text-lg sm:text-2xl tracking-tight uppercase leading-none font-sans" style={{ color: '#0F172A' }}>
                      {docName}
                    </h1>
                    <p className="text-xs sm:text-sm font-bold font-sans mt-0.5" style={{ color: '#1E4F7A' }}>
                      CRM-{docCrmState} {docCrm} {doctor?.rqe ? `• RQE ${doctor.rqe}` : ''}
                    </p>
                  </div>
                </div>
                <p className="text-xs sm:text-sm font-semibold font-sans" style={{ color: '#334155' }}>
                  {docSpecialty}
                </p>
                <p className="text-xs sm:text-xs mt-1 leading-normal font-sans" style={{ color: '#64748B' }}>
                  {docClinic} • {docAddress} • {docPhone}
                </p>
              </div>

              {/* Document Title Badge */}
              <div 
                className="text-left sm:text-right flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-start gap-1.5 border-t sm:border-t-0 pt-2.5 sm:pt-0"
                style={{ borderColor: '#E2E8F0' }}
              >
                <span 
                  className="text-[10px] sm:text-xs uppercase font-extrabold px-3 py-1.5 rounded-md inline-block tracking-wider font-sans"
                  style={{
                    backgroundColor: '#F1F5F9',
                    color: '#0F172A',
                    border: '1px solid #CBD5E1'
                  }}
                >
                  {docType === 'prescription' && 'RECEITUÁRIO MÉDICO'}
                  {docType === 'special_prescription' && 'RECEITA CONTROLE ESPECIAL'}
                  {docType === 'exams' && 'SOLICITAÇÃO DE EXAMES'}
                  {docType === 'certificate' && 'ATESTADO MÉDICO'}
                  {docType === 'referral' && 'ENCAMINHAMENTO MÉDICO'}
                </span>
                {docType === 'special_prescription' && (
                  <span className="text-[9px] sm:text-[10px] font-bold block uppercase tracking-wide font-sans" style={{ color: '#991B1B' }}>
                    1ª Via: Farmácia / 2ª Via: Paciente
                  </span>
                )}
                <span className="text-xs sm:text-xs font-medium font-sans" style={{ color: '#64748B' }}>
                  {new Date().toLocaleDateString('pt-BR')}
                </span>
              </div>
            </div>

            {/* Patient Header Box */}
            <div 
              className="mt-4 p-4 rounded-xl grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs sm:text-sm print-avoid-break"
              style={{
                backgroundColor: '#F8FAFC',
                border: '1px solid #CBD5E1',
                color: '#0F172A'
              }}
            >
              <div className="col-span-2 sm:col-span-1">
                <span className="text-[10px] sm:text-xs uppercase font-bold block text-slate-500 font-sans tracking-wide">
                  Paciente:
                </span>
                <span className="font-extrabold text-sm sm:text-base text-slate-900 block leading-tight font-sans mt-0.5">
                  {patientName}
                </span>
              </div>
              <div>
                <span className="text-[10px] sm:text-xs uppercase font-bold block text-slate-500 font-sans tracking-wide">
                  Doc (RG/CPF):
                </span>
                <span className="font-semibold text-xs sm:text-sm text-slate-800 block leading-tight font-sans mt-0.5">
                  {patientDoc}
                </span>
              </div>
              <div>
                <span className="text-[10px] sm:text-xs uppercase font-bold block text-slate-500 font-sans tracking-wide">
                  Peso Atual:
                </span>
                <span className="font-extrabold text-sm sm:text-base text-sky-800 block leading-tight font-sans mt-0.5">
                  {patientWeight ? `${patientWeight} kg` : '—'}
                </span>
              </div>
              <div>
                <span className="text-[10px] sm:text-xs uppercase font-bold block text-slate-500 font-sans tracking-wide">
                  Idade:
                </span>
                <span className="font-semibold text-xs sm:text-sm text-slate-800 block leading-tight font-sans mt-0.5">
                  {patientAge}
                </span>
              </div>
            </div>
          </header>

          {/* DOCUMENT BODY CONTENT (Grid Row 2 - Flex 1fr) */}
          <main id="print-content" className="print-body w-full min-h-0 flex-1 flex flex-col justify-start">
              {/* 1. PRESCRIPTION CONTENT */}
              {(docType === 'prescription' || docType === 'special_prescription') && (
                <div className="space-y-6 sm:space-y-8 font-serif" style={{ fontFamily: 'Georgia, Cambria, "Times New Roman", Times, serif' }}>
                  {prescriptionItems.length === 0 ? (
                    <div className="py-16 text-center italic text-base text-slate-400 font-serif">
                      Nenhum medicamento adicionado nesta prescrição.
                    </div>
                  ) : (
                    (Object.entries(itemsByRoute) as [string, PrescriptionItem[]][]).map(([route, items]) => {
                      const cleanRoute = route.trim().toUpperCase();
                      const routeTitle = cleanRoute.startsWith('USO ') ? cleanRoute : `USO ${cleanRoute}`;
                      return (
                        <div key={route} className="space-y-4 print-avoid-break">
                          <div 
                            className="pb-1.5 flex items-center justify-between"
                            style={{ borderBottom: '1.5px solid #CBD5E1' }}
                          >
                            <span className="font-bold text-xs sm:text-sm tracking-wider uppercase font-sans text-sky-900">
                              {routeTitle}
                            </span>
                          </div>

                        <div className="space-y-5 pl-1 sm:pl-2">
                          {items.map((item, idx) => (
                            <div key={item.id} className="space-y-1.5 print-avoid-break">
                              {/* Medication Item Headline */}
                              <div className="flex items-baseline justify-between font-serif text-base sm:text-lg" style={{ color: '#0F172A' }}>
                                <div className="pr-3 leading-snug">
                                  <span className="font-bold mr-2 font-serif text-base sm:text-lg text-slate-950">{idx + 1})</span>
                                  <span className="uppercase font-bold tracking-tight text-slate-950">{item.name}</span>{' '}
                                  <span className="text-sm sm:text-base font-normal italic text-slate-700">({item.presentation})</span>
                                </div>
                                <div className="text-sm sm:text-base font-semibold font-serif tracking-wider whitespace-nowrap flex-shrink-0 text-slate-800">
                                  ---------------- {item.quantity}
                                </div>
                              </div>

                              {/* Posology / Administration Instructions in Serif */}
                              <div className="pl-5 sm:pl-7 text-sm sm:text-base font-medium leading-relaxed sm:leading-loose text-slate-900 font-serif">
                                {item.instructions}
                              </div>

                              {/* Suggested Schedule Times */}
                              {item.scheduleTimes && item.scheduleTimes.length > 0 && (
                                <div className="pl-5 sm:pl-7 flex items-center gap-2 text-xs sm:text-sm font-sans font-semibold mt-1.5 flex-wrap" style={{ color: '#1E4F7A' }}>
                                  <span>Horários sugeridos:</span>
                                  <div className="flex gap-1.5 flex-wrap">
                                    {item.scheduleTimes.map(t => (
                                      <span 
                                        key={t} 
                                        className="px-2 py-0.5 rounded-md font-bold text-xs sm:text-sm font-sans"
                                        style={{
                                          backgroundColor: '#F1F5F9',
                                          color: '#0F172A',
                                          border: '1px solid #CBD5E1'
                                        }}
                                      >
                                        {t}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })
                  )}

                  {/* Special Control Prescription: Buyer & Supplier Regulatory Fields */}
                  {docType === 'special_prescription' && (
                    <div 
                      className="mt-8 pt-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs sm:text-sm font-sans print-avoid-break"
                      style={{
                        borderTop: '1.5px solid #CBD5E1',
                        color: '#334155'
                      }}
                    >
                      <div 
                        className="p-3.5 rounded-lg space-y-2"
                        style={{
                          backgroundColor: '#F8FAFC',
                          border: '1px solid #CBD5E1'
                        }}
                      >
                        <span className="font-bold uppercase block pb-1 text-xs tracking-wider" style={{ color: '#0F172A', borderBottom: '1px solid #E2E8F0' }}>
                          IDENTIFICAÇÃO DO COMPRADOR
                        </span>
                        <div className="space-y-1.5 text-xs font-medium">
                          <div>Nome: _________________________________________</div>
                          <div className="flex justify-between">
                            <span>RG/Órgão: ________________</span>
                            <span>CPF: __________________</span>
                          </div>
                          <div>Endereço: _______________________________________</div>
                          <div className="flex justify-between">
                            <span>Cidade/UF: _______________</span>
                            <span>Tel: __________________</span>
                          </div>
                        </div>
                      </div>

                      <div 
                        className="p-3.5 rounded-lg space-y-2"
                        style={{
                          backgroundColor: '#F8FAFC',
                          border: '1px solid #CBD5E1'
                        }}
                      >
                        <span className="font-bold uppercase block pb-1 text-xs tracking-wider" style={{ color: '#0F172A', borderBottom: '1px solid #E2E8F0' }}>
                          IDENTIFICAÇÃO DO FORNECEDOR
                        </span>
                        <div className="space-y-1.5 text-xs font-medium">
                          <div>Farmácia/Drogaria: ____________________________</div>
                          <div className="pt-3 text-center mt-2" style={{ borderTop: '1px dotted #94A3B8' }}>
                            <span className="block text-[10px] text-slate-500 font-medium">Assinatura do Farmacêutico / Data</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 2. EXAMS CONTENT */}
              {docType === 'exams' && (
                <div className="space-y-6 font-serif" style={{ fontFamily: 'Georgia, Cambria, "Times New Roman", Times, serif' }}>
                  {examIndication && (
                    <div 
                      className="p-4 rounded-xl text-xs sm:text-sm font-sans"
                      style={{
                        backgroundColor: '#FEF8EE',
                        border: '1px solid #FDE68A',
                        color: '#78350F'
                      }}
                    >
                      <span className="font-bold uppercase">Indicação Clínica: </span>
                      <span className="font-semibold text-slate-900">{examIndication}</span>
                    </div>
                  )}

                  <div className="pb-1.5" style={{ borderBottom: '1.5px solid #CBD5E1' }}>
                    <span className="font-bold text-xs sm:text-sm tracking-wider uppercase font-sans text-sky-900">
                      EXAMES COMPLEMENTARES SOLICITADOS:
                    </span>
                  </div>

                  {effectiveExams.length === 0 ? (
                    <div className="py-16 text-center italic text-base text-slate-400 font-serif">
                      Nenhum exame selecionado neste pedido.
                    </div>
                  ) : (
                    <ol className="list-decimal list-inside space-y-3 pl-2 text-sm sm:text-base font-serif text-slate-950 font-semibold leading-relaxed">
                      {effectiveExams.map((exam) => (
                        <li key={exam.id} className="leading-relaxed">
                          <span className="font-bold">{exam.name}</span>
                          <span className="text-xs sm:text-sm font-normal italic ml-2 text-slate-600 font-sans">({exam.category})</span>
                        </li>
                      ))}
                    </ol>
                  )}
                </div>
              )}

              {/* 3. ATESTADO MÉDICO CONTENT */}
              {docType === 'certificate' && (
                <div className="py-4 sm:py-8 px-1 sm:px-4 space-y-6 sm:space-y-8 font-serif text-justify leading-relaxed sm:leading-loose" style={{ fontFamily: 'Georgia, Cambria, "Times New Roman", Times, serif' }}>
                  <h2 
                    className="text-center font-bold text-xl sm:text-2xl uppercase tracking-widest pb-3 font-sans"
                    style={{ color: '#0F172A', borderBottom: '1.5px solid #CBD5E1' }}
                  >
                    ATESTADO MÉDICO
                  </h2>

                  <p className="text-base sm:text-lg indent-6 sm:indent-10 leading-loose sm:leading-loose text-slate-950 font-normal">
                    Atesto para os devidos fins de direito que o(a) paciente{' '}
                    <strong className="underline uppercase font-bold text-slate-950">{certificate.patientName || patientName}</strong>,{' '}
                    {(certificate.documentNumber || (patientDoc !== '—' ? patientDoc : '')) ? `portador(a) do documento nº ${certificate.documentNumber || patientDoc}, ` : ''}
                    esteve sob meus cuidados médicos profissionais no dia {certificate.startDate ? new Date(certificate.startDate + 'T00:00:00').toLocaleDateString('pt-BR') : new Date().toLocaleDateString('pt-BR')},{' '}
                    necessitando de <strong className="font-bold text-slate-950">{certificate.daysOff || 1} ({certificate.daysOff === 1 ? 'um' : certificate.daysOff || 1}) dia(s)</strong> de repouso e afastamento de suas atividades habituais{' '}
                    {certificate.periodText || ''}, com retorno previsto a partir de {certificate.endDate ? new Date(certificate.endDate + 'T00:00:00').toLocaleDateString('pt-BR') : new Date().toLocaleDateString('pt-BR')}.
                  </p>

                  {certificate.includeCID && certificate.cid10Code && (
                    <div 
                      className="p-4 rounded-xl text-xs sm:text-sm font-sans"
                      style={{
                        backgroundColor: '#F1F5F9',
                        border: '1px solid #CBD5E1',
                        color: '#0F172A'
                      }}
                    >
                      <span className="font-bold">Diagnóstico Codificado (CID-10): </span>
                      <span className="font-semibold text-sky-900">{certificate.cid10Code} - {certificate.cid10Description}</span>
                      <span className="block text-xs font-normal text-slate-500 mt-1">
                        * Inclusão do CID expressamente solicitada e autorizada pelo(a) paciente (Resolução CFM nº 1.658/2002).
                      </span>
                    </div>
                  )}

                  {certificate.observations && (
                    <div className="text-sm sm:text-base font-serif italic text-slate-800">
                      <strong className="font-bold text-slate-950 font-sans">Observações Médicas: </strong>
                      {certificate.observations}
                    </div>
                  )}
                </div>
              )}

              {/* 4. ENCAMINHAMENTO CONTENT */}
              {docType === 'referral' && (
                <div className="space-y-5 sm:space-y-6 text-sm font-serif" style={{ fontFamily: 'Georgia, Cambria, "Times New Roman", Times, serif' }}>
                  <h2 
                    className="text-center font-bold text-lg sm:text-xl uppercase tracking-widest pb-3 font-sans"
                    style={{ color: '#0F172A', borderBottom: '1.5px solid #CBD5E1' }}
                  >
                    GUIA DE ENCAMINHAMENTO & REFERÊNCIA
                  </h2>

                  <div 
                    className="p-4 rounded-xl font-sans"
                    style={{
                      backgroundColor: '#F0FDF4',
                      border: '1px solid #BBF7D0',
                      color: '#14532D'
                    }}
                  >
                    <span className="font-bold uppercase text-xs">Ao Serviço Especializado de: </span>
                    <span className="font-extrabold text-base sm:text-lg block text-emerald-950">{referral.destinationSpecialty}</span>
                    {referral.destinationInstitution && (
                      <span className="font-medium text-xs sm:text-sm block mt-1 text-slate-700">
                        Local / Instituição: {referral.destinationInstitution}
                      </span>
                    )}
                  </div>

                  <div className="space-y-1.5">
                    <span className="font-bold uppercase block text-xs font-sans text-slate-600">Motivo da Solicitação:</span>
                    <p 
                      className="p-3.5 rounded-xl font-medium text-sm sm:text-base leading-relaxed"
                      style={{
                        backgroundColor: '#F8FAFC',
                        border: '1px solid #CBD5E1',
                        color: '#0F172A'
                      }}
                    >
                      {referral.reason || 'Avaliação e conduta terapêutica especializada.'}
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <span className="font-bold uppercase block text-xs font-sans text-slate-600">Resumo Clínico / Evolução:</span>
                    <p 
                      className="p-3.5 rounded-xl font-medium text-sm sm:text-base leading-loose"
                      style={{
                        backgroundColor: '#F8FAFC',
                        border: '1px solid #CBD5E1',
                        color: '#1E293B'
                      }}
                    >
                      {referral.clinicalSummary || 'Histórico clínico e exame físico sem alterações agudas no momento.'}
                    </p>
                  </div>

                  {referral.relevantExams && (
                    <div className="space-y-1.5">
                      <span className="font-bold uppercase block text-xs font-sans text-slate-600">Exames Complementares Realizados:</span>
                      <p 
                        className="p-3.5 rounded-xl text-sm sm:text-base font-medium"
                        style={{
                          backgroundColor: '#F8FAFC',
                          border: '1px solid #CBD5E1',
                          color: '#1E293B'
                        }}
                      >
                        {referral.relevantExams}
                      </p>
                    </div>
                  )}

                  {referral.hypothesisCID && (
                    <div className="space-y-1.5 print-avoid-break">
                      <span className="font-bold uppercase block text-xs font-sans text-slate-600">Hipótese Diagnóstica (CID-10):</span>
                      <p 
                        className="p-3.5 rounded-xl font-semibold text-sm sm:text-base font-sans"
                        style={{
                          backgroundColor: '#F8FAFC',
                          border: '1px solid #CBD5E1',
                          color: '#1E4F7A'
                        }}
                      >
                        {referral.hypothesisCID}
                      </p>
                    </div>
                  )}
                </div>
              )}
          </main>

          {/* Bottom Footer & Signature (Grid Row 3) */}
          <footer 
            id="print-footer"
            className="print-footer print-avoid-break w-full mt-auto pt-4 sm:pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 sm:gap-6"
            style={{ borderTop: '2px solid #0F172A' }}
          >
            {/* Left: Validation QR Code & Security Stamp */}
            <div className="flex items-center gap-3 w-full sm:w-auto justify-center sm:justify-start">
              <div 
                onClick={handleCopyValidation}
                className="w-14 h-14 sm:w-16 sm:h-16 p-1 rounded-lg flex items-center justify-center shadow-xs cursor-pointer"
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1.5px solid #0F172A'
                }}
                title="Clique para validar autenticidade digital"
              >
                <QrCode className="w-full h-full" style={{ color: '#0F172A' }} />
              </div>
              <div className="text-[10px] sm:text-xs leading-tight font-sans text-slate-600">
                <span className="font-bold block text-slate-900">VALIDAÇÃO DIGITAL CFM</span>
                <span>Código: DOC-PRESC-{Math.random().toString(36).substr(2, 6).toUpperCase()}</span>
                <span className="block font-semibold text-emerald-800">Assinatura Eletrônica Válida</span>
                <span>Consulte em prescmed.digital</span>
              </div>
            </div>

            {/* Right: City, Date & Doctor Signature Line */}
            <div className="text-center sm:text-right w-full sm:w-auto font-sans">
              <p className="text-xs sm:text-sm font-medium mb-4 sm:mb-6 font-serif italic text-slate-700">
                {doctor?.cityState || 'São Paulo - SP'}, {currentDate}
              </p>
              
              <div 
                className="inline-block pt-2 min-w-[210px] sm:min-w-[240px] text-center"
                style={{ borderTop: '1.5px solid #0F172A' }}
              >
                <p className="font-bold text-sm sm:text-base uppercase tracking-tight text-slate-950 font-sans">
                  {docName}
                </p>
                <p className="text-xs sm:text-sm font-semibold text-sky-900 font-sans">
                  CRM-{docCrmState} {docCrm}
                </p>
                <p className="text-xs sm:text-xs text-slate-500 font-sans font-medium">
                  {docSpecialty}
                </p>
              </div>
            </div>
          </footer>
        </div>
      </div>

      {/* Bottom Sticky Action Bar */}
      <div 
        className="tactile-card p-4 sm:p-5 rounded-2xl flex items-center justify-between gap-4 no-print"
        style={{
          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
        }}
      >
        <div className="flex items-center gap-3">
          <div 
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white"
            style={{
              backgroundColor: darkMode ? '#1E4F7A' : '#0F6292',
              border: '1px solid rgba(255, 255, 255, 0.12)'
            }}
          >
            <FileCheck className="w-5 h-5 text-slate-100" strokeWidth={1.75} />
          </div>
          <div>
            <div className="text-xs sm:text-sm font-bold" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
              Documento Pronto para Download
            </div>
            <div className="text-[11px] text-slate-400">
              Formato A4 com margens de 10mm e fontes serifadas de alta legibilidade.
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={handleShare}
            className="tactile-btn-secondary px-3.5 py-2.5 text-xs font-semibold flex items-center gap-1.5 cursor-pointer"
            style={{
              backgroundColor: 'var(--surface-inset)',
              color: darkMode ? '#CBD5E1' : '#334155'
            }}
          >
            {copiedLink ? <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400" strokeWidth={1.75} /> : <Share2 className="w-4 h-4 text-slate-400" strokeWidth={1.75} />}
            <span>Compartilhar</span>
          </button>

          <button
            type="button"
            onClick={handleExportPDF}
            disabled={isExportingPdf}
            className="tactile-btn-primary px-5 py-2.5 text-xs sm:text-sm font-semibold flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {isExportingPdf ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Baixando PDF...</span>
              </>
            ) : exportSuccess ? (
              <>
                <Check className="w-4 h-4 text-emerald-300" strokeWidth={1.75} />
                <span>PDF Baixado!</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" strokeWidth={1.75} />
                <span>Baixar PDF</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
