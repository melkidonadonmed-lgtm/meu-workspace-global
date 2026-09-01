import { PediatricMedication } from '../types';

export interface CalculatedDoseResult {
  medicationId: string;
  weightKg: number;
  calculatedMg: number;
  calculatedMl: number;
  calculatedDrops?: number;
  isMaxDoseReached: boolean;
  rawDoseText: string;
  volumeText: string;
  dropsText: string;
  formattedPrescriptionText: string;
  instructionsText?: string;
  summaryBadge: string;
}

export function calculatePediatricDose(
  med: PediatricMedication,
  weightKg: number
): CalculatedDoseResult {
  const safeWeight = Math.max(0.5, Math.min(120, weightKg));
  
  // Custom fixed dosages (e.g. Vitamin D or fixed dose labels)
  if (med.unitType === 'fixed' || med.standardDoseMgKg === 0) {
    const text = med.doseCustomLabel || med.observations;
    return {
      medicationId: med.id,
      weightKg: safeWeight,
      calculatedMg: 0,
      calculatedMl: 0,
      calculatedDrops: med.unitType === 'drops' ? 10 : undefined,
      isMaxDoseReached: false,
      rawDoseText: 'Dose Fixa',
      volumeText: '-',
      dropsText: text.includes('gotas') ? text : '-',
      formattedPrescriptionText: `Administrar ${text} por via ${med.route.toLowerCase()}, ${med.frequency.toLowerCase()}.`,
      instructionsText: `Administrar ${text} por via ${med.route.toLowerCase()}, ${med.frequency.toLowerCase()}.`,
      summaryBadge: text
    };
  }

  // Calculate base mg
  let targetMg = safeWeight * med.standardDoseMgKg;
  let isMaxDoseReached = false;

  if (med.maxDoseMg > 0 && targetMg > med.maxDoseMg) {
    targetMg = med.maxDoseMg;
    isMaxDoseReached = true;
  }

  // Calculate volume (mL)
  let volumeMl = 0;
  if (med.concentrationMgPerMl > 0) {
    volumeMl = targetMg / med.concentrationMgPerMl;
  }

  // Calculate drops if drop-based medication
  const dropsPerMl = med.dropsPerMl || 20;
  let calculatedDrops: number | undefined = undefined;

  if (med.unitType === 'drops') {
    // Exact or clinically standard drop counts
    if (med.id === 'paracetamol-gotas') {
      // 1 gota / kg / dose (200 mg/mL -> 1 mL = 20 gotas = 200 mg -> 1 gota = 10 mg; 15 mg/kg -> 1.5 gotas/kg or clinically 1 gota/kg/dose)
      const drops = Math.min(100, Math.round(safeWeight * 1.0)); // standard pediatric practice in Brazil: 1 gota/kg
      calculatedDrops = drops;
      volumeMl = drops / 20;
    } else if (med.id === 'dipirona-gotas') {
      // 500 mg/mL (1 gota = 25 mg). Dose 20 mg/kg -> for 12 kg = 240 mg -> approx 10 a 12 gotas (0.5 a 1 gota/kg)
      const drops = Math.min(40, Math.max(4, Math.round((targetMg / 500) * 20)));
      calculatedDrops = drops;
      volumeMl = drops / 20;
    } else if (med.id === 'ibuprofeno-gotas-50') {
      // 50 mg/mL (1 gota = 2.5 mg). 10 mg/kg -> 4 gotas/kg
      const drops = Math.min(160, Math.round(safeWeight * 3));
      calculatedDrops = drops;
      volumeMl = drops / 20;
    } else if (med.id === 'ibuprofeno-gotas-100') {
      // 100 mg/mL (1 gota = 5 mg). 10 mg/kg -> 2 gotas/kg (1 a 2 gotas por kg)
      const drops = Math.min(80, Math.max(3, Math.round(safeWeight * 1.5)));
      calculatedDrops = drops;
      volumeMl = drops / 20;
    } else if (med.id === 'simeticona-gotas') {
      const drops = safeWeight < 12 ? 8 : 16;
      calculatedDrops = drops;
      volumeMl = drops / 25;
    } else {
      calculatedDrops = Math.round(volumeMl * dropsPerMl);
    }
  }

  // Format texts
  const mgText = targetMg >= 1 ? `${Math.round(targetMg * 10) / 10} mg` : `${targetMg.toFixed(2)} mg`;
  const mlText = volumeMl >= 1 ? `${(Math.round(volumeMl * 10) / 10).toLocaleString('pt-BR')} mL` : `${(Math.round(volumeMl * 100) / 100).toLocaleString('pt-BR')} mL`;
  const dropsText = calculatedDrops !== undefined ? `${calculatedDrops} gotas` : '-';

  // Build high-fidelity prescription text
  let posologyDetail = '';
  if (med.unitType === 'drops' && calculatedDrops !== undefined) {
    posologyDetail = `Dar ${calculatedDrops} gotas (${mlText})`;
  } else {
    posologyDetail = `Administrar ${mlText} (${mgText})`;
  }

  const daysClause = med.defaultDays ? ` por ${med.defaultDays} dias` : '';
  const formattedPrescriptionText = `${posologyDetail} por via ${med.route.toLowerCase()}, ${med.frequency.toLowerCase()}${daysClause}.`;

  let summaryBadge = '';
  if (med.unitType === 'drops' && calculatedDrops !== undefined) {
    summaryBadge = `${calculatedDrops} gts (${mlText})`;
  } else {
    summaryBadge = `${mlText} (${mgText})`;
  }

  return {
    medicationId: med.id,
    weightKg: safeWeight,
    calculatedMg: targetMg,
    calculatedMl: volumeMl,
    calculatedDrops,
    isMaxDoseReached,
    rawDoseText: mgText,
    volumeText: mlText,
    dropsText,
    formattedPrescriptionText,
    instructionsText: formattedPrescriptionText,
    summaryBadge
  };
}

export function generateScheduleTimes(interval: string, initialHour: number = 8): string[] {
  let step = 6;
  if (interval.includes('4/4') || interval.includes('4 em 4')) step = 4;
  else if (interval.includes('6/6') || interval.includes('6 em 6')) step = 6;
  else if (interval.includes('8/8') || interval.includes('8 em 8')) step = 8;
  else if (interval.includes('12/12') || interval.includes('12 em 12')) step = 12;
  else if (interval.includes('24/24') || interval.includes('1x ao dia') || interval.includes('1 vez ao dia')) step = 24;
  else return [];

  const times: string[] = [];
  const count = 24 / step;
  for (let i = 0; i < count; i++) {
    const h = (initialHour + i * step) % 24;
    const str = `${h.toString().padStart(2, '0')}:00`;
    times.push(str);
  }
  return times;
}
