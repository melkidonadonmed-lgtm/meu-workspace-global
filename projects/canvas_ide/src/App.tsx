import { useRef, useState } from 'react'
import {
  Bot,
  CheckCircle2,
  Code2,
  FilePlus,
  FolderTree,
  Gauge,
  Layers,
  MessageSquare,
  MonitorPlay,
  NotebookPen,
  Play,
  RefreshCw,
  Save,
  Send,
  ShieldCheck,
  Sparkles,
  Terminal,
  Trash2,
  Users,
} from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: Parameters<typeof clsx>) {
  return twMerge(clsx(inputs))
}

type SidebarView = 'files' | 'agents' | 'metrics'
type MainTab = 'editor' | 'notebook' | 'preview' | 'tests'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// Sistema de Arquivos Virtual Integrado
const initialFiles: Record<string, string> = {
  'app/main.py': `# Google ADK Root Orchestrator
from app.subagents.sql_specialist import sql_specialist_agent
from app.subagents.workspace_specialist import workspace_specialist_agent
from app.subagents.security_guard import security_guard_agent

def execute_pipeline(query: str):
    print(f"Roteando tarefa analítica: {query}")
`,
  'queries/vendas_analytics.sql': `-- Consulta GoogleSQL com Otimização de Custo
SELECT
    DATE(data_venda) AS dia,
    categoria,
    SUM(valor_total) AS faturamento,
    COUNT(DISTINCT cliente_id) AS clientes_unicos
FROM \`projeto.analytics.vendas_2026\`
WHERE data_venda >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY 1, 2
ORDER BY dia DESC
LIMIT 100;
`,
  'reports/executivo_docs.md': `# Relatório Executivo Q3 - Arquiteto v2.0
## Sumário de Operações Multi-Agente
- **SQL Specialist**: 14 consultas executadas com auditoria.
- **Security Guard**: 0 vazamentos de PII detectados.
- **Tokens Utilizados**: 1,842 / 20,000.
`,
  'index.html': `<!DOCTYPE html>
<html>
<head><title>Preview Demo</title></head>
<body style="font-family:sans-serif;padding:30px;background:#0f172a;color:#f8fafc">
  <h1>🚀 Arquiteto v2.0 Live Preview</h1>
  <p>Este arquivo pode ser editado e renderizado instantaneamente!</p>
</body>
</html>`,
}

const activityButtons: { view: SidebarView; title: string; icon: typeof FolderTree }[] = [
  { view: 'files', title: 'Arquivos do Workspace', icon: FolderTree },
  { view: 'agents', title: 'Subagentes Especialistas', icon: Bot },
  { view: 'metrics', title: 'Telemetria & Tokens', icon: Gauge },
]

const mainTabs: { tab: MainTab; label: string; icon: typeof Code2 }[] = [
  { tab: 'editor', label: 'app/main.py', icon: Code2 },
  { tab: 'notebook', label: 'Notebook', icon: NotebookPen },
  { tab: 'preview', label: 'Preview HTML', icon: MonitorPlay },
  { tab: 'tests', label: 'Testes', icon: Play },
]

function buildAssistantResponse(text: string): string {
  const lower = text.toLowerCase()
  if (lower.includes('sql') || lower.includes('query')) {
    return '🔵 SQL Specialist: Analisei sua solicitação. Gere uma consulta analítica no arquivo `queries/vendas_analytics.sql` com agregação por categoria e LIMIT 100 aplicado com sucesso.'
  }
  if (lower.includes('doc') || lower.includes('relatório')) {
    return '🟢 Workspace Specialist: Criei o esboço do relatório executivo em `reports/executivo_docs.md` com resumo das operações e métricas consolidadas.'
  }
  if (lower.includes('seguran') || lower.includes('pii')) {
    return '🟡 Security Guard: Auditoria Zero-Trust concluída. Nenhum vazamento de credencial ou PII encontrado no workspace. Todos os comandos destrutivos bloqueados.'
  }
  return `🤖 Arquiteto v2.0: Entendido! A proposta para sua solicitação "${text}" foi processada e as alterações foram sincronizadas no workspace virtual.`
}

