import React, { useState, useEffect } from "react";
import {
  FileText,
  Table,
  ClipboardList,
  Image as ImageIcon,
  Upload,
  Plus,
  Command,
  Sparkles,
} from "lucide-react";

interface FloatingQuickMenuProps {
  onCreateDoc: () => void;
  onCreateTable: () => void;
  onCreateForm: () => void;
  onOpenCanvas: () => void;
  onImportDocument: (file: File) => void;
  onOpenCommandPalette: () => void;
}

export const FloatingQuickMenu: React.FC<FloatingQuickMenuProps> = ({
  onCreateDoc,
  onCreateTable,
  onCreateForm,
  onOpenCanvas,
  onImportDocument,
  onOpenCommandPalette,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onOpenCommandPalette();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onOpenCommandPalette]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onImportDocument(e.target.files[0]);
      setIsOpen(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2">
      {/* Floating Popover Options Menu */}
      {isOpen && (
        <div className="w-72 overflow-hidden rounded-2xl border border-zinc-200 bg-white p-2 shadow-2xl backdrop-blur-md transition-all animate-in fade-in slide-in-from-bottom-3 dark:border-zinc-800 dark:bg-zinc-900/95">
          <div className="flex items-center justify-between px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
            <span>Ações Rápidas Híbridas</span>
            <kbd className="flex items-center gap-0.5 rounded bg-zinc-100 px-1.5 py-0.5 text-[10px] text-zinc-500 font-mono dark:bg-zinc-800 dark:text-zinc-400">
              <Command className="h-3 w-3" /> K
            </kbd>
          </div>

          <button
            onClick={() => {
              onCreateDoc();
              setIsOpen(false);
            }}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs text-zinc-800 transition-colors hover:bg-amber-50 hover:text-amber-700 dark:text-zinc-200 dark:hover:bg-amber-950/40"
          >
            <span className="rounded-lg bg-amber-500/10 p-1.5 text-amber-600">
              <FileText className="h-4 w-4" />
            </span>
            <div className="text-left">
              <div className="font-bold">Novo Documento (Docs)</div>
              <div className="text-[10px] text-zinc-400">Editor completo com formatação rica</div>
            </div>
          </button>

          <button
            onClick={() => {
              onCreateTable();
              setIsOpen(false);
            }}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs text-zinc-800 transition-colors hover:bg-emerald-50 hover:text-emerald-700 dark:text-zinc-200 dark:hover:bg-emerald-950/40"
          >
            <span className="rounded-lg bg-emerald-500/10 p-1.5 text-emerald-600">
              <Table className="h-4 w-4" />
            </span>
            <div className="text-left">
              <div className="font-bold">Inserir Tabela (Sheets)</div>
              <div className="text-[10px] text-zinc-400">Planilha interativa com fórmulas =SUM</div>
            </div>
          </button>

          <button
            onClick={() => {
              onCreateForm();
              setIsOpen(false);
            }}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs text-zinc-800 transition-colors hover:bg-sky-50 hover:text-sky-700 dark:text-zinc-200 dark:hover:bg-sky-950/40"
          >
            <span className="rounded-lg bg-sky-500/10 p-1.5 text-sky-600">
              <ClipboardList className="h-4 w-4" />
            </span>
            <div className="text-left">
              <div className="font-bold">Preencher Formulário</div>
              <div className="text-[10px] text-zinc-400">Modelos dinâmicos com marcadores</div>
            </div>
          </button>

          <button
            onClick={() => {
              onOpenCanvas();
              setIsOpen(false);
            }}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs text-zinc-800 transition-colors hover:bg-purple-50 hover:text-purple-700 dark:text-zinc-200 dark:hover:bg-purple-950/40"
          >
            <span className="rounded-lg bg-purple-500/10 p-1.5 text-purple-600">
              <ImageIcon className="h-4 w-4" />
            </span>
            <div className="text-left">
              <div className="font-bold">Anotar sobre Imagem</div>
              <div className="text-[10px] text-zinc-400">Canvas vetorial para notas em imagens</div>
            </div>
          </button>

          <label className="flex w-full cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-xs text-zinc-800 transition-colors hover:bg-indigo-50 hover:text-indigo-700 dark:text-zinc-200 dark:hover:bg-indigo-950/40">
            <span className="rounded-lg bg-indigo-500/10 p-1.5 text-indigo-600">
              <Upload className="h-4 w-4" />
            </span>
            <div className="text-left">
              <div className="font-bold">Importar Documento</div>
              <div className="text-[10px] text-zinc-400">Suporta CSV, TXT, MD e JSON</div>
            </div>
            <input
              type="file"
              onChange={handleFileChange}
              accept=".csv,.txt,.md,.json,.xlsx"
              className="hidden"
            />
          </label>
        </div>
      )}

      {/* Main Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-xl shadow-blue-600/30 transition-all duration-200 hover:bg-blue-700 hover:scale-105 active:scale-95 focus:outline-none"
        aria-label="Abrir Menu de Ações Rápidas"
      >
        <Plus className={`h-6 w-6 transition-transform duration-200 ${isOpen ? "rotate-45" : ""}`} />
      </button>
    </div>
  );
};
