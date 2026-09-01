import React, { useState } from 'react';
import { UserCheck, Check, X, Shield, Eraser, Building2, Phone, MapPin } from 'lucide-react';
import { DoctorProfile } from '../types';

interface DoctorProfileModalProps {
  darkMode: boolean;
  doctor: DoctorProfile;
  onSaveDoctor: (doctor: DoctorProfile) => void;
  onClose: () => void;
}

export const DoctorProfileModal: React.FC<DoctorProfileModalProps> = ({
  darkMode,
  doctor,
  onSaveDoctor,
  onClose
}) => {
  const [formData, setFormData] = useState<DoctorProfile>({
    name: doctor?.name || '',
    crm: doctor?.crm || '',
    crmState: doctor?.crmState || 'SP',
    specialty: doctor?.specialty || 'Clínica Médica',
    rqe: doctor?.rqe || '',
    clinicName: doctor?.clinicName || '',
    address: doctor?.address || '',
    cityState: doctor?.cityState || '',
    phone: doctor?.phone || '',
    email: doctor?.email || '',
    showSignature: doctor?.showSignature ?? true,
    signatureText: doctor?.signatureText || '',
    stampText: doctor?.stampText || ''
  });

  const [showAdvancedClinic, setShowAdvancedClinic] = useState(
    Boolean(doctor?.clinicName || doctor?.address || doctor?.cityState || doctor?.phone)
  );

  const states = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
  ];

  const handleClear = () => {
    setFormData({
      name: '',
      crm: '',
      crmState: 'SP',
      specialty: '',
      rqe: '',
      clinicName: '',
      address: '',
      cityState: '',
      phone: '',
      email: '',
      showSignature: true,
      signatureText: '',
      stampText: ''
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveDoctor(formData);
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs isolate"
      role="dialog"
      aria-modal="true"
      aria-labelledby="doctor-modal-title"
    >
      <div 
        className="w-full max-w-lg rounded-2xl border overflow-hidden shadow-tactile-lg animate-in fade-in zoom-in-95 duration-200"
        style={{
          backgroundColor: darkMode ? '#0E1420' : '#FFFFFF',
          borderColor: darkMode ? 'rgba(255, 255, 255, 0.12)' : '#E3D7BD',
          boxShadow: darkMode ? '0 24px 50px -8px rgba(0,0,0,0.85), inset 0 1px 0 rgba(255,255,255,0.1)' : '0 20px 40px -8px rgba(20,32,50,0.18), inset 0 1px 0 rgba(255,255,255,0.95)'
        }}
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
              <UserCheck className="w-4 h-4" strokeWidth={2} />
            </div>
            <div>
              <h3 id="doctor-modal-title" className="font-bold text-sm sm:text-base text-navy-900 dark:text-cream-50">
                Perfil Profissional do Médico
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Nome, CRM e dados essenciais para o cabeçalho dos documentos
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar modal"
            className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 cursor-pointer active:scale-95 transition-all"
          >
            <X className="w-5 h-5" strokeWidth={2} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 max-h-[78vh] overflow-y-auto custom-scrollbar">
          
          {/* Identificação Principal (Essencial) */}
          <div className="space-y-3 p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-navy-800">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold tracking-wider text-sky-600 dark:text-sky-400">
                Identificação Obrigatória
              </span>
              <button 
                type="button"
                onClick={handleClear}
                className="text-[11px] font-semibold text-rose-500 hover:text-rose-600 flex items-center gap-1"
              >
                <Eraser className="w-3.5 h-3.5" />
                <span>Limpar campos</span>
              </button>
            </div>

            <div>
              <label htmlFor="doc-input-name" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Nome Completo com Título *
              </label>
              <input
                id="doc-input-name"
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ex: Dr. Melki Donadon"
                className="w-full px-3.5 py-2.5 rounded-xl border text-sm font-semibold focus:ring-2 focus:ring-sky-500 outline-none transition bg-white dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100"
              />
            </div>

            <div className="grid grid-cols-12 gap-2.5">
              <div className="col-span-8">
                <label htmlFor="doc-input-crm" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Número do CRM *
                </label>
                <input
                  id="doc-input-crm"
                  type="text"
                  required
                  value={formData.crm}
                  onChange={(e) => setFormData({ ...formData, crm: e.target.value })}
                  placeholder="Ex: 12345"
                  className="w-full px-3.5 py-2 rounded-xl border text-sm font-bold text-sky-600 dark:text-sky-400 focus:ring-2 focus:ring-sky-500 outline-none transition bg-white dark:bg-navy-900 border-slate-300 dark:border-navy-700"
                />
              </div>

              <div className="col-span-4">
                <label htmlFor="doc-input-state" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  UF do CRM *
                </label>
                <select
                  id="doc-input-state"
                  value={formData.crmState}
                  onChange={(e) => setFormData({ ...formData, crmState: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border text-sm font-bold focus:ring-2 focus:ring-sky-500 outline-none transition bg-white dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100 cursor-pointer"
                >
                  {states.map(st => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-12 gap-2.5">
              <div className="col-span-7">
                <label htmlFor="doc-input-specialty" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Especialidade Principal
                </label>
                <input
                  id="doc-input-specialty"
                  type="text"
                  value={formData.specialty}
                  onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                  placeholder="Ex: Clínica Médica / Pediatria"
                  className="w-full px-3 py-2 rounded-xl border text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none transition bg-white dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100"
                />
              </div>

              <div className="col-span-5">
                <label htmlFor="doc-input-rqe" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  RQE (Opcional)
                </label>
                <input
                  id="doc-input-rqe"
                  type="text"
                  value={formData.rqe || ''}
                  onChange={(e) => setFormData({ ...formData, rqe: e.target.value })}
                  placeholder="Ex: 67890"
                  className="w-full px-3 py-2 rounded-xl border text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none transition bg-white dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100"
                />
              </div>
            </div>
          </div>

          {/* Toggle Dados Opcionais do Consultório / Unidade */}
          <div>
            <button
              type="button"
              onClick={() => setShowAdvancedClinic(!showAdvancedClinic)}
              className="w-full py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-between transition-all bg-slate-100 dark:bg-navy-900 hover:bg-slate-200 dark:hover:bg-navy-800 border-slate-300 dark:border-navy-700 text-slate-700 dark:text-slate-300"
            >
              <span className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-slate-500" />
                <span>Dados de Consultório / Unidade (Opcional)</span>
              </span>
              <span className="text-[10px] font-bold text-sky-600 dark:text-sky-400">
                {showAdvancedClinic ? 'Ocultar' : 'Exibir campos'}
              </span>
            </button>

            {showAdvancedClinic && (
              <div className="mt-2.5 space-y-2.5 p-3 rounded-xl border bg-white dark:bg-navy-950 border-slate-200 dark:border-navy-800 animate-in fade-in duration-150">
                <div>
                  <label htmlFor="doc-input-clinic" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-0.5">
                    Nome da Unidade / Consultório
                  </label>
                  <input
                    id="doc-input-clinic"
                    type="text"
                    value={formData.clinicName || ''}
                    onChange={(e) => setFormData({ ...formData, clinicName: e.target.value })}
                    placeholder="Ex: USF Hamilton Gondim / Consultório Particular"
                    className="w-full px-3 py-2 rounded-lg border text-xs bg-slate-50 dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100 outline-none focus:ring-1 focus:ring-sky-500"
                  />
                </div>

                <div className="grid grid-cols-12 gap-2">
                  <div className="col-span-7">
                    <label htmlFor="doc-input-city" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-0.5">
                      Cidade - UF
                    </label>
                    <input
                      id="doc-input-city"
                      type="text"
                      value={formData.cityState || ''}
                      onChange={(e) => setFormData({ ...formData, cityState: e.target.value })}
                      placeholder="Ex: Porto Velho - RO"
                      className="w-full px-3 py-2 rounded-lg border text-xs bg-slate-50 dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100 outline-none focus:ring-1 focus:ring-sky-500"
                    />
                  </div>
                  <div className="col-span-5">
                    <label htmlFor="doc-input-phone" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-0.5">
                      Telefone / Contato
                    </label>
                    <input
                      id="doc-input-phone"
                      type="text"
                      value={formData.phone || ''}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="Ex: (69) 99999-9999"
                      className="w-full px-3 py-2 rounded-lg border text-xs bg-slate-50 dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100 outline-none focus:ring-1 focus:ring-sky-500"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="doc-input-address" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-0.5">
                    Endereço Completo
                  </label>
                  <input
                    id="doc-input-address"
                    type="text"
                    value={formData.address || ''}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    placeholder="Ex: Av. 7 de Setembro, 1200 - Sala 04"
                    className="w-full px-3 py-2 rounded-lg border text-xs bg-slate-50 dark:bg-navy-900 border-slate-300 dark:border-navy-700 text-slate-900 dark:text-slate-100 outline-none focus:ring-1 focus:ring-sky-500"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Assinatura & Carimbo */}
          <div className="p-3 rounded-xl border flex items-center justify-between bg-slate-50 dark:bg-navy-950 border-slate-200 dark:border-navy-800">
            <div className="flex items-center gap-2.5">
              <Shield className="w-4 h-4 text-emerald-500" />
              <div>
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
                  Exibir Linha de Assinatura e Carimbo
                </p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400">
                  Inclui campo formal no rodapé das folhas A4
                </p>
              </div>
            </div>
            <input
              type="checkbox"
              id="doc-input-show-sig"
              checked={formData.showSignature}
              onChange={(e) => setFormData({ ...formData, showSignature: e.target.checked })}
              className="w-4 h-4 rounded text-sky-600 focus:ring-sky-500 cursor-pointer"
            />
          </div>

          {/* Action Buttons */}
          <div className="pt-2 flex items-center justify-end gap-2.5 border-t border-slate-200 dark:border-navy-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border text-xs font-semibold hover:bg-slate-100 dark:hover:bg-navy-800 text-slate-600 dark:text-slate-300 transition active:scale-95"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-tactile-primary px-6 py-2.5 rounded-xl text-xs font-bold transition active:scale-95 flex items-center gap-1.5 cursor-pointer"
            >
              <Check className="w-4 h-4" />
              <span>Salvar Perfil</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