export default function App() {
  const [sidebar, setSidebar] = useState<SidebarView>('files')
  const [tab, setTab] = useState<MainTab>('editor')
  const [files, setFiles] = useState<Record<string, string>>(initialFiles)
  const [currentFile, setCurrentFile] = useState('app/main.py')
  const [editorValue, setEditorValue] = useState(initialFiles['app/main.py'])
  const [chatInput, setChatInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Olá! Seu workspace e subagentes estão prontos. Como posso ajudar com consultas BigQuery, manipulação do Google Workspace ou refatoração de código?',
    },
  ])
  const [notebookOutput, setNotebookOutput] = useState(
    '[Output aparecerá aqui ao clicar em Executar]',
  )
  const chatEndRef = useRef<HTMLDivElement>(null)

  function openFile(path: string) {
    setFiles((prev) => ({ ...prev, [currentFile]: editorValue }))
    setCurrentFile(path)
    setEditorValue(files[path] ?? '')
    setTab('editor')
  }

  function saveCurrentFile() {
    setFiles((prev) => ({ ...prev, [currentFile]: editorValue }))
    window.alert(`✅ Arquivo '${currentFile}' salvo com sucesso!`)
  }

  function createNewFile() {
    const name = window.prompt('Digite o caminho do novo arquivo (ex: src/novo.py):')
    if (name && name.trim()) {
      const path = name.trim()
      setFiles((prev) => ({ ...prev, [currentFile]: editorValue, [path]: `# Arquivo ${path}\n` }))
      setCurrentFile(path)
      setEditorValue(`# Arquivo ${path}\n`)
      setTab('editor')
    }
  }

  function appendMessage(msg: ChatMessage) {
    setMessages((prev) => [...prev, msg])
    setTimeout(() => chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
  }

  function sendMessage(text: string) {
    const trimmed = text.trim()
    if (!trimmed) return
    appendMessage({ role: 'user', content: trimmed })
    setChatInput('')
    setTimeout(() => {
      appendMessage({ role: 'assistant', content: buildAssistantResponse(trimmed) })
    }, 600)
  }

  function handleSend(e: React.FormEvent) {
    e.preventDefault()
    sendMessage(chatInput)
  }

  function clearChat() {
    setMessages([
      { role: 'assistant', content: 'Conversa reiniciada. Como posso ajudar com seu código hoje?' },
    ])
  }

  function runNotebookCell() {
    setNotebookOutput('Executando célula efêmera...')
    setTimeout(() => {
      setNotebookOutput(
        '✅ Execução concluída em 38ms (Sandbox Efêmero):\n\n' +
          '[STDOUT]:\n' +
          '✅ Efêmero iniciado com sucesso.\n' +
          'Cálculo: raiz quadrada de 2026 = 45.0111\n\n' +
          '[STATUS]: Exit code 0',
      )
    }, 300)
  }

  function simulateTests() {
    window.alert('✅ Executando pytest tests/unit...\n82 testes passaram com 100% de sucesso!')
  }

  const previewDoc =
    tab === 'preview'
      ? files['index.html'] ?? '<h2>Preview</h2>'
      : undefined

  return (
    <div className="bg-obsidian-950 text-slate-100 font-sans h-screen w-screen flex flex-col overflow-hidden select-none">
      {/* 1. TOP HEADER BAR */}
      <header className="h-12 shrink-0 border-b border-obsidian-800 bg-obsidian-900/90 px-4 flex items-center justify-between backdrop-blur z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 shadow-md shadow-amber-500/20 text-obsidian-950 font-bold">
              <Sparkles className="h-4 w-4" />
            </span>
            <span className="font-bold text-sm tracking-tight text-white">
              Arquiteto <span className="text-amber-400 font-normal">v2.0 Canvas</span>
            </span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border border-amber-500/30 bg-amber-950/40 text-amber-300 ml-1">
              React + Vite
            </span>
          </div>

          <div className="hidden h-4 w-px bg-obsidian-800 md:block" />

          {/* Seletor de Modelo */}
          <div className="hidden items-center gap-1.5 md:flex">
            <Bot className="h-3.5 w-3.5 text-amber-400" />
            <select
              id="model-select"
              className="rounded-md border border-obsidian-700 bg-obsidian-950 px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              defaultValue="gemini-3.7-flash"
            >
              <option value="gemini-3.7-flash">Gemini 3.7 Flash (Padrão Interactions)</option>
              <option value="gemini-3.5-flash-lite">Gemini 3.5 Flash-Lite (Rápido)</option>
              <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro (Raciocínio)</option>
              <option value="claude-3-7-sonnet">Claude 3.7 Sonnet (Anthropic)</option>
            </select>
          </div>

          {/* Badge de Conexão */}
          <div className="hidden items-center gap-1.5 rounded-full border border-emerald-800/60 bg-emerald-950/40 px-2.5 py-0.5 text-[11px] text-emerald-300 lg:flex">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Workspace & BigQuery Guardrails: Ativo</span>
          </div>
        </div>

        {/* Status & Ações de Topo */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 rounded-full border border-obsidian-700 bg-obsidian-950 px-2.5 py-1 text-xs font-mono text-slate-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>4 ms (Local)</span>
          </div>

          <button
            onClick={() => setSidebar('agents')}
            className="flex items-center gap-1.5 rounded-md border border-amber-500/30 bg-obsidian-850 px-2.5 py-1 text-xs font-medium text-amber-200 hover:bg-obsidian-700 transition"
          >
            <Users className="h-3.5 w-3.5 text-amber-400" />
            <span>Subagentes</span>
          </button>
        </div>
      </header>

      {/* 2. MAIN LAYOUT */}
      <div className="flex flex-1 min-h-0 relative">
        {/* Activity Bar Esquerda */}
        <nav className="w-12 shrink-0 border-r border-obsidian-800 bg-obsidian-950 flex flex-col items-center py-3 gap-3 z-10">
          {activityButtons.map(({ view, title, icon: Icon }) => (
            <button
              key={view}
              onClick={() => setSidebar(view)}
              title={title}
              className={cn(
                'h-9 w-9 flex items-center justify-center rounded-lg transition',
                sidebar === view
                  ? 'text-amber-400 bg-obsidian-850 border border-amber-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-obsidian-900',
              )}
            >
              <Icon className="h-4 w-4" />
            </button>
          ))}
        </nav>

        {/* Sidebar Retrátil */}
        <aside className="w-64 shrink-0 border-r border-obsidian-800 bg-obsidian-900/60 flex flex-col text-xs z-10 backdrop-blur">
          {/* Seção de Arquivos */}
          {sidebar === 'files' && (
            <div className="flex-1 flex flex-col min-h-0 p-3">
              <div className="flex items-center justify-between border-b border-obsidian-800 pb-2 mb-2">
                <span className="font-semibold uppercase tracking-wider text-[11px] text-amber-300 flex items-center gap-1.5">
                  <Layers className="h-3.5 w-3.5" />
                  <span>Explorador</span>
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={createNewFile}
                    className="p-1 rounded text-slate-400 hover:text-amber-300 hover:bg-obsidian-800"
                    title="Novo Arquivo"
                  >
                    <FilePlus className="h-3.5 w-3.5" />
                  </button>
                  <button
                    className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-obsidian-800"
                    title="Atualizar"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              <ul className="flex-1 overflow-y-auto space-y-0.5 pr-1">
                {Object.keys(files)
                  .sort()
                  .map((path) => (
                    <li key={path}>
                      <button
                        onClick={() => openFile(path)}
                        className={cn(
                          'w-full text-left px-2 py-1.5 rounded-lg flex items-center justify-between text-xs transition',
                          currentFile === path
                            ? 'bg-amber-950/50 border border-amber-500/30 text-amber-200 font-semibold'
                            : 'text-slate-300 hover:bg-obsidian-800 hover:text-white',
                        )}
                      >
                        <span className="truncate font-mono text-[11px]">{path}</span>
                      </button>
                    </li>
                  ))}
              </ul>
            </div>
          )}

          {/* Seção de Subagentes */}
          {sidebar === 'agents' && (
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              <h3 className="font-semibold text-xs text-amber-300 border-b border-obsidian-800 pb-2">
                Subagentes do Ecossistema
              </h3>

              <div className="p-2.5 rounded-lg border border-blue-900/60 bg-blue-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-blue-300 text-xs">🔵 SQL Specialist</span>
                  <span className="text-[9px] bg-blue-900/50 px-1 py-0.5 rounded text-blue-200">
                    BigQuery
                  </span>
                </div>
                <p className="text-[11px] text-slate-300">
                  Gera consultas GoogleSQL otimizadas com LIMIT e auditoria.
                </p>
              </div>

              <div className="p-2.5 rounded-lg border border-emerald-900/60 bg-emerald-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-emerald-300 text-xs">
                    🟢 Workspace Specialist
                  </span>
                  <span className="text-[9px] bg-emerald-900/50 px-1 py-0.5 rounded text-emerald-200">
                    Drive & Docs
                  </span>
                </div>
                <p className="text-[11px] text-slate-300">
                  Cria relatórios executivos no Docs e planilhas no Sheets.
                </p>
              </div>

              <div className="p-2.5 rounded-lg border border-amber-900/60 bg-amber-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-amber-300 text-xs">🟡 Security Guard</span>
                  <span className="text-[9px] bg-amber-900/50 px-1 py-0.5 rounded text-amber-200">
                    Guardrails
                  </span>
                </div>
                <p className="text-[11px] text-slate-300">
                  Detecção de PII, bloqueio de comandos destrutivos e Dry Run.
                </p>
              </div>

              <div className="p-2.5 rounded-lg border border-cyan-900/60 bg-cyan-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-cyan-300 text-xs">🌐 Web Researcher</span>
                  <span className="text-[9px] bg-cyan-900/50 px-1 py-0.5 rounded text-cyan-200">
                    Live Search
                  </span>
                </div>
                <p className="text-[11px] text-slate-300">
                  Pesquisa em tempo real com extração limpa e cache LRU.
                </p>
              </div>
            </div>
          )}

          {/* Seção de Métricas */}
          {sidebar === 'metrics' && (
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              <h3 className="font-semibold text-xs text-amber-300 border-b border-obsidian-800 pb-2">
                Telemetria & Budget
              </h3>
              <div className="p-3 rounded-lg bg-obsidian-950 border border-obsidian-800 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Tokens Consumidos:</span>
                  <span className="font-mono text-amber-400 font-bold">1,842</span>
                </div>
                <div className="w-full bg-obsidian-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-gradient-to-r from-amber-500 to-indigo-500 h-full w-[28%]" />
                </div>
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>Limite: 20,000</span>
                  <span>Saldo: 18,158</span>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Centro: Área do Editor / Notebook / Preview */}
        <main className="flex-1 flex flex-col min-w-0 bg-obsidian-950">
          {/* Barra Superior de Abas */}
          <div className="h-10 shrink-0 border-b border-obsidian-800 bg-obsidian-900/70 px-3 flex items-center justify-between">
            <div className="flex items-center gap-1 overflow-x-auto">
              {mainTabs.map(({ tab: t, label, icon: Icon }) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={cn(
                    'flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium',
                    tab === t
                      ? 'bg-obsidian-800 text-amber-300 border border-amber-500/30 shadow-sm'
                      : 'text-slate-400 hover:bg-obsidian-800 hover:text-slate-200',
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{t === 'editor' ? currentFile : label}</span>
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={saveCurrentFile}
                className="flex items-center gap-1 bg-amber-600 hover:bg-amber-500 text-obsidian-950 font-bold px-3 py-1 rounded text-xs transition"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Salvar</span>
              </button>
            </div>
          </div>

          {/* Conteúdo das Abas */}
          <div className="flex-1 min-h-0 relative">
            {/* 1. Editor de Código */}
            {tab === 'editor' && (
              <div className="h-full w-full">
                <textarea
                  value={editorValue}
                  onChange={(e) => setEditorValue(e.target.value)}
                  spellCheck={false}
                  className="h-full w-full resize-none bg-obsidian-950 p-4 font-mono text-[13px] leading-relaxed text-slate-100 focus:outline-none"
                />
              </div>
            )}

            {/* 2. Notebook Panel */}
            {tab === 'notebook' && (
              <div className="h-full w-full overflow-y-auto p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-obsidian-800 pb-3">
                  <div>
                    <h2 className="text-sm font-bold text-amber-300 flex items-center gap-2">
                      <NotebookPen className="h-4 w-4" />
                      <span>Células Interativas de Execução</span>
                    </h2>
                    <p className="text-xs text-slate-400">
                      Execute trechos de código com medição de latência em milissegundos.
                    </p>
                  </div>
                  <button
                    onClick={runNotebookCell}
                    className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded text-xs font-semibold text-white"
                  >
                    <Play className="h-3.5 w-3.5" />
                    <span>Executar Célula</span>
                  </button>
                </div>

                <div className="rounded-xl border border-obsidian-700 bg-obsidian-900 p-4 space-y-3">
                  <textarea
                    rows={4}
                    defaultValue={
                      '# Demonstração de Execução\nimport math\nprint("✅ Efêmero iniciado com sucesso.")\nprint(f"Cálculo: raiz quadrada de 2026 = {math.sqrt(2026):.4f}")\n'
                    }
                    className="w-full bg-obsidian-950 font-mono text-xs p-3 rounded-lg border border-obsidian-800 text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                  <div className="rounded-lg bg-obsidian-950 border border-obsidian-800 p-3 font-mono text-xs text-emerald-400 whitespace-pre-wrap">
                    {notebookOutput}
                  </div>
                </div>
              </div>
            )}

            {/* 3. Preview HTML */}
            {tab === 'preview' && (
              <div className="h-full w-full flex flex-col p-4">
                <iframe
                  title="Preview HTML"
                  className="flex-1 w-full rounded-xl border border-obsidian-800 bg-white"
                  srcDoc={previewDoc}
                />
              </div>
            )}

            {/* 4. Testes Automatizados */}
            {tab === 'tests' && (
              <div className="h-full w-full overflow-y-auto p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-obsidian-800 pb-3">
                  <h2 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                    <Terminal className="h-4 w-4" />
                    <span>Suíte de Testes Automatizados (pytest)</span>
                  </h2>
                  <button
                    onClick={simulateTests}
                    className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded text-xs font-semibold text-white"
                  >
                    <Play className="h-3.5 w-3.5" />
                    <span>Rodar Todos os Testes</span>
                  </button>
                </div>

                <div className="rounded-xl border border-emerald-800/60 bg-emerald-950/20 p-4 font-mono text-xs text-slate-200">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold mb-2">
                    <CheckCircle2 className="h-4 w-4" />
                    <span>82 passed in 12.49s (100% de sucesso)</span>
                  </div>
                  <pre className="text-slate-400">{`tests/unit/test_agent_canvas_safety.py ........ PASSED
tests/unit/test_antigravity_agent.py ... PASSED
tests/unit/test_api_orchestration_plug.py ...... PASSED
tests/unit/test_subagents_and_tools.py .... PASSED
tests/unit/test_workspace_tools.py ... PASSED`}</pre>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Painel Direito: Chat & Subagentes */}
        <aside className="w-80 shrink-0 border-l border-obsidian-800 bg-obsidian-900/80 flex flex-col z-10 backdrop-blur">
          {/* Header do Chat */}
          <div className="h-10 shrink-0 border-b border-obsidian-800 px-3 flex items-center justify-between text-xs font-semibold text-slate-200">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-amber-400" />
              <span>Chat & Orquestrador</span>
            </div>
            <button
              onClick={clearChat}
              className="text-slate-400 hover:text-rose-400 p-1"
              title="Limpar Conversa"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Histórico de Mensagens */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 text-xs">
            {messages.map((msg, i) =>
              msg.role === 'assistant' ? (
                <div
                  key={i}
                  className="bg-obsidian-950 border border-obsidian-800 p-3 rounded-xl rounded-bl-sm text-slate-200 mr-6 leading-relaxed"
                >
                  <p className="font-semibold text-amber-300 mb-1 flex items-center gap-1.5">
                    <Bot className="h-3.5 w-3.5" />
                    <span>Arquiteto v2.0</span>
                  </p>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              ) : (
                <div
                  key={i}
                  className="bg-amber-600 text-obsidian-950 font-medium p-3 rounded-xl rounded-br-sm ml-6"
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              ),
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Subagent Triggers */}
          <div className="p-2 border-t border-obsidian-800/80 bg-obsidian-950/60 grid grid-cols-2 gap-1.5">
            <button
              onClick={() =>
                sendMessage('Crie uma consulta analítica no BigQuery para o dataset de vendas')
              }
              className="p-1.5 rounded border border-blue-900/60 bg-blue-950/30 text-blue-300 text-[10px] hover:bg-blue-900/40 text-left truncate"
            >
              🔵 SQL Query
            </button>
            <button
              onClick={() =>
                sendMessage('Gere um relatório executivo no Google Docs com os dados do mês')
              }
              className="p-1.5 rounded border border-emerald-900/60 bg-emerald-950/30 text-emerald-300 text-[10px] hover:bg-emerald-900/40 text-left truncate"
            >
              🟢 Google Docs
            </button>
            <button
              onClick={() =>
                sendMessage('Audite a segurança deste código contra injeção SQL e PII')
              }
              className="p-1.5 rounded border border-amber-900/60 bg-amber-950/30 text-amber-300 text-[10px] hover:bg-amber-900/40 text-left truncate"
            >
              🟡 Auditoria PII
            </button>
            <button
              onClick={() => sendMessage('Pesquise na web novidades sobre o Google ADK 2026')}
              className="p-1.5 rounded border border-cyan-900/60 bg-cyan-950/30 text-cyan-300 text-[10px] hover:bg-cyan-900/40 text-left truncate"
            >
              🌐 Web Search
            </button>
          </div>

          {/* Input de Envio */}
          <form onSubmit={handleSend} className="p-2.5 border-t border-obsidian-800 bg-obsidian-950">
            <div className="flex items-center gap-1.5">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Peça uma consulta, código ou relatório..."
                className="flex-1 bg-obsidian-900 border border-obsidian-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
              />
              <button
                type="submit"
                className="bg-gradient-to-br from-amber-500 to-amber-600 text-obsidian-950 font-bold p-2 rounded-lg hover:from-amber-400 hover:to-amber-500 transition"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
          </form>
        </aside>
      </div>
    </div>
  )
}
