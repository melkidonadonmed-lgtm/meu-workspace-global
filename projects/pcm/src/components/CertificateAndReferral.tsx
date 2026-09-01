import React, { useState } from 'react';
import { 
  Award, 
  Share2, 
  Download,
  CheckCircle2,
  AlertCircle,
  FileText,
  Building2,
  Stethoscope,
  Sparkles,
  RefreshCw,
  Plus,
  Trash2,
  Calendar,
  Clock,
  User,
  Hash,
  Send
} from 'lucide-react';
import { MedicalCertificate, MedicalReferral, Patient, DoctorProfile } from '../types';
import { CidSearchBar } from './CidSearchBar';
import { COMMON_CID10, CIDItem } from '../data/cidCatalog';

interface CertificateAndReferralProps {
  darkMode: boolean;
  patient: Patient;
  onUpdatePatient?: (patient: Patient) => void;
  doctor: DoctorProfile;
  certificate: MedicalCertificate;
  onUpdateCertificate: (cert: MedicalCertificate) => void;
  referral: MedicalReferral;
  onUpdateReferral: (ref: MedicalReferral) => void;
  activeSubTab?: 'certificate' | 'referral';
  initialSubTab?: 'certificate' | 'referral';
  onSelectSubTab?: (tab: 'certificate' | 'referral') => void;
  onNavigateToPrint: (docType?: 'certificate' | 'referral') => void;
}

