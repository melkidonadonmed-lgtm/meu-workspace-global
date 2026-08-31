import React from "react";
import {
  Search,
  Command,
  LayoutGrid,
  Grid3X3,
  List,
  Cloud,
  Plus,
  Sparkles,
  FileText,
  FileSpreadsheet,
  PenTool,
  ClipboardList,
} from "lucide-react";
import { LayoutMode } from "../types";

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  layoutMode: LayoutMode;
  setLayoutMode: (mode: LayoutMode) => void;
  onOpenCommandPalette: () => void;
  onOpenDriveModal: () => void;
  onNewNote: (type: "doc" | "form" | "sheet" | "canvas" | "checklist") => void;
  onOpenAIAssistant: () => void;
  driveSyncedAt: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  setSearchQuery,
  layoutMode,
  setLayoutMode,
  onOpenCommandPalette,
  onOpenDriveModal,
  onNewNote,
  onOpenAIAssistant,
  driveSyncedAt,
}) => {
  const [showNewDropdown, setShowNewDropdown] = React.useState(false);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-zinc-200 bg-white/90 px-4 py-2.5 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/90 sm:px-6">
      {/* Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 via-orange-500 to-indigo-600 shadow-md shadow-amber-500/10">
          <span className="text-xl font-black tracking-tight text-white">K</span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
              KeepDocs <span className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">Workspace</span>
            </h1>
          </div>
          <p className="hidden text-xs text-zinc-500 dark:text-zinc-400 sm:block">
            Mosaico Keep & Editores Docs com Formulários, Sheets e Canvas
          </p>
        </div>
      </div>

      {/* Global Search Bar */}
      <div className="relative mx-4 max-w-lg flex-1">
        <div className="relative flex items-center">
          <Search className="absolute left-3.5 h-4 w-4 text-zinc-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Pesquisar em notas, formulários, planilhas e tags... (Cmd+K)"
            className="w-full rounded-xl border border-zinc-200 bg-zinc-50 py-2 pl-10 pr-12 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-all focus:border-amber-500 focus:bg-white focus:ring-2 focus:ring-amber-500/20 dark:border-zinc-800 dark:bg-zinc-900/60 dark:text-zinc-100 dark:placeholder-zinc-500 dark:focus:border-amber-400 dark:focus:bg-zinc-900"
          />
          <button
            onClick={onOpenCommandPalette}
            className="absolute right-2.5 flex items-center gap-1 rounded-md border border-zinc-200 bg-white px-1.5 py-0.5 text-[11px] font-medium text-zinc-500 shadow-xs hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
            title="Abrir Command Palette"
          >
            <Command className="h-3 w-3" />
            <span>K</span>
          </button>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-2">
        {/* Layout Mode Switcher */}
        <div className="hidden items-center rounded-lg border border-zinc-200 bg-zinc-50 p-1 dark:border-zinc-800 dark:bg-zinc-900 sm:flex">
          <button
            onClick={() => setLayoutMode("masonry")}
            className={`rounded-md p-1.5 transition-colors ${
              layoutMode === "masonry"
                ? "bg-white text-amber-600 shadow-xs dark:bg-zinc-800 dark:text-amber-400"
                : "text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
            }`}
            title="Visualização Mosaico Masonry (Keep)"
          >
            <LayoutGrid className="h-4 w-4" />
          </button>
          <button
            onClick={() => setLayoutMode("grid")}
            className={`rounded-md p-1.5 transition-colors ${
              layoutMode === "grid"
                ? "bg-white text-amber-600 shadow-xs dark:bg-zinc-800 dark:text-amber-400"
                : "text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
            }`}
            title="Grade Uniforme"
          >
            <Grid3X3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setLayoutMode("list")}
            className={`rounded-md p-1.5 transition-colors ${
              layoutMode === "list"
                ? "bg-white text-amber-600 shadow-xs dark:bg-zinc-800 dark:text-amber-400"
                : "text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
            }`}
            title="Visualização em Lista (Docs)"
          >
            <List className="h-4 w-4" />
          </button>
        </div>

        {/* AI Assistant Button */}
        <button
          onClick={onOpenAIAssistant}
          className="flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50 px-3 py-2 text-xs font-semibold text-indigo-700 shadow-xs transition-all hover:border-indigo-300 hover:from-indigo-100 hover:to-purple-100 dark:border-indigo-900 dark:from-indigo-950/40 dark:to-purple-950/40 dark:text-indigo-300 dark:hover:border-indigo-700"
        >
          <Sparkles className="h-3.5 w-3.5 text-indigo-500 animate-pulse" />
          <span className="hidden md:inline">Gemini AI</span>
        </button>

        {/* Google Drive Status & Connector */}
        <button
          onClick={onOpenDriveModal}
          className="flex items-center gap-1.5 rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs font-medium text-zinc-700 shadow-xs transition-all hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
          title="Conectar e Sincronizar Google Drive"
        >
          <Cloud className="h-4 w-4 text-sky-500" />
          <span className="hidden lg:inline">Drive</span>
          {driveSyncedAt && (
            <span className="h-2 w-2 rounded-full bg-emerald-500" title="Sincronizado com o Google Drive" />
          )}
        </button>

        {/* Floating / Quick New Note Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNewDropdown(!showNewDropdown)}
            className="flex items-center gap-1.5 rounded-xl bg-amber-600 px-3.5 py-2 text-xs font-semibold text-white shadow-md shadow-amber-600/20 transition-all hover:bg-amber-700 active:scale-95"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">Criar</span>
          </button>

          {showNewDropdown && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowNewDropdown(false)}
              />
              <div className="absolute right-0 z-50 mt-2 w-56 rounded-xl border border-zinc-200 bg-white p-1.5 shadow-xl dark:border-zinc-800 dark:bg-zinc-900">
                <button
                  onClick={() => {
                    onNewNote("doc");
                    setShowNewDropdown(false);
                  }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium text-zinc-700 hover:bg-amber-50 hover:text-amber-700 dark:text-zinc-300 dark:hover:bg-amber-950/40 dark:hover:text-amber-300"
                >
                  <FileText className="h-4 w-4 text-amber-500" />
                  <div>
                    <div className="font-semibold">Nova Nota Rica (Doc)</div>
                    <div className="text-[10px] text-zinc-400">Editor completo estilo Google Docs</div>
                  </div>
                </button>

                <button
                  onClick={() => {
                    onNewNote("form");
                    setShowNewDropdown(false);
                  }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium text-zinc-700 hover:bg-sky-50 hover:text-sky-700 dark:text-zinc-300 dark:hover:bg-sky-950/40 dark:hover:text-sky-300"
                >
                  <ClipboardList className="h-4 w-4 text-sky-500" />
                  <div>
                    <div className="font-semibold">Formulário Inteligente</div>
                    <div className="text-[10px] text-zinc-400">Template dinâmico com auto-preenchimento</div>
                  </div>
                </button>

                <button
                  onClick={() => {
                    onNewNote("sheet");
                    setShowNewDropdown(false);
                  }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium text-zinc-700 hover:bg-emerald-50 hover:text-emerald-700 dark:text-zinc-300 dark:hover:bg-emerald-950/40 dark:hover:text-emerald-300"
                >
                  <FileSpreadsheet className="h-4 w-4 text-emerald-500" />
                  <div>
                    <div className="font-semibold">Mini-Sheets (Tabela)</div>
                    <div className="text-[10px] text-zinc-400">Planilha interativa com fórmulas</div>
                  </div>
                </button>

                <button
                  onClick={() => {
                    onNewNote("canvas");
                    setShowNewDropdown(false);
                  }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium text-zinc-700 hover:bg-purple-50 hover:text-purple-700 dark:text-zinc-300 dark:hover:bg-purple-950/40 dark:hover:text-purple-300"
                >
                  <PenTool className="h-4 w-4 text-purple-500" />
                  <div>
                    <div className="font-semibold">Anotação Visual (Canvas)</div>
                    <div className="text-[10px] text-zinc-400">Desenhe sobre imagens com ferramentas</div>
                  </div>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
