import React, { useRef, useState, useEffect } from "react";
import {
  X,
  Bold,
  Italic,
  Underline,
  Strikethrough,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Sparkles,
  Download,
  Copy,
  Check,
  MessageSquare,
  Send,
  Cloud,
  FileSpreadsheet,
  PenTool,
  ClipboardList,
  Pin,
  Palette,
  Share2,
  Plus,
  Table as TableIcon,
  FileText,
} from "lucide-react";
import { Note, Comment, NoteColor, EmbeddedTableData } from "../types";
import { getNoteColorClasses } from "../utils/helpers";
import { NoteExportEngine } from "../services/NoteExportEngine";
import { MiniSheetEditor } from "./MiniSheetEditor";

interface DocsEditorModalProps {
  note: Note | null;
  onClose: () => void;
  onSaveNote: (updatedNote: Note) => void;
}

export const DocsEditorModal: React.FC<DocsEditorModalProps> = ({
  note,
  onClose,
  onSaveNote,
}) => {
  if (!note) return null;

  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content);
  const [color, setColor] = useState<NoteColor>(note.color);
  const [pinned, setPinned] = useState(note.pinned);
  const [tags, setTags] = useState<string[]>(note.tags);
  const [newTagInput, setNewTagInput] = useState("");
  const [comments, setComments] = useState<Comment[]>(note.comments || []);
  const [newCommentText, setNewCommentText] = useState("");
  const [showCommentsSidebar, setShowCommentsSidebar] = useState(false);
  const [aiPromptInput, setAiPromptInput] = useState("");
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  // Embedded Tables in Docs
  const [tables, setTables] = useState<EmbeddedTableData[]>(note.tables || []);

  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setTitle(note.title);
    setContent(note.content);
    setColor(note.color);
    setPinned(note.pinned);
    setTags(note.tags);
    setComments(note.comments || []);
    setTables(note.tables || []);
  }, [note]);

  // Sync content back to state on edit
  const handleContentChange = () => {
    if (editorRef.current) {
      setContent(editorRef.current.innerHTML);
    }
  };

  // Execute Rich Text Command
  const execCmd = (cmd: string, val: string | undefined = undefined) => {
    document.execCommand(cmd, false, val);
    handleContentChange();
  };

  // Auto-Save Note
  const triggerSave = () => {
    const updated: Note = {
      ...note,
      title: title || "Nota Sem Título",
      content,
      color,
      pinned,
      tags,
      comments,
      tables,
      updatedAt: new Date().toISOString(),
    };
    onSaveNote(updated);
  };

  const handleAddTag = () => {
    if (newTagInput.trim() && !tags.includes(newTagInput.trim())) {
      const updatedTags = [...tags, newTagInput.trim()];
      setTags(updatedTags);
      setNewTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleAddComment = () => {
    if (!newCommentText.trim()) return;
    const newComment: Comment = {
      id: "comment_" + Date.now(),
      author: "Você (Usuário)",
      text: newCommentText.trim(),
      createdAt: new Date().toISOString(),
    };
    const updated = [...comments, newComment];
    setComments(updated);
    setNewCommentText("");
  };

  const handleInsertTable = () => {
    const newTable: EmbeddedTableData = {
      id: `tbl_${Date.now()}`,
      title: "Nova Tabela Interativa",
      headers: ["Descrição", "Valor (R$)", "Quantidade", "Total"],
      hasHeaderRow: true,
      hasSummaryRow: true,
      rows: [
        [
          { id: `c_0_0_${Date.now()}`, value: "Consultoria Técnica" },
          { id: `c_0_1_${Date.now()}`, value: "250" },
          { id: `c_0_2_${Date.now()}`, value: "4" },
          { id: `c_0_3_${Date.now()}`, value: "=B1*C1" },
        ],
        [
          { id: `c_1_0_${Date.now()}`, value: "Licença de Software" },
          { id: `c_1_1_${Date.now()}`, value: "1200" },
          { id: `c_1_2_${Date.now()}`, value: "1" },
          { id: `c_1_3_${Date.now()}`, value: "=B2*C2" },
        ],
      ],
    };
    setTables((prev) => [...prev, newTable]);
  };

  // Gemini AI Writing Assistant Call
  const handleGeminiAssist = async (actionPrompt: string) => {
    setIsAiLoading(true);
    try {
      const promptText = `Atue como um editor e redator sênior do Google Docs.
Ação solicitada: ${actionPrompt}
Texto/Conteúdo atual do documento:
${content}

Retorne APENAS o conteúdo em HTML formatado pronto para ser inserido no editor.`;

      const res = await fetch("/api/gemini/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: promptText }),
      });
      const data = await res.json();

      if (data.text) {
        let cleanText = data.text.replace(/```html|```/g, "").trim();
        setContent(cleanText);
        if (editorRef.current) {
          editorRef.current.innerHTML = cleanText;
        }
        setShowAIPanel(false);
      }
    } catch (err) {
      console.error("Erro na assistência da IA:", err);
    } finally {
      setIsAiLoading(false);
    }
  };

  // Export functions
  const handleCopyText = () => {
    if (editorRef.current) {
      navigator.clipboard.writeText(editorRef.current.innerText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const currentFullNote: Note = {
    ...note,
    title,
    content,
    color,
    pinned,
    tags,
    comments,
    tables,
  };

  const colorClasses = getNoteColorClasses(color);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-2 backdrop-blur-sm sm:p-6">
      <div
        className={`relative flex h-full max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-3xl border shadow-2xl transition-all ${colorClasses.bg} ${colorClasses.border}`}
      >
        {/* Modal Top Header */}
        <div className="flex items-center justify-between border-b border-zinc-200/80 px-6 py-3.5 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="rounded-lg bg-amber-500/10 p-1.5 text-amber-600 dark:text-amber-400">
              {note.type === "form" && <ClipboardList className="h-5 w-5" />}
              {note.type === "sheet" && <FileSpreadsheet className="h-5 w-5" />}
              {note.type === "canvas" && <PenTool className="h-5 w-5" />}
              {note.type === "doc" && <Heading1 className="h-5 w-5" />}
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Google Docs Canvas Editor
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Pin Toggle */}
            <button
              onClick={() => {
                setPinned(!pinned);
              }}
              className={`rounded-xl p-2 transition-colors ${
                pinned
                  ? "bg-amber-100 text-amber-700 dark:bg-amber-900/60 dark:text-amber-300"
                  : "text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              }`}
              title="Fixar/Desafixar no topo"
            >
              <Pin className={`h-4 w-4 ${pinned ? "fill-amber-600" : ""}`} />
            </button>

            {/* AI Assistant Button */}
            <button
              onClick={() => setShowAIPanel(!showAIPanel)}
              className="flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 shadow-2xs hover:border-indigo-300 dark:border-indigo-900 dark:from-indigo-950/40 dark:to-purple-950/40 dark:text-indigo-300"
            >
              <Sparkles className="h-3.5 w-3.5 text-indigo-500 animate-pulse" />
              <span>✨ Gemini AI</span>
            </button>

            {/* Comments Sidebar Toggle */}
            <button
              onClick={() => setShowCommentsSidebar(!showCommentsSidebar)}
              className={`relative flex items-center gap-1.5 rounded-xl border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-800 ${
                showCommentsSidebar ? "bg-zinc-200 dark:bg-zinc-800" : "bg-white dark:bg-zinc-900"
              }`}
            >
              <MessageSquare className="h-4 w-4 text-amber-500" />
              <span>Comentários ({comments.length})</span>
            </button>

            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="flex items-center gap-1.5 rounded-xl border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                <Download className="h-4 w-4 text-blue-500" />
                <span>Exportar</span>
              </button>

              {showExportMenu && (
                <div className="absolute right-0 top-10 z-50 w-48 rounded-2xl border border-zinc-200 bg-white p-2 shadow-xl dark:border-zinc-800 dark:bg-zinc-900">
                  <button
                    onClick={() => {
                      NoteExportEngine.exportToMarkdown(currentFullNote);
                      setShowExportMenu(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs text-zinc-800 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
                  >
                    <FileText className="h-3.5 w-3.5 text-blue-500" />
                    <span>Markdown (.md)</span>
                  </button>
                  <button
                    onClick={() => {
                      NoteExportEngine.exportToHTML(currentFullNote);
                      setShowExportMenu(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs text-zinc-800 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
                  >
                    <FileText className="h-3.5 w-3.5 text-amber-500" />
                    <span>Página Web (.html)</span>
                  </button>
                  <button
                    onClick={() => {
                      NoteExportEngine.exportToJSON(currentFullNote);
                      setShowExportMenu(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs text-zinc-800 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
                  >
                    <FileText className="h-3.5 w-3.5 text-purple-500" />
                    <span>Backup JSON (.json)</span>
                  </button>
                  {tables.length > 0 && (
                    <button
                      onClick={() => {
                        NoteExportEngine.exportTableToCSV(tables[0]);
                        setShowExportMenu(false);
                      }}
                      className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs text-zinc-800 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
                    >
                      <TableIcon className="h-3.5 w-3.5 text-emerald-500" />
                      <span>Tabela em CSV (.csv)</span>
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Copy */}
            <button
              onClick={handleCopyText}
              className="flex items-center gap-1.5 rounded-xl border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
              title="Copiar texto formatado"
            >
              {copied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
              <span>{copied ? "Copiado!" : "Copiar"}</span>
            </button>

            {/* Close Button */}
            <button
              onClick={() => {
                triggerSave();
                onClose();
              }}
              className="rounded-xl p-2 text-zinc-400 hover:bg-zinc-200 hover:text-zinc-800 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Gemini AI Floating Toolbar Panel */}
        {showAIPanel && (
          <div className="border-b border-indigo-200 bg-indigo-50/90 p-3 dark:border-indigo-900/50 dark:bg-indigo-950/60">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="font-bold text-indigo-900 dark:text-indigo-200">✨ Comandos Gemini:</span>
              <button
                disabled={isAiLoading}
                onClick={() => handleGeminiAssist("Resuma o documento em tópicos executivos.")}
                className="rounded-lg bg-white px-2.5 py-1 font-medium text-indigo-700 shadow-2xs hover:bg-indigo-100 dark:bg-indigo-900 dark:text-indigo-200"
              >
                Resumir Documento
              </button>
              <button
                disabled={isAiLoading}
                onClick={() => handleGeminiAssist("Melhore a gramática, tom profissional e clareza do texto.")}
                className="rounded-lg bg-white px-2.5 py-1 font-medium text-indigo-700 shadow-2xs hover:bg-indigo-100 dark:bg-indigo-900 dark:text-indigo-200"
              >
                Melhorar Tom & Clareza
              </button>
              <button
                disabled={isAiLoading}
                onClick={() => handleGeminiAssist("Expanda este conteúdo com detalhes e exemplos práticos.")}
                className="rounded-lg bg-white px-2.5 py-1 font-medium text-indigo-700 shadow-2xs hover:bg-indigo-100 dark:bg-indigo-900 dark:text-indigo-200"
              >
                Expandir Tópicos
              </button>
              <button
                disabled={isAiLoading}
                onClick={() => handleGeminiAssist("Traduza todo o texto para o Inglês.")}
                className="rounded-lg bg-white px-2.5 py-1 font-medium text-indigo-700 shadow-2xs hover:bg-indigo-100 dark:bg-indigo-900 dark:text-indigo-200"
              >
                Traduzir para Inglês
              </button>
            </div>

            <div className="mt-2 flex items-center gap-2">
              <input
                type="text"
                value={aiPromptInput}
                onChange={(e) => setAiPromptInput(e.target.value)}
                placeholder="Ex: 'Adicione uma tabela de cronograma...' ou 'Crie uma introdução executiva...'"
                className="w-full rounded-xl border border-indigo-200 bg-white px-3 py-1.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none dark:border-indigo-800 dark:bg-zinc-900 dark:text-zinc-100"
              />
              <button
                disabled={isAiLoading || !aiPromptInput.trim()}
                onClick={() => {
                  handleGeminiAssist(aiPromptInput);
                  setAiPromptInput("");
                }}
                className="flex items-center gap-1 rounded-xl bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-2xs hover:bg-indigo-700 disabled:opacity-50"
              >
                {isAiLoading ? "Processando..." : "Executar"}
              </button>
            </div>
          </div>
        )}

        {/* Google Docs Rich Toolbar */}
        <div className="flex flex-wrap items-center gap-1 border-b border-zinc-200/80 bg-white/70 px-6 py-2 dark:border-zinc-800 dark:bg-zinc-900/70">
          <button
            onClick={() => execCmd("formatBlock", "<h1>")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Título 1 (H1)"
          >
            <Heading1 className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("formatBlock", "<h2>")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Título 2 (H2)"
          >
            <Heading2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("formatBlock", "<h3>")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Título 3 (H3)"
          >
            <Heading3 className="h-4 w-4" />
          </button>

          <div className="h-4 w-px bg-zinc-300 mx-1 dark:bg-zinc-700" />

          <button
            onClick={() => execCmd("bold")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 font-bold"
            title="Negrito (Ctrl+B)"
          >
            <Bold className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("italic")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 italic"
            title="Itálico (Ctrl+I)"
          >
            <Italic className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("underline")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 underline"
            title="Sublinhado (Ctrl+U)"
          >
            <Underline className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("strikeThrough")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 line-through"
            title="Tachado"
          >
            <Strikethrough className="h-4 w-4" />
          </button>

          <div className="h-4 w-px bg-zinc-300 mx-1 dark:bg-zinc-700" />

          <button
            onClick={() => execCmd("insertUnorderedList")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Lista com Marcadores"
          >
            <List className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("insertOrderedList")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Lista Numerada"
          >
            <ListOrdered className="h-4 w-4" />
          </button>

          <div className="h-4 w-px bg-zinc-300 mx-1 dark:bg-zinc-700" />

          <button
            onClick={() => execCmd("justifyLeft")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Alinhar à Esquerda"
          >
            <AlignLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("justifyCenter")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Centralizar"
          >
            <AlignCenter className="h-4 w-4" />
          </button>
          <button
            onClick={() => execCmd("justifyRight")}
            className="rounded-lg p-1.5 hover:bg-zinc-200/80 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Alinhar à Direita"
          >
            <AlignRight className="h-4 w-4" />
          </button>

          <div className="h-4 w-px bg-zinc-300 mx-1 dark:bg-zinc-700" />

          {/* Insert Table Button */}
          <button
            onClick={handleInsertTable}
            className="flex items-center gap-1 rounded-lg bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/60 dark:text-emerald-300"
            title="Inserir Tabela Interativa (Sheets inside Docs)"
          >
            <TableIcon className="h-4 w-4" />
            <span>+ Tabela (Sheets)</span>
          </button>
        </div>

        {/* Main Split Area: Editor Canvas + Comments Sidebar */}
        <div className="flex flex-1 overflow-hidden">
          {/* Docs Page / Paper Canvas Container */}
          <div className="flex-1 overflow-y-auto p-6 sm:p-10">
            <div className="mx-auto max-w-3xl min-h-[500px] rounded-2xl border border-zinc-200 bg-white p-8 sm:p-12 shadow-md dark:border-zinc-800 dark:bg-zinc-900">
              {/* Document Title Input */}
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Título do Documento..."
                className="w-full border-b border-zinc-200 bg-transparent pb-3 text-2xl font-black text-zinc-900 outline-none placeholder:text-zinc-300 dark:border-zinc-800 dark:text-zinc-100 dark:placeholder:text-zinc-700"
              />

              {/* Tags Editor */}
              <div className="my-3 flex flex-wrap items-center gap-1.5">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="flex items-center gap-1 rounded-md bg-zinc-100 px-2 py-0.5 text-[11px] font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                  >
                    #{tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-1 text-zinc-400 hover:text-red-500"
                    >
                      ×
                    </button>
                  </span>
                ))}
                <div className="flex items-center gap-1">
                  <input
                    type="text"
                    value={newTagInput}
                    onChange={(e) => setNewTagInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAddTag()}
                    placeholder="+ Adicionar tag"
                    className="w-24 border-b border-zinc-200 bg-transparent text-[11px] text-zinc-700 outline-none dark:border-zinc-800 dark:text-zinc-300"
                  />
                </div>
              </div>

              {/* Editable Content Area */}
              <div
                ref={editorRef}
                contentEditable
                onInput={handleContentChange}
                dangerouslySetInnerHTML={{ __html: content }}
                className="prose prose-zinc dark:prose-invert max-w-none mt-6 min-h-[250px] outline-none text-zinc-800 dark:text-zinc-200 leading-relaxed text-sm"
              />

              {/* Embedded Tables (Sheets inside Docs) */}
              {tables.length > 0 && (
                <div className="mt-8 space-y-6 border-t border-zinc-200 pt-6 dark:border-zinc-800">
                  <h4 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                    <TableIcon className="h-4 w-4" />
                    <span>Tabelas Interativas Embutidas ({tables.length})</span>
                  </h4>

                  {tables.map((table, tIdx) => (
                    <div key={table.id} className="relative rounded-2xl border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-950/60">
                      <div className="flex items-center justify-between mb-3">
                        <input
                          type="text"
                          value={table.title}
                          onChange={(e) => {
                            const updated = tables.map((tbl, i) => (i === tIdx ? { ...tbl, title: e.target.value } : tbl));
                            setTables(updated);
                          }}
                          className="font-bold text-sm text-zinc-900 dark:text-zinc-100 bg-transparent outline-none border-b border-transparent hover:border-zinc-300"
                        />
                        <button
                          onClick={() => setTables(tables.filter((_, i) => i !== tIdx))}
                          className="text-xs text-red-500 hover:text-red-700"
                        >
                          Remover Tabela
                        </button>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left border-collapse border border-zinc-200 dark:border-zinc-800">
                          <thead>
                            <tr className="bg-zinc-200/60 dark:bg-zinc-800">
                              {table.headers.map((h, cIdx) => (
                                <th key={cIdx} className="p-2 border border-zinc-200 dark:border-zinc-800 font-bold text-zinc-700 dark:text-zinc-300">
                                  {h}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {table.rows.map((row, rIdx) => (
                              <tr key={rIdx} className="hover:bg-white dark:hover:bg-zinc-900">
                                {row.map((cell, cIdx) => (
                                  <td key={cell.id} className="p-0 border border-zinc-200 dark:border-zinc-800">
                                    <input
                                      type="text"
                                      value={cell.value}
                                      onChange={(e) => {
                                        const newVal = e.target.value;
                                        const updatedRows = table.rows.map((r, rI) => {
                                          if (rI !== rIdx) return r;
                                          return r.map((c, cI) => (cI === cIdx ? { ...c, value: newVal, computedValue: newVal } : c));
                                        });
                                        const updatedTbls = tables.map((tbl, i) => (i === tIdx ? { ...tbl, rows: updatedRows } : tbl));
                                        setTables(updatedTbls);
                                      }}
                                      className="w-full h-full px-2 py-1.5 bg-transparent outline-none font-mono text-xs"
                                    />
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar: Comments & Collaboration */}
          {showCommentsSidebar && (
            <div className="w-80 flex-shrink-0 border-l border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-950/80 flex flex-col justify-between">

              <div>
                <h4 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
                  <MessageSquare className="h-4 w-4 text-amber-500" />
                  <span>Comentários ({comments.length})</span>
                </h4>

                <div className="mt-4 space-y-3 overflow-y-auto max-h-[50vh]">
                  {comments.length === 0 ? (
                    <p className="text-xs text-zinc-400 italic">Nenhum comentário cadastrado ainda.</p>
                  ) : (
                    comments.map((c) => (
                      <div
                        key={c.id}
                        className="rounded-xl border border-zinc-200 bg-white p-3 text-xs shadow-2xs dark:border-zinc-800 dark:bg-zinc-900"
                      >
                        <div className="flex items-center justify-between font-semibold text-zinc-800 dark:text-zinc-200">
                          <span>{c.author}</span>
                          <span className="text-[10px] text-zinc-400">
                            {new Date(c.createdAt).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
                          </span>
                        </div>
                        <p className="mt-1 text-zinc-600 dark:text-zinc-300">{c.text}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* New Comment Input */}
              <div className="mt-4 border-t border-zinc-200 pt-3 dark:border-zinc-800">
                <div className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={newCommentText}
                    onChange={(e) => setNewCommentText(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAddComment()}
                    placeholder="Adicionar um comentário..."
                    className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-900 outline-none dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
                  />
                  <button
                    onClick={handleAddComment}
                    className="rounded-xl bg-amber-600 p-2 text-white hover:bg-amber-700"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-zinc-200/80 bg-white/70 px-6 py-3.5 dark:border-zinc-800 dark:bg-zinc-900/70">
          <div className="text-xs text-zinc-400">
            Salvo automaticamente localmente e sincronizável com o Google Drive
          </div>

          <button
            onClick={() => {
              triggerSave();
              onClose();
            }}
            className="rounded-xl bg-amber-600 px-5 py-2 text-xs font-semibold text-white shadow-md shadow-amber-600/20 hover:bg-amber-700"
          >
            Concluir & Salvar
          </button>
        </div>
      </div>
    </div>
  );
};
