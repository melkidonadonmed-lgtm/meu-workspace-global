import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { MobileBottomNav } from './components/MobileBottomNav';
import { PediatricCalculator } from './components/PediatricCalculator';
import { PrescriptionBuilder } from './components/PrescriptionBuilder';
import { ExamRequester } from './components/ExamRequester';
import { CertificateAndReferral } from './components/CertificateAndReferral';
import { ClinicalProtocolsView } from './components/ClinicalProtocolsView';
import { PrintPreview } from './components/PrintPreview';
import { PatientModal } from './components/PatientModal';
import { DoctorProfileModal } from './components/DoctorProfileModal';
import { 
  ActiveTab, 
  DoctorProfile, 
  Patient, 
  PrescriptionItem, 
  ExamItem, 
  MedicalCertificate, 
  MedicalReferral 
} from './types';

const DEFAULT_DOCTOR: DoctorProfile = {
  name: '',
  crm: '',
  crmState: 'SP',
  specialty: 'Clínica Médica',
  rqe: '',
  clinicName: '',
  address: '',
  cityState: '',
  phone: '',
  email: '',
  showSignature: true,
  stampText: ''
};

const DEFAULT_PATIENT: Patient = {
  id: '',
  name: '',
  weightKg: 0,
  birthDate: '',
  ageText: '',
  gender: 'male',
  documentNumber: '',
  phone: '',
  allergies: []
};

