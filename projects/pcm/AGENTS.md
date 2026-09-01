# AGENTS.md — Remix PresCMed new

## Visão geral do projeto

**PresCMed** é um sistema de prescrição médica digital em português (pt-BR), voltado ao contexto brasileiro. Funcionalidades principais:

- Prescrição médica com calculadora automática de doses pediátricas por peso (mg/kg → mL/gotas).
- Solicitação de exames laboratoriais e de imagem.
- Emissão de atestados médicos e encaminhamentos (com referências à legislação CFM, ex.: Res. CFM 1.658/2002 para inclusão de CID).
- Geração de PDF dos documentos (receituário simples, receituário de controle especial, exames, atestado, encaminhamento).
- Visualização de impressão (`PrintPreview`) e protocolos clínicos pediátricos.

O projeto foi gerado a partir de um template do **Google AI Studio** (ver `metadata.json` e `README.md`), mas o código atual é uma **SPA 100% client-side**: não há backend implementado. As dependências `@google/genai`, `express` e `dotenv` estão declaradas no `package.json`, porém **não são usadas em nenhum arquivo de `src/`** — não crie código assumindo que exista um servidor ou chamadas à API Gemini. O script `clean` remove `server.js`, que não existe no repositório.

**Atenção:** este é um app do domínio médico (YMYL). As doses pediátricas usam regras clínicas específicas do Brasil (ex.: paracetamol gotas = 1 gota/kg/dose). Qualquer alteração em lógica de cálculo de doses (`src/utils/doseCalculator.ts`) ou nos catálogos de medicamentos (`src/data/`) exige revisão cuidadosa.

## Stack tecnológica

- **React 19 + TypeScript ~5.8** (modo estrito parcial — `tsconfig.json` não habilita `strict`).
- **Vite 6** como bundler e dev server (`@vitejs/plugin-react`).
- **Tailwind CSS v4** via `@tailwindcss/vite` (sem `tailwind.config.js`; a configuração é feita em CSS com `@import "tailwindcss"` e `@theme`/variáveis em `src/index.css`).
- **lucide-react** para ícones, **motion** para animações.
- **jspdf + jspdf-autotable** para geração de PDF e **html2canvas** para captura de tela dos documentos no preview.
- Gerenciador de pacotes: há `bun.lock` (Bun), mas os comandos `npm` também funcionam.

## Comandos

```bash
npm install        # ou: bun install
npm run dev        # dev server Vite na porta 3000, host 0.0.0.0
npm run build      # build de produção em dist/
npm run preview    # serve o build de produção
npm run lint       # type-check: tsc --noEmit (única forma de verificação)
npm run clean      # remove dist/ e server.js
```

**Testes:** não existe framework de testes configurado (sem Vitest/Jest/Playwright, sem arquivos de teste). A verificação disponível é `npm run lint` (TypeScript). Ao modificar lógica crítica (ex.: cálculo de doses), valide manualmente na UI via `npm run dev`.

## Estrutura do código

```
index.html              # Entry HTML (monta #root, carrega /src/main.tsx)
vite.config.ts          # Plugins React + Tailwind; alias '@' → raiz do projeto
src/
  main.tsx              # Bootstrap React (StrictMode)
  App.tsx               # Estado global da aplicação + roteamento por abas
  types.ts              # Todas as interfaces de domínio (DoctorProfile, Patient,
                        #   PediatricMedication, PrescriptionItem, ExamItem,
                        #   MedicalCertificate, MedicalReferral, ClinicalProtocol, ActiveTab)
  index.css             # Tailwind v4 + design system em CSS custom properties
                        #   (Light: canvas creme #F9F6F0 + painéis deep navy;
                        #   Dark: obsidian #0D0F12 + grafite; sombras/luz "optical physics")
  components/           # Um componente por funcionalidade (todos funcionais)
    Header.tsx, Sidebar.tsx, MobileBottomNav.tsx   # Navegação e layout
    PrescriptionBuilder.tsx                        # Construtor de receituário
    PediatricCalculator.tsx                        # Calculadora de dose por peso
    ExamRequester.tsx                              # Solicitação de exames
    CertificateAndReferral.tsx                     # Atestados e encaminhamentos
    ClinicalProtocolsView.tsx                      # Protocolos clínicos
    PrintPreview.tsx                               # Preview de impressão + exportação PDF
    PatientModal.tsx, DoctorProfileModal.tsx       # Edição de paciente e médico
    CidSearchBar.tsx                               # Busca de CID-10
  data/                 # Catálogos estáticos (dados clínicos em pt-BR)
    pediatricMeds.ts    # ~54 medicamentos pediátricos com dose mg/kg
    adultMeds.ts        # ~32 medicamentos adultos com posologia
    examCatalog.ts      # ~43 exames
    cidCatalog.ts       # Catálogo CID-10 (CIDItem: code, description, category, keywords)
  utils/
    doseCalculator.ts   # calculatePediatricDose() e generateScheduleTimes()
    pdfGenerator.ts     # generateMedicalPDF() — gera os 5 tipos de documento em PDF
```

