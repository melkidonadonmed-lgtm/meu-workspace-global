export interface UnifiedMedication {
  id: string;
  name: string;
  activeIngredient: string;
  route: string;
  category: 'analgesicos' | 'antibioticos' | 'cardio' | 'diabetes' | 'respiratorio' | 'gastro' | 'snc' | 'outros';
  defaultQuantity: string;
  defaultPosology: string;
  isSpecialControl?: boolean;
  isPediatric?: boolean;
  pediatricDoseMgKg?: number;
  pediatricConcentrationMgMl?: number;
  pediatricUnitType?: 'drops' | 'ml' | 'mg' | 'sache';
  pediatricMaxDoseMg?: number;
  pediatricDefaultDays?: number;
}

export const UNIFIED_MEDICATIONS: UnifiedMedication[] = [
  // ==========================================
  // 1. ANALGÉSICOS, ANTITÉRMICOS E ANTI-INFLAMATÓRIOS (AINES)
  // ==========================================
  {
    id: 'dipirona-500mg',
    name: 'Dipirona Sódica 500mg comprimido (Novalgina, Anador)',
    activeIngredient: 'Dipirona monoidratada',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 6 em 6 horas em caso de dor ou febre.'
  },
  {
    id: 'dipirona-1g',
    name: 'Dipirona Sódica 1g comprimido (Novalgina 1g)',
    activeIngredient: 'Dipirona monoidratada',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 6 em 6 horas se dor ou febre intensa.'
  },
  {
    id: 'dipirona-gotas-500mg',
    name: 'Dipirona Sódica 500mg/mL gotas (Novalgina Gotas)',
    activeIngredient: 'Dipirona monoidratada',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Tomar 1 gota por kg de peso de 6 em 6 horas se dor ou febre (máx 40 gotas).',
    isPediatric: true,
    pediatricDoseMgKg: 20,
    pediatricConcentrationMgMl: 500,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 1000
  },
  {
    id: 'dipirona-ampola',
    name: 'Dipirona Sódica 500mg/mL ampola 2mL (1g) / 5mL (2,5g)',
    activeIngredient: 'Dipirona monoidratada',
    route: 'Uso Intravenoso',
    category: 'analgesicos',
    defaultQuantity: '2 ampolas',
    defaultPosology: 'Aplicar 1 ampola (1g) IV lenta diluída em 100mL SF 0,9% de 6/6h.'
  },
  {
    id: 'paracetamol-500mg',
    name: 'Paracetamol 500mg comprimido (Tylenol, Sonridor)',
    activeIngredient: 'Paracetamol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 6 em 6 horas em caso de dor ou febre (máx 4g/dia).'
  },
  {
    id: 'paracetamol-750mg',
    name: 'Paracetamol 750mg comprimido (Tylenol 750)',
    activeIngredient: 'Paracetamol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 6 em 6 horas se dor ou febre.'
  },
  {
    id: 'paracetamol-gotas-200mg',
    name: 'Paracetamol 200mg/mL gotas (Tylenol Gotas)',
    activeIngredient: 'Paracetamol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (15 mL)',
    defaultPosology: 'Tomar 1 gota por kg de peso de 6 em 6 horas se dor ou febre (máx 35 gotas).',
    isPediatric: true,
    pediatricDoseMgKg: 15,
    pediatricConcentrationMgMl: 200,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 750
  },
  {
    id: 'paracetamol-gotas-100mg-bebe',
    name: 'Paracetamol 100mg/mL gotas bebê (Tylenol Bebê)',
    activeIngredient: 'Paracetamol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (15 mL)',
    defaultPosology: 'Administrar 1 dose calculada com seringa dosadora de 6 em 6 horas.',
    isPediatric: true,
    pediatricDoseMgKg: 15,
    pediatricConcentrationMgMl: 100,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 500
  },
  {
    id: 'paracetamol-solucao-32mg',
    name: 'Paracetamol 32mg/mL (160mg/5mL) solução oral',
    activeIngredient: 'Paracetamol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (60 mL)',
    defaultPosology: 'Dar volume calculado em mL de 6 em 6 horas se dor ou febre.',
    isPediatric: true,
    pediatricDoseMgKg: 15,
    pediatricConcentrationMgMl: 32,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 750
  },
  {
    id: 'ibuprofeno-600mg',
    name: 'Ibuprofeno 600mg comprimido (Advil, Alivium, Buprovil)',
    activeIngredient: 'Ibuprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas após refeições por 3 a 5 dias.'
  },
  {
    id: 'ibuprofeno-400mg',
    name: 'Ibuprofeno 400mg comprimido / cápsula (Advil 400)',
    activeIngredient: 'Ibuprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (16 cápsulas)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas por 3 a 5 dias.'
  },
  {
    id: 'ibuprofeno-100mg-gotas',
    name: 'Ibuprofeno 100mg/mL gotas (Alivium 100)',
    activeIngredient: 'Ibuprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Tomar 1 gota por kg de peso de 8 em 8 horas por 3 dias se dor ou febre (máx 30-40 gotas).',
    isPediatric: true,
    pediatricDoseMgKg: 10,
    pediatricConcentrationMgMl: 100,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 400
  },
  {
    id: 'ibuprofeno-50mg-gotas',
    name: 'Ibuprofeno 50mg/mL gotas (Alivium 50)',
    activeIngredient: 'Ibuprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (30 mL)',
    defaultPosology: 'Tomar 2 gotas por kg de peso de 8 em 8 horas por 3 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 10,
    pediatricConcentrationMgMl: 50,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 400
  },
  {
    id: 'ibuprofeno-30mg-susp',
    name: 'Ibuprofeno 30mg/mL suspensão oral (Alivium)',
    activeIngredient: 'Ibuprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (100 mL)',
    defaultPosology: 'Dar volume calculado em mL de 8 em 8 horas por 3 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 10,
    pediatricConcentrationMgMl: 30,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 400
  },
  {
    id: 'cetoprofeno-100mg',
    name: 'Cetoprofeno 100mg comprimido (Profenid)',
    activeIngredient: 'Cetoprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas por 3 a 5 dias.'
  },
  {
    id: 'cetoprofeno-150mg-biprofenid',
    name: 'Cetoprofeno 150mg comprimido lib. prolongada (Bi-Profenid)',
    activeIngredient: 'Cetoprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia por 3 a 5 dias.'
  },
  {
    id: 'cetoprofeno-gotas-20mg',
    name: 'Cetoprofeno 20mg/mL gotas (Profenid Gotas)',
    activeIngredient: 'Cetoprofeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Tomar 1 gota por kg de peso corporal de 8 em 8 horas por 3 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 1,
    pediatricConcentrationMgMl: 20,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 50
  },
  {
    id: 'cetoprofeno-injetavel-100mg',
    name: 'Cetoprofeno 100mg pó liofilizado injetável IV/IM',
    activeIngredient: 'Cetoprofeno',
    route: 'Uso Intravenoso',
    category: 'analgesicos',
    defaultQuantity: '2 frascos-ampola',
    defaultPosology: 'Infundir 100mg diluído em 100mL SF 0,9% IV de 12/12h por até 48h.'
  },
  {
    id: 'diclofenaco-sodico-50mg',
    name: 'Diclofenaco Sódico 50mg comprimido (Voltaren)',
    activeIngredient: 'Diclofenaco sódico',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas por 3 a 5 dias.'
  },
  {
    id: 'diclofenaco-sodico-75mg-retard',
    name: 'Diclofenaco Sódico 75mg / 100mg lib. prolongada (Voltaren Retard/SR)',
    activeIngredient: 'Diclofenaco sódico',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia após refeição.'
  },
  {
    id: 'diclofenaco-potassico-50mg',
    name: 'Diclofenaco Potássico 50mg comprimido (Cataflam)',
    activeIngredient: 'Diclofenaco potássico',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 drágeas)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas por 3 dias.'
  },
  {
    id: 'diclofenaco-potassico-gotas-15mg',
    name: 'Diclofenaco Potássico 15mg/mL gotas (Cataflam Gotas)',
    activeIngredient: 'Diclofenaco potássico',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Tomar 1 gota por kg de peso corporal de 8 em 8 horas por 3 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 1,
    pediatricConcentrationMgMl: 15,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 50
  },
  {
    id: 'diclofenaco-ampola-75mg',
    name: 'Diclofenaco Sódico 75mg/3mL ampola IM (Voltaren)',
    activeIngredient: 'Diclofenaco sódico',
    route: 'Uso Intramuscular',
    category: 'analgesicos',
    defaultQuantity: '2 ampolas',
    defaultPosology: 'Aplicar 1 ampola (75mg) IM profundo 1 vez ao dia por no máx 2 dias.'
  },
  {
    id: 'meloxicam-15mg',
    name: 'Meloxicam 15mg comprimido (Movatec, Bioflac)',
    activeIngredient: 'Meloxicam',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia após o almoço por 5 a 7 dias.'
  },
  {
    id: 'meloxicam-7-5mg',
    name: 'Meloxicam 7,5mg comprimido (Movatec, Bioflac)',
    activeIngredient: 'Meloxicam',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia.'
  },
  {
    id: 'nimesulida-100mg',
    name: 'Nimesulida 100mg comprimido (Nisulid, Maxsulid)',
    activeIngredient: 'Nimesulida',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (12 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 12 em 12 horas após refeições por no máx 5 dias (Adultos e ≥ 12 anos).'
  },
  {
    id: 'nimesulida-gotas-50mg',
    name: 'Nimesulida 50mg/mL gotas (Nisulid Gotas)',
    activeIngredient: 'Nimesulida',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (15 mL)',
    defaultPosology: 'Tomar 1 gota por kg a cada 12 horas por no máx 5 dias (Restrito a ≥ 12 anos).'
  },
  {
    id: 'celecoxibe-200mg',
    name: 'Celecoxibe 200mg cápsulas (Celebra)',
    activeIngredient: 'Celecoxibe',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral 1 a 2 vezes ao dia por 5 a 7 dias.'
  },
  {
    id: 'etoricoxibe-90mg',
    name: 'Etoricoxibe 90mg comprimido (Arcoxia)',
    activeIngredient: 'Etoricoxibe',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (7 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia por até 5 dias.'
  },
  {
    id: 'naproxeno-500mg',
    name: 'Naproxeno 500mg comprimido (Flanax 550mg)',
    activeIngredient: 'Naproxeno',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas por 3 a 5 dias.'
  },
  {
    id: 'tenoxicam-20mg',
    name: 'Tenoxicam 20mg comprimido / pó injetável (Tilatil, Teflan)',
    activeIngredient: 'Tenoxicam',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido (ou 1 ampola IV/IM) 1 vez ao dia por 5 dias.'
  },
  {
    id: 'piroxicam-20mg',
    name: 'Piroxicam 20mg cápsula (Feldene)',
    activeIngredient: 'Piroxicam',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (15 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral 1 vez ao dia junto à refeição.'
  },
  {
    id: 'acido-mefenamico-500mg',
    name: 'Ácido Mefenâmico 500mg comprimido (Ponstan)',
    activeIngredient: 'Ácido mefenâmico',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (24 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas durante o período de dor.'
  },
  {
    id: 'clonixinato-lisina-ciclobenzaprina',
    name: 'Clonixinato de Lisina + Ciclobenzaprina (Dolamin Flex)',
    activeIngredient: 'Clonixinato de lisina + ciclobenzaprina',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (15 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas por 3 a 5 dias.'
  },
  {
    id: 'buscopan-composto-comp',
    name: 'Escopolamina + Dipirona comprimido (Buscopan Composto)',
    activeIngredient: 'Butilbrometo de escopolamina + dipirona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos via oral de 8 em 8 horas se dor em cólica.'
  },
  {
    id: 'buscopan-composto-ampola',
    name: 'Escopolamina + Dipirona ampola 5mL (Buscopan Composto)',
    activeIngredient: 'Butilbrometo de escopolamina + dipirona',
    route: 'Uso Intravenoso',
    category: 'analgesicos',
    defaultQuantity: '2 ampolas',
    defaultPosology: 'Infundir 1 ampola diluída em 100mL SF 0,9% IV lento.'
  },
  {
    id: 'dorflex-comp',
    name: 'Dipirona + Orfenadrina + Cafeína (Dorflex)',
    activeIngredient: 'Dipirona + citrato de orfenadrina + cafeína',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (24 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos (ou 30 a 60 gotas) de 6 em 6 horas se dor muscular.'
  },
  {
    id: 'torsilax-comp',
    name: 'Paracetamol + Cafeína + Carisoprodol + Diclofenaco (Torsilax, Tandrilax)',
    activeIngredient: 'Paracetamol + carisoprodol + diclofenaco + cafeína',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 12 em 12 horas por no máx 5 dias.'
  },
  {
    id: 'neosaldina-drageas',
    name: 'Dipirona + Isometepteno + Cafeína (Neosaldina)',
    activeIngredient: 'Dipirona + mucato de isometepteno + cafeína',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 drágeas)',
    defaultPosology: 'Tomar 1 a 2 drágeas (ou 30 a 60 gotas) de 6 em 6 horas se cefaleia.'
  },
  {
    id: 'dramin-b6-comp',
    name: 'Dimenidrinato + Piridoxina (Dramin B6)',
    activeIngredient: 'Dimenidrinato + cloridrato de piridoxina',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido (ou 20 a 40 gotas) de 6 em 6 horas se náuseas ou vômitos.'
  },
  {
    id: 'plasil-10mg',
    name: 'Metoclopramida 10mg comprimido (Plasil)',
    activeIngredient: 'Cloridrato de metoclopramida',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas 30 min antes das refeições.'
  },
  {
    id: 'ondansetrona-4mg-flash',
    name: 'Ondansetrona 4mg orodispersível (Vonau Flash, Ono)',
    activeIngredient: 'Cloridrato de ondansetrona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 comprimidos)',
    defaultPosology: 'Dissolver 1 comprimido sobre a língua de 8 em 8 horas se náuseas/vômitos.'
  },
  {
    id: 'ondansetrona-sol-oral-0-8mg',
    name: 'Ondansetrona 0,8mg/mL (4mg/5mL) solução oral (Vonau)',
    activeIngredient: 'Cloridrato de ondansetrona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (50 mL)',
    defaultPosology: 'Dar 0,15 mg/kg de 8 em 8 horas se náuseas ou vômitos persistentes.',
    isPediatric: true,
    pediatricDoseMgKg: 0.15,
    pediatricConcentrationMgMl: 0.8,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 8
  },
  {
    id: 'ondansetrona-ampola-4mg',
    name: 'Ondansetrona 2mg/mL ampola 2mL (4mg) e 4mL (8mg)',
    activeIngredient: 'Cloridrato de ondansetrona',
    route: 'Uso Intravenoso',
    category: 'analgesicos',
    defaultQuantity: '2 ampolas',
    defaultPosology: 'Infundir 4mg a 8mg IV lento ou diluído em 100mL SF 0,9% a cada 8 horas.'
  },
  {
    id: 'tramadol-50mg',
    name: 'Tramadol 50mg cápsulas (Tramal, Sylador)',
    activeIngredient: 'Cloridrato de tramadol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 ou 20 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral de 6 em 6 horas se dor moderada (máx 400mg/dia).',
    isSpecialControl: true
  },
  {
    id: 'tramadol-gotas-100mg',
    name: 'Tramadol 100mg/mL gotas (Tramal Gotas)',
    activeIngredient: 'Cloridrato de tramadol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (10 mL)',
    defaultPosology: 'Tomar 20 a 40 gotas via oral de 6 em 6 horas.',
    isSpecialControl: true
  },
  {
    id: 'codeina-30mg',
    name: 'Codeína 30mg comprimido (Codein)',
    activeIngredient: 'Fosfato de codeína',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 4 em 4 horas ou 6 em 6 horas se dor moderada.',
    isSpecialControl: true
  },
  {
    id: 'tylex-30mg',
    name: 'Codeína 30mg + Paracetamol 500mg (Tylex 30, Paco)',
    activeIngredient: 'Fosfato de codeína + paracetamol',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (12 ou 24 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 6 em 6 horas se dor moderada.',
    isSpecialControl: true
  },
  {
    id: 'morfina-10mg',
    name: 'Morfina 10mg / 30mg comprimido (Dimorf)',
    activeIngredient: 'Sulfato de morfina',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (50 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 4 em 4 horas com resgate se dor oncológica.',
    isSpecialControl: true
  },
  {
    id: 'prednisona-20mg',
    name: 'Prednisona 20mg comprimido (Meticorten)',
    activeIngredient: 'Prednisona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos pela manhã por 5 dias com desmame subsequente.'
  },
  {
    id: 'prednisolona-sol-3mg',
    name: 'Prednisolona 3mg/mL solução oral (Prelone, Predsim)',
    activeIngredient: 'Fosfato sódico de prednisolona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (60 mL)',
    defaultPosology: 'Dar dose pediátrica calculada (1 a 2 mg/kg/dia) 1x ao dia pela manhã por 3 a 5 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 1,
    pediatricConcentrationMgMl: 3,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 60,
    pediatricDefaultDays: 5
  },
  {
    id: 'prednisolona-gotas-11mg',
    name: 'Prednisolona 11mg/mL gotas (Predsim Gotas)',
    activeIngredient: 'Fosfato sódico de prednisolona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Tomar 2 gotas por kg de peso 1 vez ao dia pela manhã por 3 a 5 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 1,
    pediatricConcentrationMgMl: 11,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 60
  },
  {
    id: 'dexametasona-4mg',
    name: 'Dexametasona 4mg comprimido (Decadron)',
    activeIngredient: 'Dexametasona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 caixa (10 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã por 3 dias.'
  },
  {
    id: 'dexametasona-elixir-0-1mg',
    name: 'Dexametasona 0,1mg/mL elixir (Decadron Elixir)',
    activeIngredient: 'Dexametasona',
    route: 'Uso Oral',
    category: 'analgesicos',
    defaultQuantity: '1 frasco (120 mL)',
    defaultPosology: 'Tomar volume calculado em mL conforme indicação médica.',
    isPediatric: true,
    pediatricDoseMgKg: 0.15,
    pediatricConcentrationMgMl: 0.1,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 10
  },
  {
    id: 'dexametasona-ampola-4mg',
    name: 'Dexametasona 4mg/mL ampola 2,5mL (Decadron Injetável)',
    activeIngredient: 'Fosfato dissódico de dexametasona',
    route: 'Uso Intravenoso',
    category: 'analgesicos',
    defaultQuantity: '2 ampolas',
    defaultPosology: 'Aplicar 4mg a 10mg IV ou IM 1 vez ao dia.'
  },
  {
    id: 'hidrocortisona-injetavel',
    name: 'Hidrocortisona 100mg / 500mg pó injetável (Cortisonal, Flebocortid)',
    activeIngredient: 'Succinato sódico de hidrocortisona',
    route: 'Uso Intravenoso',
    category: 'analgesicos',
    defaultQuantity: '2 frascos-ampola',
    defaultPosology: 'Adulto: 100mg a 500mg IV lento a cada 6 a 8 horas. Pediatria: 5mg/kg IV.'
  },
  {
    id: 'diprospan-ampola',
    name: 'Dipropionato + Fosfato de Betametasona (Diprospan, Celestone Soluspan)',
    activeIngredient: 'Dipropionato de betametasona + fosfato dissódico de betametasona',
    route: 'Uso Intramuscular',
    category: 'analgesicos',
    defaultQuantity: '1 ampola (1 mL)',
    defaultPosology: 'Aplicar 1 ampola (1mL) IM profundo em dose única (PROIBIDO USO IV).'
  },

  // ==========================================
  // 2. ANTIBIÓTICOS, ANTIFÚNGICOS E ANTIPARASITÁRIOS
  // ==========================================
  {
    id: 'amoxicilina-500mg',
    name: 'Amoxicilina 500mg cápsulas (Amoxil, Novocilin)',
    activeIngredient: 'Amoxicilina tri-hidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 caixas (30 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral de 8 em 8 horas durante 7 a 10 dias.'
  },
  {
    id: 'amoxicilina-875mg',
    name: 'Amoxicilina 875mg comprimido (Novocilin 875)',
    activeIngredient: 'Amoxicilina tri-hidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (14 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas durante 7 a 10 dias.'
  },
  {
    id: 'amoxicilina-susp-250mg',
    name: 'Amoxicilina 250mg/5mL suspensão oral (Amoxil, Novocilin)',
    activeIngredient: 'Amoxicilina tri-hidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 frascos (150 mL)',
    defaultPosology: 'Dar dose pediátrica calculada (50mg/kg/dia) de 8 em 8 horas por 10 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 50,
    pediatricConcentrationMgMl: 50,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 1500,
    pediatricDefaultDays: 10
  },
  {
    id: 'amoxicilina-susp-400mg',
    name: 'Amoxicilina 400mg/5mL suspensão oral (Novocilin 400)',
    activeIngredient: 'Amoxicilina tri-hidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 frasco (100 mL)',
    defaultPosology: 'Dar dose calculada de 12 em 12 horas durante 10 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 50,
    pediatricConcentrationMgMl: 80,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 1500,
    pediatricDefaultDays: 10
  },
  {
    id: 'amox-clav-875mg',
    name: 'Amoxicilina + Clavulanato 875/125mg (Clavulin BD)',
    activeIngredient: 'Amoxicilina + clavulanato de potássio',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (14 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas durante 7 a 10 dias.'
  },
  {
    id: 'amox-clav-500mg',
    name: 'Amoxicilina + Clavulanato 500/125mg (Clavulin)',
    activeIngredient: 'Amoxicilina + clavulanato de potássio',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 caixas (21 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas por 7 a 10 dias.'
  },
  {
    id: 'amox-clav-susp-400mg',
    name: 'Amoxicilina + Clavulanato 400/57mg/5mL suspensão (Clavulin BD)',
    activeIngredient: 'Amoxicilina + clavulanato de potássio',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 frascos (70 mL)',
    defaultPosology: 'Dar dose calculada (45 a 90 mg/kg/dia) de 12 em 12 horas por 10 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 50,
    pediatricConcentrationMgMl: 80,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 1750,
    pediatricDefaultDays: 10
  },
  {
    id: 'amox-clav-susp-250mg',
    name: 'Amoxicilina + Clavulanato 250/62,5mg/5mL suspensão (Clavulin)',
    activeIngredient: 'Amoxicilina + clavulanato de potássio',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 frascos (75 mL)',
    defaultPosology: 'Dar dose calculada de 8 em 8 horas durante 10 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 50,
    pediatricConcentrationMgMl: 50,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 1500,
    pediatricDefaultDays: 10
  },
  {
    id: 'cefalexina-500mg',
    name: 'Cefalexina 500mg comprimido / cápsula (Keflex, Cefagel)',
    activeIngredient: 'Cefalexina monoidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 caixas (28 cápsulas)',
    defaultPosology: 'Tomar 1 comprimido via oral de 6 em 6 horas durante 7 a 10 dias.'
  },
  {
    id: 'cefalexina-susp-250mg',
    name: 'Cefalexina 250mg/5mL suspensão oral (Keflex)',
    activeIngredient: 'Cefalexina monoidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 frascos (100 mL)',
    defaultPosology: 'Dar dose calculada (50mg/kg/dia) de 6 em 6 horas durante 7 a 10 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 50,
    pediatricConcentrationMgMl: 50,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 2000,
    pediatricDefaultDays: 10
  },
  {
    id: 'ceftriaxona-1g-injetavel',
    name: 'Ceftriaxona 1g frasco-ampola IV/IM (Rocefin)',
    activeIngredient: 'Ceftriaxona dissódica',
    route: 'Uso Intravenoso',
    category: 'antibioticos',
    defaultQuantity: '3 frascos-ampola',
    defaultPosology: 'Adulto: 1g a 2g IV/IM 1x ao dia. Pediatria: 50 a 80 mg/kg/dia 1x ao dia.',
    isPediatric: true,
    pediatricDoseMgKg: 50,
    pediatricConcentrationMgMl: 100,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 2000
  },
  {
    id: 'azitromicina-500mg',
    name: 'Azitromicina 500mg comprimido (Zitromax, Astro)',
    activeIngredient: 'Azitromicina di-hidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (5 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia durante 5 dias (ou dose única de 1g para DST).'
  },
  {
    id: 'azitromicina-susp-200mg',
    name: 'Azitromicina 200mg/5mL suspensão oral (Astro, Zitromax)',
    activeIngredient: 'Azitromicina di-hidratada',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 frasco (600 mg)',
    defaultPosology: 'Dar dose pediátrica calculada (10mg/kg/dia) 1x ao dia por 5 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 10,
    pediatricConcentrationMgMl: 40,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 500,
    pediatricDefaultDays: 5
  },
  {
    id: 'claritromicina-500mg',
    name: 'Claritromicina 500mg comprimido (Klaricid)',
    activeIngredient: 'Claritromicina',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (14 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas por 7 a 10 dias.'
  },
  {
    id: 'ciprofloxacino-500mg',
    name: 'Ciprofloxacino 500mg comprimido (Cipro)',
    activeIngredient: 'Cloridrato de ciprofloxacino',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (14 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas por 7 a 14 dias.'
  },
  {
    id: 'levofloxacino-500mg',
    name: 'Levofloxacino 500mg comprimido (Levaquin, Tamiram)',
    activeIngredient: 'Levofloxacino hemi-hidratado',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (7 ou 10 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia por 7 a 10 dias.'
  },
  {
    id: 'bactrim-f-comprimido',
    name: 'Sulfametoxazol + Trimetoprima 800+160mg comprimido (Bactrim F)',
    activeIngredient: 'Sulfametoxazol + trimetoprima',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (10 ou 20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas por 7 a 14 dias.'
  },
  {
    id: 'bactrim-susp-oral',
    name: 'Sulfametoxazol + Trimetoprima 200+40mg/5mL suspensão (Bactrim)',
    activeIngredient: 'Sulfametoxazol + trimetoprima',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 frasco (100 mL)',
    defaultPosology: 'Dar dose calculada (40mg SMZ + 8mg TMP/kg/dia) de 12/12h por 7 a 10 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 40,
    pediatricConcentrationMgMl: 40,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 800,
    pediatricDefaultDays: 10
  },
  {
    id: 'nitrofurantoina-100mg',
    name: 'Nitrofurantoína 100mg cápsulas (Macrodantina)',
    activeIngredient: 'Nitrofurantoína',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (28 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral de 6 em 6 horas junto às refeições por 5 dias.'
  },
  {
    id: 'fosfomicina-3g',
    name: 'Fosfomicina Trometamol 3g envelope (Monuril)',
    activeIngredient: 'Fosfomicina trometamol',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 envelope',
    defaultPosology: 'Diluir em meio copo de água e tomar à noite com bexiga vazia em dose única.'
  },
  {
    id: 'metronidazol-400mg',
    name: 'Metronidazol 400mg comprimido (Flagyl)',
    activeIngredient: 'Metronidazol',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (24 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas por 7 dias (PROIBIDO ÁLCOOL).'
  },
  {
    id: 'clindamicina-300mg',
    name: 'Clindamicina 300mg cápsulas (Dalacin C)',
    activeIngredient: 'Cloridrato de clindamicina',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '2 caixas (32 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral de 6 em 6 horas por 7 a 10 dias.'
  },
  {
    id: 'doxiciclina-100mg',
    name: 'Doxiciclina 100mg comprimido (Vibramicina, Doxiclin)',
    activeIngredient: 'Hiclato de doxiciclina',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (15 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas após refeições por 7 a 14 dias.'
  },
  {
    id: 'benzetacil-1200000',
    name: 'Benzilpenicilina Benzatina 1.200.000 UI (Benzetacil)',
    activeIngredient: 'Benzilpenicilina benzatina',
    route: 'Uso Intramuscular',
    category: 'antibioticos',
    defaultQuantity: '1 frasco-ampola',
    defaultPosology: 'Aplicar 1 ampola (1.200.000 UI) IM profundo em dose única.'
  },
  {
    id: 'benzetacil-600000',
    name: 'Benzilpenicilina Benzatina 600.000 UI (Benzetacil Infantil)',
    activeIngredient: 'Benzilpenicilina benzatina',
    route: 'Uso Intramuscular',
    category: 'antibioticos',
    defaultQuantity: '1 frasco-ampola',
    defaultPosology: 'Aplicar 1 ampola (600.000 UI) IM profundo para crianças < 27 kg.'
  },
  {
    id: 'fluconazol-150mg',
    name: 'Fluconazol 150mg cápsula (Zoltec)',
    activeIngredient: 'Fluconazol',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (1 ou 2 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral em dose única (ou 1x por semana conforme indicação).'
  },
  {
    id: 'nistatina-susp-oral',
    name: 'Nistatina 100.000 UI/mL suspensão oral (Micostatin, Canditrat)',
    activeIngredient: 'Nistatina',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 frasco (50 mL)',
    defaultPosology: 'Bochechar e engolir 4 a 6 mL de 6 em 6 horas por 7 a 14 dias.'
  },
  {
    id: 'albendazol-400mg',
    name: 'Albendazol 400mg comprimido mastigável (Zentel)',
    activeIngredient: 'Albendazol',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (1 ou 3 comprimidos)',
    defaultPosology: 'Mastigar 1 comprimido em dose única à noite (ou 3 dias consecutivos se Giardíase).'
  },
  {
    id: 'ivermectina-6mg',
    name: 'Ivermectina 6mg comprimido (Revectina)',
    activeIngredient: 'Ivermectina',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (2 ou 4 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido para cada 30kg de peso corporal em dose única em jejum.'
  },
  {
    id: 'nitazoxanida-500mg',
    name: 'Nitazoxanida 500mg comprimido (Annita)',
    activeIngredient: 'Nitazoxanida',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (6 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas com alimentos por 3 dias.'
  },
  {
    id: 'aciclovir-200mg',
    name: 'Aciclovir 200mg / 400mg comprimido (Zovirax)',
    activeIngredient: 'Aciclovir',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (25 ou 30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 4 em 4 horas (5x ao dia) por 5 a 7 dias.'
  },
  {
    id: 'oseltamivir-75mg',
    name: 'Oseltamivir 75mg cápsulas (Tamiflu)',
    activeIngredient: 'Fosfato de oseltamivir',
    route: 'Uso Oral',
    category: 'antibioticos',
    defaultQuantity: '1 caixa (10 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral de 12 em 12 horas durante 5 dias consecutivos.'
  },

  // ==========================================
  // 3. CARDIOLOGIA, HIPERTENSÃO E ANTICOAGULAÇÃO
  // ==========================================
  {
    id: 'losartana-50mg',
    name: 'Losartana Potássica 50mg comprimido (Cozaar, Corus, Aradois)',
    activeIngredient: 'Losartana potássica',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã (ou de 12/12h se necessário).'
  },
  {
    id: 'losartana-100mg',
    name: 'Losartana Potássica 100mg comprimido (Cozaar 100)',
    activeIngredient: 'Losartana potássica',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'losartana-hctz-50-12',
    name: 'Losartana + Hidroclorotiazida 50+12,5mg / 100+25mg (Hyzaar)',
    activeIngredient: 'Losartana potássica + hidroclorotiazida',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'enalapril-10mg',
    name: 'Maleato de Enalapril 10mg / 20mg comprimido (Renitec)',
    activeIngredient: 'Maleato de enalapril',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas (ou 1x ao dia).'
  },
  {
    id: 'captopril-25mg',
    name: 'Captopril 25mg / 50mg comprimido (Capoten, Captosen)',
    activeIngredient: 'Captopril',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 8/8h ou 12/12h 1 hora antes das refeições.'
  },
  {
    id: 'anlodipino-5mg',
    name: 'Besilato de Anlodipino 5mg comprimido (Norvasc, Cordarex)',
    activeIngredient: 'Besilato de anlodipino',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia à noite.'
  },
  {
    id: 'anlodipino-10mg',
    name: 'Besilato de Anlodipino 10mg comprimido (Norvasc 10)',
    activeIngredient: 'Besilato de anlodipino',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia à noite.'
  },
  {
    id: 'hidroclorotiazida-25mg',
    name: 'Hidroclorotiazida 25mg comprimido (Clorana)',
    activeIngredient: 'Hidroclorotiazida',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'clortalidona-25mg',
    name: 'Clortalidona 12,5mg / 25mg / 50mg comprimido (Higroton)',
    activeIngredient: 'Clortalidona',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'furosemida-40mg',
    name: 'Furosemida 40mg comprimido (Lasix)',
    activeIngredient: 'Furosemida',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (20 ou 30 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos via oral pela manhã em jejum.'
  },
  {
    id: 'furosemida-ampola-20mg',
    name: 'Furosemida 10mg/mL ampola 2mL (20mg) (Lasix)',
    activeIngredient: 'Furosemida',
    route: 'Uso Intravenoso',
    category: 'cardio',
    defaultQuantity: '4 ampolas',
    defaultPosology: 'Infundir 20mg a 40mg IV lento em edema agudo de pulmão ou sobrecarga.'
  },
  {
    id: 'espironolactona-25mg',
    name: 'Espironolactona 25mg comprimido (Aldactone)',
    activeIngredient: 'Espironolactona',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'metoprolol-succinato-50mg',
    name: 'Succinato de Metoprolol 25mg / 50mg / 100mg (Selozok)',
    activeIngredient: 'Succinato de metoprolol',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'atenolol-50mg',
    name: 'Atenolol 25mg / 50mg / 100mg comprimido (Ablok, Atenol)',
    activeIngredient: 'Atenolol',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'carvedilol-12-5mg',
    name: 'Carvedilol 3,125mg / 6,25mg / 12,5mg / 25mg (Coreg, Cardilol)',
    activeIngredient: 'Carvedilol',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas junto às refeições.'
  },
  {
    id: 'propranolol-40mg',
    name: 'Propranolol 40mg comprimido (Inderal, Amprax)',
    activeIngredient: 'Cloridrato de propranolol',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 ou 60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 12 em 12 horas.'
  },
  {
    id: 'metildopa-250mg',
    name: 'Metildopa 250mg / 500mg comprimido (Aldomet)',
    activeIngredient: 'Metildopa',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 8 em 8 horas (1ª escolha na hipertensão gestacional).'
  },
  {
    id: 'sinvastatina-20mg',
    name: 'Sinvastatina 20mg / 40mg comprimido (Zocor, Sinvacor)',
    activeIngredient: 'Sinvastatina',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia à noite ao deitar.'
  },
  {
    id: 'atorvastatina-20mg',
    name: 'Atorvastatina 10mg / 20mg / 40mg / 80mg (Citalor, Lipitor)',
    activeIngredient: 'Atorvastatina cálcica',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia à noite.'
  },
  {
    id: 'rosuvastatina-20mg',
    name: 'Rosuvastatina 5mg / 10mg / 20mg / 40mg (Crestor)',
    activeIngredient: 'Rosuvastatina cálcica',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia.'
  },
  {
    id: 'aas-100mg',
    name: 'Ácido Acetilsalicílico 100mg (Aspirina Prevent, Somalgin Cardio)',
    activeIngredient: 'Ácido acetilsalicílico',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral após o almoço para profilaxia cardiovascular.'
  },
  {
    id: 'clopidogrel-75mg',
    name: 'Clopidogrel 75mg comprimido (Plavix)',
    activeIngredient: 'Bissulfato de clopidogrel',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (28 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia.'
  },
  {
    id: 'varfarina-5mg',
    name: 'Varfarina Sódica 5mg comprimido (Marevan, Coumadin)',
    activeIngredient: 'Varfarina sódica',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar dose titulada para manter RNI alvo entre 2,0 e 3,0.'
  },
  {
    id: 'rivaroxabana-20mg',
    name: 'Rivaroxabana 10mg / 15mg / 20mg (Xarelto)',
    activeIngredient: 'Rivaroxabana',
    route: 'Uso Oral',
    category: 'cardio',
    defaultQuantity: '1 caixa (28 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia com alimentos.'
  },

  // ==========================================
  // 4. DIABETES, ENDOCRINOLOGIA E METABOLISMO
  // ==========================================
  {
    id: 'metformina-850mg',
    name: 'Cloridrato de Metformina 850mg (Glifage)',
    activeIngredient: 'Cloridrato de metformina',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 2 vezes ao dia junto às principais refeições.'
  },
  {
    id: 'metformina-500mg-xr',
    name: 'Cloridrato de Metformina 500mg XR lib. prolongada (Glifage XR)',
    activeIngredient: 'Cloridrato de metformina',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos ao jantar.'
  },
  {
    id: 'gliclazida-mr-30mg',
    name: 'Gliclazida MR 30mg liberação modificada (Diamicron MR)',
    activeIngredient: 'Gliclazida',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (30 ou 60 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos via oral pela manhã antes do café.'
  },
  {
    id: 'glibenclamida-5mg',
    name: 'Glibenclamida 5mg comprimido (Daonil)',
    activeIngredient: 'Glibenclamida',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral antes do café da manhã.'
  },
  {
    id: 'dapagliflozina-10mg',
    name: 'Dapagliflozina 10mg comprimido (Forxiga)',
    activeIngredient: 'Dapagliflozina',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'empagliflozina-25mg',
    name: 'Empagliflozina 10mg / 25mg comprimido (Jardiance)',
    activeIngredient: 'Empagliflozina',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.'
  },
  {
    id: 'vildagliptina-50mg',
    name: 'Vildagliptina 50mg comprimido (Galvus)',
    activeIngredient: 'Vildagliptina',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (56 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido 2 vezes ao dia.'
  },
  {
    id: 'insulina-nph-100ui',
    name: 'Insulina Humana NPH 100 UI/mL frasco 10mL / refil (Humulin N, Novolin N)',
    activeIngredient: 'Insulina humana NPH',
    route: 'Uso Subcutâneo',
    category: 'diabetes',
    defaultQuantity: '1 frasco (10 mL)',
    defaultPosology: 'Aplicar dose prescrita SC pela manhã (e antes do jantar) com seringa/caneta.'
  },
  {
    id: 'insulina-regular-100ui',
    name: 'Insulina Humana Regular 100 UI/mL frasco 10mL (Humulin R, Novolin R)',
    activeIngredient: 'Insulina humana regular',
    route: 'Uso Subcutâneo',
    category: 'diabetes',
    defaultQuantity: '1 frasco (10 mL)',
    defaultPosology: 'Aplicar dose prescrita SC 30 min antes das refeições.'
  },
  {
    id: 'levotiroxina-50mcg',
    name: 'Levotiroxina Sódica 25mcg / 50mcg / 75mcg / 100mcg (Puran T4, Synthroid, Levoid)',
    activeIngredient: 'Levotiroxina sódica',
    route: 'Uso Oral',
    category: 'diabetes',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido em jejum absoluto com água, 30 a 60 minutos antes do café da manhã.'
  },

  // ==========================================
  // 5. RESPIRATÓRIO, ASMA E ANTI-ALÉRGICOS
  // ==========================================
  {
    id: 'salbutamol-spray-100mcg',
    name: 'Sulfato de Salbutamol Spray 100mcg/dose (Aerolin)',
    activeIngredient: 'Sulfato de salbutamol',
    route: 'Uso Inalatória',
    category: 'respiratorio',
    defaultQuantity: '1 frasco spray (200 doses) + espaçador',
    defaultPosology: 'Inalar 2 a 4 jatos com espaçador em caso de falta de ar ou chiado no peito.'
  },
  {
    id: 'salbutamol-gotas-5mg',
    name: 'Sulfato de Salbutamol 5mg/mL solução para inalação (Aerolin Gotas)',
    activeIngredient: 'Sulfato de salbutamol',
    route: 'Uso Inalatória',
    category: 'respiratorio',
    defaultQuantity: '1 frasco (10 mL)',
    defaultPosology: 'Fazer inalação com 10 a 20 gotas em 3mL SF 0,9% de 6 em 6 horas.',
    isPediatric: true,
    pediatricDoseMgKg: 0.15,
    pediatricConcentrationMgMl: 5,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 5
  },
  {
    id: 'ipratropio-gotas-0-25mg',
    name: 'Brometo de Ipratrópio 0,25mg/mL gotas (Atrovent)',
    activeIngredient: 'Brometo de ipratrópio',
    route: 'Uso Inalatória',
    category: 'respiratorio',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Fazer inalação com 20 a 40 gotas (crianças: 10 a 20 gotas) em 3mL SF 0,9% de 8/8h.',
    isPediatric: true,
    pediatricDoseMgKg: 0.05,
    pediatricConcentrationMgMl: 0.25,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 0.5
  },
  {
    id: 'budesonida-spray-nasal-50mcg',
    name: 'Budesonida Spray Nasal 32mcg / 50mcg / 64mcg / 100mcg (Busonid, Noex)',
    activeIngredient: 'Budesonida',
    route: 'Uso Nasal',
    category: 'respiratorio',
    defaultQuantity: '1 frasco spray (120 doses)',
    defaultPosology: 'Aplicar 1 a 2 jatos em cada narina 1 a 2 vezes ao dia.'
  },
  {
    id: 'budesonida-inalacao-0-25mg',
    name: 'Budesonida 0,25mg/mL / 0,50mg/mL suspensão para inalação (Pulmicort)',
    activeIngredient: 'Budesonida',
    route: 'Uso Inalatória',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (5 ou 20 flaconetes)',
    defaultPosology: 'Fazer inalação com 1 flaconete (2mL) 1 a 2 vezes ao dia.'
  },
  {
    id: 'beclometasona-spray-250mcg',
    name: 'Dipropionato de Beclometasona 50mcg / 250mcg spray (Clenil HFA)',
    activeIngredient: 'Dipropionato de beclometasona',
    route: 'Uso Inalatória',
    category: 'respiratorio',
    defaultQuantity: '1 frasco spray (200 doses)',
    defaultPosology: 'Inalar 1 a 2 jatos de 12 em 12 horas com espaçador (lavar a boca após).'
  },
  {
    id: 'loratadina-10mg',
    name: 'Loratadina 10mg comprimido (Claritin)',
    activeIngredient: 'Loratadina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (12 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia por 5 a 7 dias.'
  },
  {
    id: 'loratadina-xarope-1mg',
    name: 'Loratadina 1mg/mL xarope (Claritin Xarope)',
    activeIngredient: 'Loratadina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 frasco (100 mL)',
    defaultPosology: 'Dar 5mL (< 30 kg) ou 10mL (≥ 30 kg) via oral 1 vez ao dia.',
    isPediatric: true,
    pediatricDoseMgKg: 0.2,
    pediatricConcentrationMgMl: 1,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 10
  },
  {
    id: 'desloratadina-5mg',
    name: 'Desloratadina 5mg comprimido (Desalex, Esalerg)',
    activeIngredient: 'Desloratadina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (10 ou 30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia.'
  },
  {
    id: 'cetirizina-10mg',
    name: 'Cetirizina 10mg comprimido / gotas 10mg/mL (Zyrtec)',
    activeIngredient: 'Dicloridrato de cetirizina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (12 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido (ou 20 gotas) 1 vez ao dia à noite.'
  },
  {
    id: 'dexclorfeniramina-2mg',
    name: 'Dexclorfeniramina 2mg comprimido (Polaramine)',
    activeIngredient: 'Maleato de dexclorfeniramina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (20 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral de 8 em 8 horas.'
  },
  {
    id: 'dexclorfeniramina-xarope',
    name: 'Dexclorfeniramina 0,4mg/mL xarope (Polaramine)',
    activeIngredient: 'Maleato de dexclorfeniramina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 frasco (120 mL)',
    defaultPosology: 'Tomar 5mL de 8 em 8 horas.',
    isPediatric: true,
    pediatricDoseMgKg: 0.15,
    pediatricConcentrationMgMl: 0.4,
    pediatricUnitType: 'ml',
    pediatricMaxDoseMg: 6
  },
  {
    id: 'hidroxizina-25mg',
    name: 'Hidroxizina 25mg comprimido (Hixizine)',
    activeIngredient: 'Cloridrato de hidroxizina',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 8/8h ou à noite ao deitar.'
  },
  {
    id: 'acetilcisteina-600mg',
    name: 'Acetilcisteína 200mg / 600mg sachê efervescente (Fluimucil)',
    activeIngredient: 'Acetilcisteína',
    route: 'Uso Oral',
    category: 'respiratorio',
    defaultQuantity: '1 caixa (16 envelopes)',
    defaultPosology: 'Dissolver 1 sachê em meio copo de água 1 vez ao dia (600mg) ou de 8/8h (200mg).'
  },
  {
    id: 'soro-fisiologico-spray-0-9',
    name: 'Cloreto de Sódio 0,9% spray nasal (Sorine, Rinosoro)',
    activeIngredient: 'Cloreto de sódio',
    route: 'Uso Nasal',
    category: 'respiratorio',
    defaultQuantity: '1 frasco (50 mL)',
    defaultPosology: 'Aplicar 2 a 3 jatos em cada narina várias vezes ao dia.'
  },

  // ==========================================
  // 6. GASTROENTEROLOGIA E REIDRATAÇÃO
  // ==========================================
  {
    id: 'omeprazol-20mg',
    name: 'Omeprazol 20mg cápsula (Losec, Prilosec, Pratiprazol)',
    activeIngredient: 'Omeprazol magnésico',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '2 caixas (56 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula pela manhã em jejum 30 minutos antes do café por 4 a 8 semanas.'
  },
  {
    id: 'pantoprazol-40mg',
    name: 'Pantoprazol 40mg comprimido (Pantozol)',
    activeIngredient: 'Pantoprazol sódico',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 caixa (28 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido pela manhã em jejum 30 min antes do café.'
  },
  {
    id: 'domperidona-10mg',
    name: 'Domperidona 10mg comprimido (Motilium)',
    activeIngredient: 'Domperidona',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido 15 a 30 minutos antes das refeições (máx 3x/dia).'
  },
  {
    id: 'simeticona-gotas-75mg',
    name: 'Simeticona 75mg/mL gotas (Luftal)',
    activeIngredient: 'Simeticona',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 frasco (15 mL)',
    defaultPosology: 'Tomar 20 a 30 gotas (crianças: 5 a 10 gotas) de 8 em 8 horas se gases.',
    isPediatric: true,
    pediatricDoseMgKg: 1,
    pediatricConcentrationMgMl: 75,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 40
  },
  {
    id: 'sais-reidratacao-sro',
    name: 'Sais de Reidratação Oral (SRO) envelopes (Reidrat, Pedialyte)',
    activeIngredient: 'Cloreto de sódio + glicose + cloreto de potássio + citrato',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '6 envelopes',
    defaultPosology: 'Diluir 1 envelope em 1L de água tratada. Beber após cada evacuação líquida ou vômito.'
  },
  {
    id: 'sulfato-zinco-gotas-10mg',
    name: 'Sulfato de Zinco 10mg Zn elementar/mL gotas (Zincoquel, Bio-Zinco)',
    activeIngredient: 'Sulfato de zinco heptaidratado',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Lactentes < 6 meses: 10mg/dia; ≥ 6 meses: 20mg/dia por 10 a 14 dias seguidos.',
    isPediatric: true,
    pediatricDoseMgKg: 1,
    pediatricConcentrationMgMl: 10,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 20
  },
  {
    id: 'racecadotrila-100mg',
    name: 'Racecadotrila 100mg cápsulas (Tiorfan)',
    activeIngredient: 'Racecadotrila',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 caixa (9 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula de 8 em 8 horas antes das refeições até normalizar o trânsito.'
  },
  {
    id: 'racecadotrila-sache-30mg',
    name: 'Racecadotrila 10mg / 30mg sachês granulado (Tiorfan Pediátrico)',
    activeIngredient: 'Racecadotrila',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 caixa (16 sachês)',
    defaultPosology: 'Dar 1,5mg/kg/dose dissolvido em água de 8 em 8 horas por até 5 dias.',
    isPediatric: true,
    pediatricDoseMgKg: 1.5,
    pediatricConcentrationMgMl: 30,
    pediatricUnitType: 'mg',
    pediatricMaxDoseMg: 30
  },
  {
    id: 'lactulose-xarope',
    name: 'Lactulose 667mg/mL xarope (Lactulona)',
    activeIngredient: 'Lactulose',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 frasco (120 mL)',
    defaultPosology: 'Tomar 15 a 30 mL 1 a 2 vezes ao dia.'
  },
  {
    id: 'sulfato-ferroso-40mg',
    name: 'Sulfato Ferroso 40mg Fe elementar comprimido (Ferro)',
    activeIngredient: 'Sulfato ferroso',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '2 caixas (60 comprimidos)',
    defaultPosology: 'Tomar 1 a 2 comprimidos ao dia 1 hora antes do almoço com suco cítrico.'
  },
  {
    id: 'sulfato-ferroso-gotas-25mg',
    name: 'Sulfato Ferroso gotas (25mg Fe/mL = 1,25mg/gota)',
    activeIngredient: 'Sulfato ferroso',
    route: 'Uso Oral',
    category: 'gastro',
    defaultQuantity: '1 frasco (30 mL)',
    defaultPosology: 'Pediatria: 1 a 2 mg Fe/kg/dia profilático ou 3 a 5 mg Fe/kg/dia terapêutico.',
    isPediatric: true,
    pediatricDoseMgKg: 4,
    pediatricConcentrationMgMl: 25,
    pediatricUnitType: 'drops',
    pediatricMaxDoseMg: 60
  },

  // ==========================================
  // 7. SISTEMA NERVOSO CENTRAL, PSIQUIATRIA E CONTROLE ESPECIAL
  // ==========================================
  {
    id: 'fluoxetina-20mg',
    name: 'Cloridrato de Fluoxetina 20mg cápsula (Prozac, Daforin)',
    activeIngredient: 'Cloridrato de fluoxetina',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula pela manhã após o café da manhã.',
    isSpecialControl: true
  },
  {
    id: 'sertralina-50mg',
    name: 'Cloridrato de Sertralina 50mg comprimido (Zoloft, Assert, Tolrest)',
    activeIngredient: 'Cloridrato de sertralina',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral pela manhã (ou à noite).',
    isSpecialControl: true
  },
  {
    id: 'escitalopram-10mg',
    name: 'Oxalato de Escitalopram 10mg / 20mg (Lexapro, Exodus)',
    activeIngredient: 'Oxalato de escitalopram',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral 1 vez ao dia pela manhã.',
    isSpecialControl: true
  },
  {
    id: 'amitriptilina-25mg',
    name: 'Cloridrato de Amitriptilina 25mg comprimido (Tryptanol, Amytril)',
    activeIngredient: 'Cloridrato de amitriptilina',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral à noite ao deitar.',
    isSpecialControl: true
  },
  {
    id: 'diazepam-10mg',
    name: 'Diazepam 5mg / 10mg comprimido (Valium)',
    activeIngredient: 'Diazepam',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido à noite ou se crise de ansiedade aguda.',
    isSpecialControl: true
  },
  {
    id: 'clonazepam-2mg',
    name: 'Clonazepam 0,5mg / 2mg comprimido (Rivotril)',
    activeIngredient: 'Clonazepam',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido via oral à noite ao deitar.',
    isSpecialControl: true
  },
  {
    id: 'clonazepam-gotas-2-5mg',
    name: 'Clonazepam 2,5mg/mL gotas (Rivotril Gotas)',
    activeIngredient: 'Clonazepam',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 frasco (20 mL)',
    defaultPosology: 'Tomar gotas prescritas (cada gota = 0,1mg) à noite com água.',
    isSpecialControl: true
  },
  {
    id: 'zolpidem-10mg',
    name: 'Hemitartarato de Zolpidem 10mg comprimido (Stilnox, Patz)',
    activeIngredient: 'Hemitartarato de zolpidem',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (20 ou 30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido imediatamente antes de deitar na cama (indutor do sono).',
    isSpecialControl: true
  },
  {
    id: 'pregabalina-75mg',
    name: 'Pregabalina 75mg / 150mg cápsulas (Lyrica, Dorene)',
    activeIngredient: 'Pregabalina',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 cápsulas)',
    defaultPosology: 'Tomar 1 cápsula via oral 1 a 2 vezes ao dia.',
    isSpecialControl: true
  },
  {
    id: 'carbamazepina-200mg',
    name: 'Carbamazepina 200mg / 400mg comprimido (Tegretol)',
    activeIngredient: 'Carbamazepina',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 12 em 12 horas ou 8 em 8 horas.',
    isSpecialControl: true
  },
  {
    id: 'haloperidol-5mg',
    name: 'Haloperidol 1mg / 5mg comprimido (Haldol)',
    activeIngredient: 'Haloperidol',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido de 8/8h ou 12/12h conforme indicação.',
    isSpecialControl: true
  },
  {
    id: 'risperidona-2mg',
    name: 'Risperidona 1mg / 2mg / 3mg comprimido (Risperdal)',
    activeIngredient: 'Risperidona',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido à noite ao deitar (ou 12/12h).',
    isSpecialControl: true
  },
  {
    id: 'quetiapina-25mg',
    name: 'Quetiapina 25mg / 100mg / 200mg comprimido (Seroquel)',
    activeIngredient: 'Hemifumarato de quetiapina',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido à noite ao deitar.',
    isSpecialControl: true
  },
  {
    id: 'cloridrato-metilfenidato-10mg',
    name: 'Cloridrato de Metilfenidato 10mg (Ritalina)',
    activeIngredient: 'Cloridrato de metilfenidato',
    route: 'Uso Oral',
    category: 'snc',
    defaultQuantity: '1 caixa (30 ou 60 comprimidos)',
    defaultPosology: 'Tomar 1 comprimido 1 a 2 vezes ao dia (manhã e almoço).',
    isSpecialControl: true
  }
];

export const CATEGORY_LABELS: Record<string, string> = {
  all: 'Todos os Fármacos',
  analgesicos: 'Sintomáticos & AINEs',
  antibioticos: 'Antibióticos & Antiparasitários',
  cardio: 'Cardiovascular & HAS',
  diabetes: 'Diabetes & Endócrino',
  respiratorio: 'Respiratório & Alergia',
  gastro: 'Gastroenterologia',
  snc: 'SNC & Psiquiatria'
};