export const CertificateAndReferral: React.FC<CertificateAndReferralProps> = ({
  darkMode,
  patient,
  onUpdatePatient,
  doctor,
  certificate,
  onUpdateCertificate,
  referral,
  onUpdateReferral,
  activeSubTab,
  initialSubTab,
  onSelectSubTab,
  onNavigateToPrint
}) => {
  const [internalSubTab, setInternalSubTab] = useState<'certificate' | 'referral'>(initialSubTab || activeSubTab || 'certificate');
  const currentSubTab = activeSubTab || internalSubTab;

  const handlePatientNameChange = (newName: string) => {
    onUpdateCertificate({ ...certificate, patientName: newName });
    onUpdateReferral({ ...referral, patientName: newName });
    if (onUpdatePatient) {
      onUpdatePatient({ ...patient, name: newName });
    }
  };

  const handlePatientDocChange = (newDoc: string) => {
    onUpdateCertificate({ ...certificate, documentNumber: newDoc });
    onUpdateReferral({ ...referral, documentNumber: newDoc });
    if (onUpdatePatient) {
      onUpdatePatient({ ...patient, documentNumber: newDoc });
    }
  };

  const handleSwitchTab = (tab: 'certificate' | 'referral') => {
    setInternalSubTab(tab);
    if (onSelectSubTab) onSelectSubTab(tab);
  };
  const specialtiesList = [
    'Cardiologia',
    'Pediatria Especializada / Alergologia',
    'Otorrinolaringologia',
    'Ortopedia & Traumatologia',
    'Neurologia / Neuropediatria',
    'Endocrinologia & Metabologia',
    'Dermatologia',
    'Gastroenterologia',
    'Pneumologia',
    'Psiquiatria / Psicologia',
    'Cirurgia Geral / Pediátrica',
    'Oftalmologia',
    'Nefrologia / Urologia'
  ];

  // Specialty quick CIDs mapping for fast 1-click inclusion in referral
  const specialtyCidSuggestions: Record<string, { code: string; label: string }[]> = {
    'Cardiologia': [
      { code: 'I10', label: 'Hipertensão Arterial (HAS)' },
      { code: 'I20.9', label: 'Angina Pectoris' },
      { code: 'I50.9', label: 'Insuficiência Cardíaca' },
      { code: 'R07.4', label: 'Dor Torácica a Esclarecer' }
    ],
    'Pediatria Especializada / Alergologia': [
      { code: 'J45.9', label: 'Asma / Broncoespasmo' },
      { code: 'J30.4', label: 'Rinite Alérgica' },
      { code: 'L20.9', label: 'Dermatite Atópica' },
      { code: 'B08.4', label: 'Mão-Pé-Boca' }
    ],
    'Otorrinolaringologia': [
      { code: 'J01.9', label: 'Sinusite Aguda / Crônica' },
      { code: 'H66.9', label: 'Otite Média' },
      { code: 'H93.1', label: 'Tinnitus (Zumbido)' },
      { code: 'J30.4', label: 'Rinite Vasomotora/Alérgica' }
    ],
    'Ortopedia & Traumatologia': [
      { code: 'M54.5', label: 'Lombalgia' },
      { code: 'M54.2', label: 'Cervicalgia' },
      { code: 'S93.4', label: 'Entorse de Tornozelo' },
      { code: 'M75.1', label: 'Manguito Rotador (Ombro)' },
      { code: 'M65.9', label: 'Tendinopatia / Sinovite' }
    ],
    'Neurologia / Neuropediatria': [
      { code: 'G43.9', label: 'Enxaqueca / Migrânea' },
      { code: 'G44.2', label: 'Cefaleia Tensional' },
      { code: 'G40.9', label: 'Epilepsia / Convulsão' },
      { code: 'H81.1', label: 'VPPB / Vertigem' }
    ],
    'Endocrinologia & Metabologia': [
      { code: 'E11.9', label: 'Diabetes Mellitus tipo 2' },
      { code: 'E03.9', label: 'Hipotireoidismo' },
      { code: 'E66.9', label: 'Obesidade' },
      { code: 'E78.0', label: 'Dislipidemia' }
    ],
    'Dermatologia': [
      { code: 'L20.9', label: 'Dermatite Atópica' },
      { code: 'L50.9', label: 'Urticária' },
      { code: 'L70.0', label: 'Acne Vulgar' },
      { code: 'L40.0', label: 'Psoríase' }
    ],
    'Gastroenterologia': [
      { code: 'K21.9', label: 'DRGE / Refluxo' },
      { code: 'K29.7', label: 'Gastrite' },
      { code: 'K58.9', label: 'Intestino Irritável' },
      { code: 'K80.2', label: 'Colelitíase (Pedra Vesícula)' }
    ],
    'Pneumologia': [
      { code: 'J45.9', label: 'Asma / Crise Asmática' },
      { code: 'J44.9', label: 'DPOC / Enfisema' },
      { code: 'J18.9', label: 'Pneumonia' },
      { code: 'J20.9', label: 'Bronquite Aguda' }
    ],
    'Psiquiatria / Psicologia': [
      { code: 'F41.1', label: 'Ansiedade Generalizada (TAG)' },
      { code: 'F32.9', label: 'Episódio Depressivo' },
      { code: 'F41.0', label: 'Transtorno do Pânico' },
      { code: 'Z73.0', label: 'Burnout / Esgotamento' }
    ],
    'Nefrologia / Urologia': [
      { code: 'N39.0', label: 'ITU Recorrente' },
      { code: 'N20.1', label: 'Cálculo Renal / Ureteral' },
      { code: 'N40', label: 'Hiperplasia Prostática (HPB)' },
      { code: 'N10', label: 'Pielonefrite' }
    ]
  };

  const handleSelectCidForCertificate = (cid: { code: string; description: string }) => {
    onUpdateCertificate({
      ...certificate,
      includeCID: true,
      cid10Code: cid.code,
      cid10Description: cid.description
    });
  };

  const handleClearCidCertificate = () => {
    onUpdateCertificate({
      ...certificate,
      cid10Code: '',
      cid10Description: ''
    });
  };

  const handleSelectCidForReferral = (cid: { code: string; description: string }) => {
    const formatted = `${cid.code} - ${cid.description}`;
    onUpdateReferral({
      ...referral,
      hypothesisCID: formatted
    });
  };

  const handleAppendCidForReferral = (cid: { code: string; description: string }) => {
    const formatted = `${cid.code} - ${cid.description}`;
    const current = referral.hypothesisCID ? referral.hypothesisCID.trim() : '';
    const updated = current ? `${current} / ${formatted}` : formatted;
    onUpdateReferral({
      ...referral,
      hypothesisCID: updated
    });
  };

  const handleDaysChange = (days: number) => {
    const validDays = Math.max(0, isNaN(days) ? 0 : days);
    const startBase = certificate.startDate ? certificate.startDate + 'T00:00:00' : undefined;
    const start = startBase ? new Date(startBase) : new Date();
    const end = new Date(start);
    end.setDate(start.getDate() + (validDays > 0 ? validDays - 1 : 0));
    
    onUpdateCertificate({
      ...certificate,
      daysOff: validDays,
      endDate: end.toISOString().split('T')[0]
    });
  };

  const handleSendCertificateWhatsApp = () => {
    const pName = certificate.patientName?.trim() || patient?.name?.trim() || 'Paciente';
    const dateStr = certificate.date || new Date().toLocaleDateString('pt-BR');
    const docLine = doctor?.name?.trim() ? `👨‍⚕️ *${doctor.name.trim()}* — CRM ${doctor.crm || '------'}/${doctor.crmState || 'SP'}\n` : '';
    
    let msg = `📋 *ATESTADO MÉDICO DIGITAL*\n${docLine}👤 *Paciente:* ${pName}\n📅 *Data:* ${dateStr}\n------------------------------------\n\n`;
    msg += `Atesto para os devidos fins que o(a) paciente acima identificado(a) esteve sob atendimento médico nesta data (${dateStr}).\n\n`;
    if (certificate.daysOff > 0) {
      msg += `👉 *Recomendação:* Repouso e afastamento de suas atividades por *${certificate.daysOff} dia(s)* a contar desta data.\n\n`;
    }
    if (certificate.includeCID && certificate.cid10Code) {
      msg += `📌 *CID-10:* ${certificate.cid10Code}${certificate.cid10Description ? ` - ${certificate.cid10Description}` : ''}\n\n`;
    }
    if (certificate.observations) {
      msg += `📝 *Observações:* ${certificate.observations}\n\n`;
    }
    msg += `------------------------------------\n_Documento emitido conforme Resolução CFM 1.658/2002._`;

    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`, '_blank');
  };

  const handleSendReferralWhatsApp = () => {
    const pName = referral.patientName?.trim() || patient?.name?.trim() || 'Paciente';
    const dateStr = referral.date || new Date().toLocaleDateString('pt-BR');
    const docLine = doctor?.name?.trim() ? `👨‍⚕️ *${doctor.name.trim()}* — CRM ${doctor.crm || '------'}/${doctor.crmState || 'SP'}\n` : '';

    let msg = `📋 *ENCAMINHAMENTO MÉDICO DIGITAL*\n${docLine}👤 *Paciente:* ${pName}\n📅 *Data:* ${dateStr}\n------------------------------------\n\n`;
    msg += `Ao(À) Colega da especialidade *${referral.destinationSpecialty || 'Especialista'}*:\n\n`;
    msg += `Encaminho o(a) paciente para avaliação e conduta clínica especializada.\n\n`;
    if (referral.reason) {
      msg += `📌 *Motivo / Hipótese Diagnóstica:* ${referral.reason}\n\n`;
    }
    if (referral.clinicalSummary) {
      msg += `📝 *Resumo Clínico & Condutas Prévias:* ${referral.clinicalSummary}\n\n`;
    }
    msg += `------------------------------------\n_PrescMed — Referência e Contrarreferência Ambulatorial_`;

    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`, '_blank');
  };

  const currentSpecialtySuggestions = specialtyCidSuggestions[referral.destinationSpecialty] || [];

  return (
    <div id="certificate-and-referral-section" className="space-y-4 sm:space-y-5">
      {/* Subtabs Switcher */}
      <div 
        className="tactile-card p-1.5 rounded-2xl flex items-center gap-1.5 max-w-sm mx-auto"
        style={{
          backgroundColor: darkMode ? 'var(--surface-card)' : 'var(--surface-card)',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(11, 19, 43, 0.08)'
        }}
      >
        <button
          type="button"
          onClick={() => handleSwitchTab('certificate')}
          className={`flex-1 py-2.5 min-h-[44px] rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer active:scale-95 ${
            currentSubTab === 'certificate'
              ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
              : darkMode
              ? 'text-slate-400 hover:text-white'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Award className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
          <span>Atestado Médico</span>
        </button>

        <button
          type="button"
          onClick={() => handleSwitchTab('referral')}
          className={`flex-1 py-2.5 min-h-[44px] rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer active:scale-95 ${
            currentSubTab === 'referral'
              ? 'bg-navy-900 text-white dark:bg-cream-100 dark:text-navy-950 border border-navy-800 dark:border-white/30 shadow-tactile-navy dark:shadow-tactile-cream'
              : darkMode
              ? 'text-slate-400 hover:text-white'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Share2 className="w-4 h-4 icon-sculpted" strokeWidth={1.75} />
          <span>Encaminhamento</span>
        </button>
      </div>

      {/* ATESTADO MÉDICO FORM */}
      {currentSubTab === 'certificate' && (
        <div className="space-y-4">
          <div 
            className="tactile-card p-4 sm:p-5 md:p-6 rounded-2xl space-y-5"
            style={{
              backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
              borderColor: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(15, 23, 42, 0.08)'
            }}
          >
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)' }}>
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-sm"
                  style={{
                    backgroundColor: darkMode ? '#1E4F7A' : '#0F6292',
                    border: '1px solid rgba(255, 255, 255, 0.12)'
                  }}
                >
                  <Award className="w-5 h-5 text-slate-100" strokeWidth={1.75} />
                </div>
                <div>
                  <h3 className="font-bold text-base sm:text-lg" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                    Emissão de Atestado Médico
                  </h3>
                  <p className="text-xs text-slate-400 font-medium">
                    Atestado de afastamento, repouso ou comparecimento em conformidade com o CFM.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <button
                  type="button"
                  onClick={handleSendCertificateWhatsApp}
                  className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 cursor-pointer active:scale-95 transition-all shadow-tactile-btn"
                  title="Enviar o atestado médico diretamente pelo WhatsApp"
                >
                  <Send className="w-4 h-4" strokeWidth={2} />
                  <span>Enviar no WhatsApp</span>
                </button>

                <button
                  type="button"
                  onClick={() => onNavigateToPrint('certificate')}
                  className="tactile-btn-success px-4 py-2.5 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2 cursor-pointer active:scale-95 transition-transform"
                >
                  <Download className="w-4 h-4" strokeWidth={1.75} />
                  <span>Visualizar & Baixar PDF</span>
                </button>
              </div>
            </div>

            {/* Patient data for Certificate */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <User className="w-3.5 h-3.5 text-slate-400" />
                  <span>Nome do Paciente</span>
                </label>
                <input
                  type="text"
                  value={patient?.name ?? certificate.patientName ?? ''}
                  onChange={(e) => handlePatientNameChange(e.target.value)}
                  placeholder="Nome completo do paciente..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-semibold focus:outline-none tactile-input"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <Hash className="w-3.5 h-3.5 text-slate-400" />
                  <span>Documento (RG / CPF)</span>
                </label>
                <input
                  type="text"
                  value={patient?.documentNumber ?? certificate.documentNumber ?? ''}
                  onChange={(e) => handlePatientDocChange(e.target.value)}
                  placeholder="Ex: RG 12.345.678-9 ou CPF..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-medium focus:outline-none tactile-input"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5 text-slate-400" />
                  <span>Finalidade / Motivo</span>
                </label>
                <select
                  value={certificate.periodText}
                  onChange={(e) => onUpdateCertificate({ ...certificate, periodText: e.target.value })}
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-semibold focus:outline-none tactile-input cursor-pointer"
                >
                  <option value="por motivo de doença e necessidade de repouso">Afastamento por motivo de doença / Repouso</option>
                  <option value="para fins de comparecimento a consulta médica e realização de exames">Comparecimento a consulta e exames</option>
                  <option value="para fins de acompanhamento de dependente menor de idade">Acompanhamento de dependente menor</option>
                  <option value="para fins de aptidão física e práticas desportivas">Aptidão para atividades físicas</option>
                  <option value="por motivo de pós-operatório e recuperação cirúrgica">Recuperação pós-cirúrgica</option>
                  <option value="para fins de perícia médica e avaliação previdenciária">Avaliação pericial / Previdência</option>
                </select>
              </div>
            </div>

            {/* Days off presets and dates */}
            <div 
              className="p-4 rounded-xl border space-y-3 tactile-flat"
              style={{
                backgroundColor: darkMode ? 'var(--surface-inset)' : 'var(--bg-app)',
                borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
              }}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-sky-500" />
                  <span>Período de Afastamento:</span>
                </span>
                <span className="text-xs font-bold text-sky-600 dark:text-sky-400">
                  {certificate.daysOff} {certificate.daysOff === 1 ? 'dia de repouso' : 'dias de repouso'}
                </span>
              </div>

              <div className="flex items-center gap-1.5 flex-wrap">
                {[1, 2, 3, 5, 7, 10, 14, 15, 30].map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => handleDaysChange(d)}
                    className={`text-xs px-3 py-1.5 rounded-xl border font-bold transition-all cursor-pointer active:scale-95 ${
                      certificate.daysOff === d
                        ? 'bg-sky-700 dark:bg-sky-600 text-white border-sky-600 shadow-sm'
                        : darkMode
                        ? 'bg-slate-800/80 text-slate-300 border-slate-700/60 hover:bg-slate-700 hover:text-white'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-sky-50 hover:border-sky-300'
                    }`}
                  >
                    {d} {d === 1 ? 'dia' : 'dias'}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                <div>
                  <label className="block text-[10px] font-bold uppercase text-slate-400 mb-1">Dias de Repouso (Manual)</label>
                  <input
                    type="number"
                    min="0"
                    max="180"
                    value={certificate.daysOff}
                    onChange={(e) => handleDaysChange(parseInt(e.target.value) || 0)}
                    className="w-full p-2.5 rounded-xl border font-bold text-xs sm:text-sm focus:outline-none tactile-input text-center"
                    style={{
                      backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
                      borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)',
                      color: darkMode ? '#F1F5F9' : '#0F172A'
                    }}
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-slate-400" />
                    <span>Data de Início</span>
                  </label>
                  <input
                    type="date"
                    value={certificate.startDate}
                    onChange={(e) => onUpdateCertificate({ ...certificate, startDate: e.target.value })}
                    className="w-full p-2.5 rounded-xl border font-medium text-xs sm:text-sm focus:outline-none tactile-input"
                    style={{
                      backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
                      borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)',
                      color: darkMode ? '#F1F5F9' : '#0F172A'
                    }}
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-slate-400" />
                    <span>Data de Retorno Previsto</span>
                  </label>
                  <input
                    type="date"
                    value={certificate.endDate}
                    onChange={(e) => onUpdateCertificate({ ...certificate, endDate: e.target.value })}
                    className="w-full p-2.5 rounded-xl border font-medium text-xs sm:text-sm focus:outline-none tactile-input"
                    style={{
                      backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
                      borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)',
                      color: darkMode ? '#F1F5F9' : '#0F172A'
                    }}
                  />
                </div>
              </div>
            </div>

            {/* CID-10 Section with Search Autocomplete Integration */}
            <div 
              className="p-4 sm:p-5 rounded-2xl border space-y-4"
              style={{
                backgroundColor: darkMode ? 'var(--surface-inset)' : '#FDFBF7',
                borderColor: darkMode ? 'rgba(56, 142, 230, 0.2)' : 'rgba(15, 98, 146, 0.15)'
              }}
            >
              {/* Checkbox toggle */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.06)' }}>
                <div className="flex items-center gap-2.5">
                  <input
                    type="checkbox"
                    id="toggle-include-cid"
                    checked={certificate.includeCID}
                    onChange={(e) => onUpdateCertificate({ ...certificate, includeCID: e.target.checked })}
                    className="w-4 h-4 rounded text-sky-700 focus:ring-sky-500 cursor-pointer"
                  />
                  <label htmlFor="toggle-include-cid" className="text-xs sm:text-sm font-bold cursor-pointer select-none" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                    Incluir Código CID-10 no Atestado
                  </label>
                </div>

                <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                  <span>Exige autorização expressa do paciente (Res. CFM 1.658/2002)</span>
                </div>
              </div>

              {certificate.includeCID ? (
                <div className="space-y-4">
                  {/* Intelligent CID Search & Auto-Fill Component */}
                  <CidSearchBar
                    darkMode={darkMode}
                    selectedCode={certificate.cid10Code}
                    selectedDescription={certificate.cid10Description}
                    onSelectCid={handleSelectCidForCertificate}
                    onClearCid={handleClearCidCertificate}
                    label="Buscador Inteligente de CID-10 (Preenchimento Automático)"
                    placeholder="Digite o diagnóstico ou código (ex: J00, Asma, Lombalgia, Dengue, A09, Ansiedade, R50)..."
                    showQuickChips={true}
                    variant="certificate"
                  />

                  {/* Direct Code & Description manual inputs for fine-tuning */}
                  <div className="pt-2 grid grid-cols-1 sm:grid-cols-4 gap-3">
                    <div className="sm:col-span-1">
                      <label className="block text-[10px] font-bold uppercase text-slate-400 mb-1">Código CID-10</label>
                      <input
                        type="text"
                        value={certificate.cid10Code || ''}
                        onChange={(e) => onUpdateCertificate({ ...certificate, cid10Code: e.target.value.toUpperCase() })}
                        placeholder="Ex: J00"
                        className="w-full p-2.5 rounded-xl border text-xs sm:text-sm font-mono font-bold focus:outline-none tactile-input text-center"
                        style={{
                          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
                          borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)',
                          color: darkMode ? '#388EE6' : '#0369A1'
                        }}
                      />
                    </div>

                    <div className="sm:col-span-3">
                      <label className="block text-[10px] font-bold uppercase text-slate-400 mb-1">Descrição do Diagnóstico (Edição Livre)</label>
                      <input
                        type="text"
                        value={certificate.cid10Description || ''}
                        onChange={(e) => onUpdateCertificate({ ...certificate, cid10Description: e.target.value })}
                        placeholder="Ex: Nasofaringite aguda (resfriado comum)..."
                        className="w-full p-2.5 rounded-xl border text-xs sm:text-sm font-medium focus:outline-none tactile-input"
                        style={{
                          backgroundColor: darkMode ? 'var(--surface-elevated)' : 'var(--surface-card)',
                          borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)',
                          color: darkMode ? '#F1F5F9' : '#0F172A'
                        }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-3.5 rounded-xl border border-dashed border-slate-500/20 text-center text-xs text-slate-400">
                  <span>Inclusão de CID desativada. O atestado será gerado sem a informação codificada da doença.</span>
                </div>
              )}
            </div>

            {/* Observations */}
            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1">
                Observações Complementares / Recomendações (Opcional)
              </label>
              <textarea
                rows={2}
                value={certificate.observations}
                onChange={(e) => onUpdateCertificate({ ...certificate, observations: e.target.value })}
                placeholder="Ex: Paciente esteve sob cuidados médicos das 08h às 11h. Recomenda-se repouso domiciliar e hidratação oral..."
                className="w-full p-3 rounded-xl text-xs sm:text-sm font-normal focus:outline-none tactile-input leading-relaxed"
              />
            </div>
          </div>
        </div>
      )}

      {/* ENCAMINHAMENTO MÉDICO FORM */}
      {currentSubTab === 'referral' && (
        <div className="space-y-4">
          <div 
            className="tactile-card p-4 sm:p-5 md:p-6 rounded-2xl space-y-5"
          >
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)' }}>
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-sm"
                  style={{
                    backgroundColor: darkMode ? '#155730' : '#15803D',
                    border: '1px solid rgba(255, 255, 255, 0.12)'
                  }}
                >
                  <Share2 className="w-5 h-5 text-slate-100" strokeWidth={1.75} />
                </div>
                <div>
                  <h3 className="font-bold text-base sm:text-lg" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                    Guia de Encaminhamento & Referência Especializada
                  </h3>
                  <p className="text-xs text-slate-400 font-medium">
                    Referência e contrarreferência para ambulatórios de especialidades e hospitais.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <button
                  type="button"
                  onClick={handleSendReferralWhatsApp}
                  className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 cursor-pointer active:scale-95 transition-all shadow-tactile-btn"
                  title="Enviar a guia de encaminhamento diretamente pelo WhatsApp"
                >
                  <Send className="w-4 h-4" strokeWidth={2} />
                  <span>Enviar no WhatsApp</span>
                </button>

                <button
                  type="button"
                  onClick={() => onNavigateToPrint('referral')}
                  className="tactile-btn-success px-4 py-2.5 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2 cursor-pointer active:scale-95 transition-transform"
                >
                  <Download className="w-4 h-4" strokeWidth={1.75} />
                  <span>Visualizar & Baixar PDF</span>
                </button>
              </div>
            </div>

            {/* Patient data for Referral */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <User className="w-3.5 h-3.5 text-slate-400" />
                  <span>Nome do Paciente</span>
                </label>
                <input
                  type="text"
                  value={patient?.name ?? referral.patientName ?? ''}
                  onChange={(e) => handlePatientNameChange(e.target.value)}
                  placeholder="Nome completo do paciente..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-semibold focus:outline-none tactile-input"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <Hash className="w-3.5 h-3.5 text-slate-400" />
                  <span>Documento (RG / CPF)</span>
                </label>
                <input
                  type="text"
                  value={patient?.documentNumber ?? referral.documentNumber ?? ''}
                  onChange={(e) => handlePatientDocChange(e.target.value)}
                  placeholder="Ex: RG 12.345.678-9 ou CPF..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-medium focus:outline-none tactile-input"
                />
              </div>
            </div>

            {/* Specialty & Destination */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <Stethoscope className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Especialidade de Destino</span>
                </label>
                <select
                  value={referral.destinationSpecialty}
                  onChange={(e) => onUpdateReferral({ ...referral, destinationSpecialty: e.target.value })}
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-semibold focus:outline-none tactile-input cursor-pointer"
                >
                  {specialtiesList.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" />
                  <span>Serviço / Hospital de Destino</span>
                </label>
                <input
                  type="text"
                  value={referral.destinationInstitution || ''}
                  onChange={(e) => onUpdateReferral({ ...referral, destinationInstitution: e.target.value })}
                  placeholder="Ex: Ambulatório de Especialidades / HU..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-medium focus:outline-none tactile-input"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1">Grau de Prioridade</label>
                <div className="flex items-center gap-1.5">
                  {(['eletivo', 'prioritario', 'urgente'] as const).map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => onUpdateReferral({ ...referral, priority: p })}
                      className={`flex-1 py-2.5 rounded-xl text-xs font-bold capitalize border transition-all cursor-pointer active:scale-95 ${
                        referral.priority === p
                          ? p === 'urgente'
                            ? 'bg-rose-700 text-white border-rose-600 shadow-sm'
                            : p === 'prioritario'
                            ? 'bg-amber-700 text-white border-amber-600 shadow-sm'
                            : 'bg-emerald-700 text-white border-emerald-600 shadow-sm'
                          : darkMode
                          ? 'bg-slate-800/80 text-slate-400 border-slate-700/60 hover:bg-slate-700 hover:text-slate-200'
                          : 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Motivo & Resumo Clínico */}
            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1">Motivo do Encaminhamento</label>
              <input
                type="text"
                value={referral.reason}
                onChange={(e) => onUpdateReferral({ ...referral, reason: e.target.value })}
                placeholder="Ex: Avaliação especializada e conduta terapêutica..."
                className="w-full p-3 rounded-xl text-xs sm:text-sm font-medium focus:outline-none tactile-input"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1">Resumo da História Clínica & Exame Físico</label>
              <textarea
                rows={3}
                value={referral.clinicalSummary}
                onChange={(e) => onUpdateReferral({ ...referral, clinicalSummary: e.target.value })}
                placeholder="Ex: Paciente com história de episódios recorrentes de broncoespasmo..."
                className="w-full p-3 rounded-xl text-xs sm:text-sm font-normal focus:outline-none tactile-input leading-relaxed"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1">Exames Relevantes Realizados</label>
                <textarea
                  rows={3}
                  value={referral.relevantExams}
                  onChange={(e) => onUpdateReferral({ ...referral, relevantExams: e.target.value })}
                  placeholder="Ex: Hemograma completo sem alterações, RX de tórax com hiperinsuflação discreta..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-normal focus:outline-none tactile-input leading-relaxed"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-400 mb-1">
                  Texto da Hipótese Diagnóstica (CID-10)
                </label>
                <textarea
                  rows={3}
                  value={referral.hypothesisCID}
                  onChange={(e) => onUpdateReferral({ ...referral, hypothesisCID: e.target.value })}
                  placeholder="Ex: J45.9 - Asma não especificada / J30.4 - Rinite alérgica..."
                  className="w-full p-3 rounded-xl text-xs sm:text-sm font-medium focus:outline-none tactile-input leading-relaxed font-sans"
                />
              </div>
            </div>

            {/* Integrated CID-10 Finder for Referral / Encaminhamento */}
            <div 
              className="p-4 sm:p-5 rounded-2xl border space-y-3.5"
              style={{
                backgroundColor: darkMode ? '#0E1713' : '#F4FBF7',
                borderColor: darkMode ? 'rgba(16, 185, 129, 0.25)' : 'rgba(21, 128, 61, 0.18)'
              }}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b pb-2.5" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.06)' }}>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-500" />
                  <h4 className="text-xs sm:text-sm font-bold" style={{ color: darkMode ? '#F1F5F9' : '#0F172A' }}>
                    Buscador de CID-10 para Encaminhamento
                  </h4>
                </div>
                <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                  Clique no diagnóstico para preencher ou adicionar à hipótese
                </span>
              </div>

              {/* Specialty suggestions bar */}
              {currentSpecialtySuggestions.length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 block">
                    Sugestões para {referral.destinationSpecialty}:
                  </span>

                  <div className="flex items-center gap-1.5 flex-wrap">
                    {currentSpecialtySuggestions.map((item) => (
                      <button
                        key={item.code}
                        type="button"
                        onClick={() => handleAppendCidForReferral({ code: item.code, description: item.label })}
                        className="text-[11px] px-2.5 py-1 rounded-lg border font-semibold flex items-center gap-1.5 cursor-pointer active:scale-95 transition-all"
                        style={{
                          backgroundColor: darkMode ? '#152E22' : 'var(--surface-card)',
                          borderColor: darkMode ? 'rgba(52, 211, 153, 0.3)' : 'rgba(21, 128, 61, 0.2)',
                          color: darkMode ? '#6EE7B7' : '#166534'
                        }}
                        title={`Adicionar ${item.code} - ${item.label}`}
                      >
                        <span className="font-mono font-bold">{item.code}</span>
                        <span>{item.label}</span>
                        <Plus className="w-3 h-3 text-emerald-500" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* General CID Search Bar for Referral */}
              <CidSearchBar
                darkMode={darkMode}
                selectedCode=""
                selectedDescription=""
                onSelectCid={handleSelectCidForReferral}
                onAppendCid={handleAppendCidForReferral}
                label="Pesquisar Qualquer Diagnóstico CID-10"
                placeholder="Buscar diagnóstico CID para o encaminhamento (ex: Pneumonia, Asma, Enxaqueca, Fibromialgia, G43, J45)..."
                showQuickChips={false}
                variant="referral"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
