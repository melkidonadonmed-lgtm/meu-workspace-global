import React, { useState, useEffect } from "react";
import {
  Search,
  FileText,
  ClipboardList,
  FileSpreadsheet,
  PenTool,
  Cloud,
  Sparkles,
  Command,
  X,
  ArrowRight,
} from "lucide-react";
import { Note } from "../types";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  notes: Note[];
  onOpenNote: (note: Note) => void;
  onNewNote: (type: "doc" | "form" | "sheet" | "canvas" | "checklist") => void;
  onOpenDriveModal: () => void;
  onOpenAIAssistant: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  notes,
  onOpenNote,
  onNewNote,
  onOpenDriveModal,
  onOpenAIAssistant,
}) => {
  const [query, setQuery] = useState("");

  // Keydown listener for Cmd+K or Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery("");
      } else if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredNotes = notes.filter(
    (n) =>
      n.title.toLowerCase().includes(query.toLowerCase()) ||
      n.tags.some((t) => t.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/60 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-950">
        {/* Search Input Bar */}
        <div className="flex items-center border-b border-zinc-200 px-4 py-3.5 dark:border-zinc-800">
          <Search className="h-5 w-5 text-amber-500 mr-3" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Digite um comando, título ou tag... (Cmd+K)"
            className="w-full bg-transparent text-sm font-medium text-zinc-900 outline-none placeholder:text-zinc-400 dark:text-zinc-100 dark:placeholder:text-zinc-600"
          />
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Command Menu Results */}
        <div className="max-h-[60vh] overflow-y-auto p-3 space-y-4">
          {/* Quick Create Actions */}
          {!query && (
            <div className="space-y-1">
              <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                Ações Rápidas (Floating Quick Menu)
              </div>

              <button
                onClick={() => {
                  onNewNote("doc");
                  onClose();
                }}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs text-zinc-800 hover:bg-amber-50 hover:text-amber-700 dark:text-zinc-200 dark:hover:bg-amber-950/40"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-amber-500/10 p-1.5 text-amber-600">
                    <FileText className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-bold">Nova Nota Rica / Google Doc</div>
                    <div className="text-[10px] text-zinc-400">Editor completo WYSIWYG no estilo Google Docs</div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </button>

              <button
                onClick={() => {
                  onNewNote("form");
                  onClose();
                }}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs text-zinc-800 hover:bg-sky-50 hover:text-sky-700 dark:text-zinc-200 dark:hover:bg-sky-950/40"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-sky-500/10 p-1.5 text-sky-600">
                    <ClipboardList className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-bold">Formulário Dinâmico Auto-Preenchível</div>
                    <div className="text-[10px] text-zinc-400">Contratos, anamneses e relatórios com marcadores</div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </button>

              <button
                onClick={() => {
                  onNewNote("sheet");
                  onClose();
                }}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs text-zinc-800 hover:bg-emerald-50 hover:text-emerald-700 dark:text-zinc-200 dark:hover:bg-emerald-950/40"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-emerald-500/10 p-1.5 text-emerald-600">
                    <FileSpreadsheet className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-bold">Tabela / Mini-Sheets</div>
                    <div className="text-[10px] text-zinc-400">Planilha com fórmulas integradas (=SUM, =AVERAGE)</div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </button>

              <button
                onClick={() => {
                  onNewNote("canvas");
                  onClose();
                }}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs text-zinc-800 hover:bg-purple-50 hover:text-purple-700 dark:text-zinc-200 dark:hover:bg-purple-950/40"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-purple-500/10 p-1.5 text-purple-600">
                    <PenTool className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-bold">Anotação de Imagem (Canvas Overlay)</div>
                    <div className="text-[10px] text-zinc-400">Desenhe sobre imagens com caneta, formas e texto</div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </button>

              <button
                onClick={() => {
                  onOpenDriveModal();
                  onClose();
                }}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs text-zinc-800 hover:bg-sky-50 hover:text-sky-700 dark:text-zinc-200 dark:hover:bg-sky-950/40"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-sky-500/10 p-1.5 text-sky-600">
                    <Cloud className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-bold">Google Drive Connector & Sync</div>
                    <div className="text-[10px] text-zinc-400">Sincronize notas e gerencie anexos na nuvem</div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </button>

              <button
                onClick={() => {
                  onOpenAIAssistant();
                  onClose();
                }}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs text-indigo-900 hover:bg-indigo-50 dark:text-indigo-200 dark:hover:bg-indigo-950/40"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-indigo-500/10 p-1.5 text-indigo-600">
                    <Sparkles className="h-4 w-4 text-indigo-500 animate-pulse" />
                  </span>
                  <div>
                    <div className="font-bold">Assistente Gemini AI Brainstorm</div>
                    <div className="text-[10px] text-zinc-400">Gere conteúdo, resumos e ideias com inteligência artificial</div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </button>
            </div>
          )}

          {/* Search Matching Notes */}
          <div className="space-y-1">
            <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
              Notas no Workspace ({filteredNotes.length})
            </div>

            {filteredNotes.length === 0 ? (
              <p className="px-3 py-2 text-xs text-zinc-400 italic">
                Nenhuma nota encontrada para "{query}".
              </p>
            ) : (
              filteredNotes.map((note) => (
                <button
                  key={note.id}
                  onClick={() => {
                    onOpenNote(note);
                    onClose();
                  }}
                  className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs text-zinc-800 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="font-bold text-zinc-900 dark:text-zinc-100">{note.title}</span>
                    <span className="text-[10px] text-zinc-400 font-mono">[{note.type}]</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {note.tags.map((t) => (
                      <span key={t} className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
                        #{t}
                      </span>
                    ))}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-zinc-200 bg-zinc-50 px-4 py-2 text-[11px] text-zinc-400 dark:border-zinc-800 dark:bg-zinc-900">
          <span>Use as setas para navegar, Enter para selecionar</span>
          <span className="font-mono">Esc para fechar</span>
        </div>
      </div>
    </div>
  );
};