export default function App() {
  // Theme state (Tema Claro como padrão preferido pelo usuário)
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('prescmed_theme');
    return saved !== null ? saved === 'dark' : false;
  });

  // Responsive sidebar open state
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth >= 1024;
    }
    return false;
  });

  // Keep sidebar in sync with the desktop/mobile breakpoint (covers cases where the
  // initial width check races with the viewport still settling on first paint)
  useEffect(() => {
    const DESKTOP_BREAKPOINT = 1024;
    let wasDesktop = window.innerWidth >= DESKTOP_BREAKPOINT;

    const handleBreakpointChange = () => {
      const isDesktop = window.innerWidth >= DESKTOP_BREAKPOINT;
      if (isDesktop !== wasDesktop) {
        wasDesktop = isDesktop;
        setSidebarOpen(isDesktop);
      }
    };

    handleBreakpointChange();
    window.addEventListener('resize', handleBreakpointChange);
    return () => window.removeEventListener('resize', handleBreakpointChange);
  }, []);

  // Auto-close sidebar on mobile scroll
  useEffect(() => {
    let lastScrollY = window.scrollY;
    
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      if (currentScrollY > 30 && (currentScrollY > lastScrollY + 5 || window.innerWidth < 1024)) {
        setSidebarOpen(false);
      }
      lastScrollY = currentScrollY;
    };

    const handleTouchMove = () => {
      if (window.scrollY > 20 && window.innerWidth < 1024) {
        setSidebarOpen(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('touchmove', handleTouchMove, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('touchmove', handleTouchMove);
    };
  }, []);

  // Navigation state
  const [activeTab, setActiveTab] = useState<ActiveTab>('prescription');
  const [certSubTab, setCertSubTab] = useState<'certificate' | 'referral'>('certificate');
  const [printDocType, setPrintDocType] = useState<'prescription' | 'special_prescription' | 'exams' | 'certificate' | 'referral'>('prescription');

  const handleNavigateToPrint = (type?: 'prescription' | 'special_prescription' | 'exams' | 'certificate' | 'referral') => {
    if (type) {
      setPrintDocType(type);
    }
    setActiveTab('print_preview');
  };

  // Modals state
  const [isPatientModalOpen, setIsPatientModalOpen] = useState(false);
  const [isDoctorModalOpen, setIsDoctorModalOpen] = useState(false);

  // Doctor profile state
  const [doctor, setDoctor] = useState<DoctorProfile>(() => {
    try {
      const saved = localStorage.getItem('prescmed_doctor');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && typeof parsed === 'object') {
          return { ...DEFAULT_DOCTOR, ...parsed };
        }
      }
    } catch (e) {
      console.error('Error loading doctor from localStorage:', e);
    }
    return DEFAULT_DOCTOR;
  });

  // Patient state (starts clean)
  const [patient, setPatient] = useState<Patient>(() => {
    try {
      const saved = localStorage.getItem('prescmed_patient');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && typeof parsed === 'object') {
          return { ...DEFAULT_PATIENT, ...parsed };
        }
      }
    } catch (e) {
      console.error('Error loading patient from localStorage:', e);
    }
    return DEFAULT_PATIENT;
  });

  // Prescription items state (starts clean)
  const [prescriptionItems, setPrescriptionItems] = useState<PrescriptionItem[]>(() => {
    const saved = localStorage.getItem('prescmed_prescription');
    if (saved) {
      try { 
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) return parsed;
      } catch (e) {}
    }
    return [];
  });

  // Selected exams state
  const [selectedExams, setSelectedExams] = useState<ExamItem[]>(() => {
    const saved = localStorage.getItem('prescmed_exams');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return [];
  });

  // Clinical indication for exams
  const [examIndication, setExamIndication] = useState<string>(() => {
    return localStorage.getItem('prescmed_exam_indication') || 'Investigação clínica de rotina e controle metabólico.';
  });

  // Medical certificate state
  const [certificate, setCertificate] = useState<MedicalCertificate>(() => {
    const saved = localStorage.getItem('prescmed_certificate');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0];
    return {
      id: 'cert-1',
      patientName: '',
      documentType: 'CPF',
      documentNumber: '',
      daysOff: 2,
      startDate: today,
      endDate: tomorrow,
      periodText: 'por motivo de doença e necessidade de repouso',
      includeCID: true,
      cid10Code: 'J00',
      cid10Description: 'Nasofaringite aguda (resfriado comum)',
      observations: 'Paciente necessita de repouso e hidratação domiciliar durante o período estipulado.',
      cityDateText: (doctor.cityState || 'Brasil') + ', ' + new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' })
    };
  });

  // Medical referral state
  const [referral, setReferral] = useState<MedicalReferral>(() => {
    const saved = localStorage.getItem('prescmed_referral');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return {
      id: 'ref-1',
      patientName: '',
      documentNumber: '',
      destinationSpecialty: 'Cardiologia Ambulatorial',
      destinationInstitution: 'Ambulatório de Especialidades',
      priority: 'prioritario',
      reason: 'Investigação diagnóstica e acompanhamento especializado.',
      clinicalSummary: 'Paciente com indicação de avaliação especializada.',
      relevantExams: '',
      hypothesisCID: '',
      date: new Date().toISOString().split('T')[0]
    };
  });

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem('prescmed_theme', darkMode ? 'dark' : 'light');
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('prescmed_doctor', JSON.stringify(doctor));
  }, [doctor]);

  useEffect(() => {
    localStorage.setItem('prescmed_patient', JSON.stringify(patient));
    setCertificate(prev => ({
      ...prev,
      patientName: patient.name || '',
      documentNumber: patient.documentNumber || ''
    }));
    setReferral(prev => ({
      ...prev,
      patientName: patient.name || '',
      documentNumber: patient.documentNumber || ''
    }));
  }, [patient]);

  useEffect(() => {
    localStorage.setItem('prescmed_prescription', JSON.stringify(prescriptionItems));
  }, [prescriptionItems]);

  useEffect(() => {
    localStorage.setItem('prescmed_exams', JSON.stringify(selectedExams));
  }, [selectedExams]);

  useEffect(() => {
    localStorage.setItem('prescmed_exam_indication', examIndication);
  }, [examIndication]);

  useEffect(() => {
    localStorage.setItem('prescmed_certificate', JSON.stringify(certificate));
  }, [certificate]);

  useEffect(() => {
    localStorage.setItem('prescmed_referral', JSON.stringify(referral));
  }, [referral]);

  // Handler to update patient weight from anywhere
  const handleUpdatePatientWeight = (newWeight: number) => {
    setPatient(prev => ({ ...prev, weightKg: newWeight }));
  };

  // Handler to toggle weight calculation mode
  const handleToggleWeightCalc = (enabled: boolean) => {
    setPatient(prev => ({ ...prev, weightCalcEnabled: enabled }));
  };

  // Add prescription item handler
  const handleAddPrescriptionItem = (newItem: PrescriptionItem) => {
    setPrescriptionItems(prev => [...prev, newItem]);
  };

  // Clear prescription items (zerar receita)
  const handleClearPrescription = () => {
    setPrescriptionItems([]);
    localStorage.removeItem('prescmed_prescription');
  };

  // Clear patient data (limpar dados do paciente globalmente)
  const handleClearPatient = () => {
    const emptyPatient: Patient = {
      id: 'patient-' + Date.now(),
      name: '',
      weightKg: 0,
      birthDate: '',
      ageText: '',
      gender: 'male',
      documentNumber: '',
      phone: '',
      allergies: [],
      motherName: '',
      notes: ''
    };
    setPatient(emptyPatient);
    setCertificate(prev => ({
      ...prev,
      patientName: '',
      documentNumber: ''
    }));
    setReferral(prev => ({
      ...prev,
      patientName: '',
      documentNumber: ''
    }));
    localStorage.setItem('prescmed_patient', JSON.stringify(emptyPatient));
  };

  // Reset entire consultation (Zerar tudo: paciente + receitas + exames + documentos)
  const handleResetAll = () => {
    handleClearPatient();
    handleClearPrescription();
    setSelectedExams([]);
    localStorage.removeItem('prescmed_exams');
    setActiveTab('prescription');
  };

  return (
    <div 
      className="min-h-screen font-sans antialiased flex flex-col transition-colors duration-300"
      style={{ backgroundColor: 'var(--bg-app)', color: 'var(--text-main)' }}
    >
      {/* Top Application Header */}
      <Header
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        patient={patient}
        onOpenPatientModal={() => setIsPatientModalOpen(true)}
        prescriptionCount={prescriptionItems.length}
        selectedExamsCount={selectedExams.length}
        onQuickWeightChange={handleUpdatePatientWeight}
      />

      {/* Main Responsive Body Layout */}
      <div className="flex-1 w-full max-w-screen-2xl container mx-auto px-2.5 sm:px-4 md:px-6 lg:px-8 py-3 sm:py-5 flex gap-4 lg:gap-6 relative min-h-0">
        {/* Desktop & Tablet Persistent Sidebar */}
        <Sidebar
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
          activeTab={activeTab}
          onSelectTab={(tab) => {
            if (tab === 'patients') {
              setIsPatientModalOpen(true);
              return;
            }
            if (tab === 'certificate') {
              setCertSubTab('certificate');
            } else if (tab === 'referral') {
              setCertSubTab('referral');
            }
            setActiveTab(tab);
          }}
          isOpen={sidebarOpen}
          onToggleOpen={() => setSidebarOpen(!sidebarOpen)}
          onClose={() => setSidebarOpen(false)}
          doctor={doctor}
          patient={patient}
          prescriptionCount={prescriptionItems.length}
          selectedExamsCount={selectedExams.length}
          onOpenDoctorModal={() => setIsDoctorModalOpen(true)}
          onOpenPatientModal={() => setIsPatientModalOpen(true)}
          onClearPrescription={handleClearPrescription}
          onClearPatient={handleClearPatient}
          onResetAll={handleResetAll}
        />

        {/* Main Content Area */}
        <main className="flex-1 min-w-0 pb-20 lg:pb-6">
          {activeTab === 'prescription' && (
            <PrescriptionBuilder
              darkMode={darkMode}
              doctor={doctor}
              onUpdateDoctor={setDoctor}
              patient={patient}
              onUpdatePatient={setPatient}
              items={prescriptionItems}
              onUpdateItems={setPrescriptionItems}
              weightCalcEnabled={patient.weightCalcEnabled}
              onToggleWeightCalc={handleToggleWeightCalc}
              onClearPrescription={handleClearPrescription}
              onNavigateToPrint={() => handleNavigateToPrint('prescription')}
              onNavigateToPediatricCalc={() => setActiveTab('pediatric_calc')}
              onOpenDoctorModal={() => setIsDoctorModalOpen(true)}
              onOpenPatientModal={() => setIsPatientModalOpen(true)}
            />
          )}

          {activeTab === 'pediatric_calc' && (
            <PediatricCalculator
              darkMode={darkMode}
              patient={patient}
              onUpdatePatientWeight={handleUpdatePatientWeight}
              onAddPrescriptionItem={handleAddPrescriptionItem}
              onNavigateToPrescription={() => setActiveTab('prescription')}
            />
          )}

          {activeTab === 'exams' && (
            <ExamRequester
              darkMode={darkMode}
              patient={patient}
              selectedExams={selectedExams}
              onUpdateSelectedExams={setSelectedExams}
              onUpdateExams={setSelectedExams}
              clinicalIndication={examIndication}
              onUpdateClinicalIndication={setExamIndication}
              onNavigateToPrint={() => handleNavigateToPrint('exams')}
            />
          )}

          {(activeTab === 'certificate' || activeTab === 'referral') && (
            <CertificateAndReferral
              darkMode={darkMode}
              patient={patient}
              onUpdatePatient={setPatient}
              doctor={doctor}
              certificate={certificate}
              onUpdateCertificate={setCertificate}
              referral={referral}
              onUpdateReferral={setReferral}
              initialSubTab={certSubTab}
              onNavigateToPrint={(type) => handleNavigateToPrint(type)}
            />
          )}

          {activeTab === 'protocols' && (
            <ClinicalProtocolsView
              darkMode={darkMode}
              patient={patient}
              onAddPrescriptionItem={handleAddPrescriptionItem}
              onNavigateToPrescription={() => setActiveTab('prescription')}
            />
          )}

          {activeTab === 'print_preview' && (
            <PrintPreview
              darkMode={darkMode}
              doctor={doctor}
              patient={patient}
              prescriptionItems={prescriptionItems}
              exams={selectedExams}
              selectedExams={selectedExams}
              examIndication={examIndication}
              certificate={certificate}
              referral={referral}
              initialDocType={printDocType}
              onNavigateBack={() => setActiveTab('prescription')}
              onBack={() => setActiveTab('prescription')}
              onClearPrescription={handleClearPrescription}
              onResetAll={handleResetAll}
              onOpenDoctorModal={() => setIsDoctorModalOpen(true)}
            />
          )}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        activeTab={activeTab}
        onSelectTab={(tab) => {
          if (tab === 'certificate') {
            setCertSubTab('certificate');
          } else if (tab === 'referral') {
            setCertSubTab('referral');
          }
          setActiveTab(tab);
        }}
        prescriptionCount={prescriptionItems.length}
        selectedExamsCount={selectedExams.length}
        onOpenDoctorModal={() => setIsDoctorModalOpen(true)}
        onOpenMenu={() => setSidebarOpen(true)}
      />

      {/* Modals */}
      {isPatientModalOpen && (
        <PatientModal
          darkMode={darkMode}
          patient={patient}
          onSavePatient={setPatient}
          onClearPatient={handleClearPatient}
          onClose={() => setIsPatientModalOpen(false)}
        />
      )}

      {isDoctorModalOpen && (
        <DoctorProfileModal
          darkMode={darkMode}
          doctor={doctor}
          onSaveDoctor={setDoctor}
          onClose={() => setIsDoctorModalOpen(false)}
        />
      )}
    </div>
  );
}