## Arquitetura em tempo de execução

- **SPA sem roteador:** a navegação é feita por estado (`activeTab: ActiveTab`) em `App.tsx`, que renderiza condicionalmente cada view. Não há react-router nem URLs por tela.
- **Estado centralizado em `App.tsx`:** médico, paciente, itens da prescrição, exames, atestado e encaminhamento vivem em `useState` no App e são passados por props (prop drilling — os componentes recebem `darkMode`, dados e callbacks como `onUpdatePatient`, `onNavigateToPrint`). Siga esse padrão; não introduza gerenciador de estado global.
- **Persistência em `localStorage`:** chaves `prescmed_theme`, `prescmed_doctor`, `prescmed_patient`, `prescmed_prescription`, `prescmed_exams`, sincronizadas via `useEffect`. Leituras usam try/catch com fallback para defaults.
- **Tema claro/escuro:** booleano `darkMode` no App; aplica/remove a classe `dark` no `<html>`. Componentes recebem `darkMode` como prop e alternam classes manualmente (o app não depende apenas do seletor `dark:` do Tailwind). Paleta Light: canvas creme (`--bg-app: #F9F6F0`), cards branco-quente (`--surface-card: #FFFDF9`), texto navy. Paleta Dark: obsidian (`--bg-app: #0D0F12`), superfícies grafite (`--surface-card: #1A1D24`). **Chrome de navegação (Header, Sidebar, MobileBottomNav) é sempre deep navy nos dois temas** — usa os tokens `--surface-panel*` e as classes `.panel-navy`/`.panel-navy-inset`; textos sobre o navy são sempre claros (#F1F5F9/#CBD5E1/#94A3B8). Prefira os tokens `var(--*)` de `index.css` a cores hardcoded ao criar novos estilos.
- **Geração de documentos:** `PrintPreview.tsx` renderiza o documento formatado e usa `html2canvas` para captura; `pdfGenerator.ts` monta PDFs programaticamente com jsPDF/autoTable. A folha A4 do documento (`printable-a4-sheet` e todo o conteúdo médico) é **sempre branca com texto escuro, nos dois temas** — nunca aplique o tema da app dentro da folha. Há um helper de conversão de cores (oklch/oklab → rgb) porque o html2canvas não suporta cores modernas do CSS — mantenha isso em mente ao criar estilos que aparecem em documentos exportados.

## Convenções de código

- **Idioma:** UI, dados clínicos e textos de documentos em **português (pt-BR)**; comentários de código misturam português e inglês. Novos textos de UI devem ser em pt-BR.
- **Componentes:** funcionais com hooks, exportação nomeada (`export function X` / `export const X`), um componente principal por arquivo em PascalCase.
- **Estilo:** Tailwind utility classes inline; design tokens como CSS custom properties em `src/index.css` (ex.: `--bg-app`, `--surface-card`). Breakpoint de referência para "mobile": `lg` (1024px) — a sidebar fecha automaticamente abaixo dele.
- **Tipos:** centralizados em `src/types.ts`; adicione novos tipos de domínio lá. `tsconfig` não é estrito e permite `allowJs`, mas escreva código tipado.
- **Path alias:** `@/*` mapeia para a raiz do projeto (pouco usado; os imports existentes são relativos — prefira relativos dentro de `src/`).
- **Formatação numérica:** doses e volumes usam locale pt-BR (`toLocaleString('pt-BR')`, vírgula decimal) nos textos de prescrição.

## Variáveis de ambiente

- `.env.example` documenta `GEMINI_API_KEY` e `APP_URL`, herdadas do template AI Studio — **não são usadas pelo código atual**. `.env*` é ignorado pelo git (exceto `.env.example`).
- `vite.config.ts` respeita `DISABLE_HMR=true` (usado pelo AI Studio para desligar HMR/watch durante edições de agente). Não remova essa lógica.

## Considerações de segurança e privacidade

- O app manipula dados sensíveis de pacientes (nome, CPF/RG, peso, alergias) **somente no navegador** via localStorage — não há envio a servidor. Não introduza telemetria ou chamadas de rede com esses dados sem necessidade explícita.
- Não commite arquivos `.env` nem dados reais de pacientes/médicos.
- Atestados com CID exigem consentimento do paciente (Res. CFM 1.658/2002) — a UI já sinaliza isso; preserve os avisos legais ao alterar `CertificateAndReferral.tsx` ou `pdfGenerator.ts`.

## Deploy

O build (`npm run build`) gera estáticos em `dist/`, servíveis por qualquer host estático. O `metadata.json` indica origem no Google AI Studio (deploy típico via Cloud Run pela plataforma), mas não há configuração de deploy no repositório.
