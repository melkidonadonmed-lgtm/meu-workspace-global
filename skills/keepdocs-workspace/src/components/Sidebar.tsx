import React from "react";
import {
  Pin,
  FileText,
  ClipboardList,
  FileSpreadsheet,
  PenTool,
  Cloud,
  Tag,
  Trash2,
  Archive,
  Layers,
  CheckSquare,
  Sparkles,
} from "lucide-react";
import { ViewFilter, NoteColor } from "../types";

interface SidebarProps {
  currentFilter: ViewFilter;
  setFilter: (filter: ViewFilter) => void;
  allTags: string[];
  selectedTag: string | null;
  setSelectedTag: (tag: string | null) => void;
  selectedColor: NoteColor | null;
  setSelectedColor: (color: NoteColor | null) => void;
  notesCounts: {
    all: number;
    pinned: number;
    docs: number;
    forms: number;
    sheets: number;
    canvas: number;
    drive: number;
    trash: number;
  };
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentFilter,
  setFilter,
  allTags,
  selectedTag,
  setSelectedTag,
  selectedColor,
  setSelectedColor,
  notesCounts,
}) => {
  const colors: { name: NoteColor; class: string; label: string }[] = [
    { name: "default", class: "bg-white border-zinc-300 dark:bg-zinc-800", label: "Padrão" },
    { name: "yellow", class: "bg-amber-200 border-amber-300", label: "Amarelo" },
    { name: "green", class: "bg-emerald-200 border-emerald-300", label: "Verde" },
    { name: "teal", class: "bg-teal-200 border-teal-300", label: "Teal" },
    { name: "blue", class: "bg-sky-200 border-sky-300", label: "Azul" },
    { name: "purple", class: "bg-purple-200 border-purple-300", label: "Roxo" },
    { name: "pink", class: "bg-rose-200 border-rose-300", label: "Rosa" },
    { name: "amber", class: "bg-orange-200 border-orange-300", label: "Laranja" },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-zinc-200 bg-zinc-50/50 p-4 dark:border-zinc-800 dark:bg-zinc-950/50">
      <div className="space-y-6">
        {/* Main Navigation Views */}
        <div className="space-y-1">
          <div className="px-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
            Filtros & Módulos
          </div>

          <button
            onClick={() => {
              setFilter("all");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "all" && !selectedTag
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Layers className="h-4 w-4" />
              <span>Todas as Notas</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.all}
            </span>
          </button>

          <button
            onClick={() => {
              setFilter("pinned");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "pinned"
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Pin className="h-4 w-4 text-amber-500 fill-amber-500" />
              <span>Fixadas no Topo</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.pinned}
            </span>
          </button>

          <button
            onClick={() => {
              setFilter("docs");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "docs"
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <FileText className="h-4 w-4 text-amber-600" />
              <span>Google Docs Ricos</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.docs}
            </span>
          </button>

          <button
            onClick={() => {
              setFilter("forms");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "forms"
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <ClipboardList className="h-4 w-4 text-sky-500" />
              <span>Formulários Dinâmicos</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.forms}
            </span>
          </button>

          <button
            onClick={() => {
              setFilter("sheets");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "sheets"
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <FileSpreadsheet className="h-4 w-4 text-emerald-500" />
              <span>Mini-Sheets (Tabelas)</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.sheets}
            </span>
          </button>

          <button
            onClick={() => {
              setFilter("canvas");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "canvas"
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <PenTool className="h-4 w-4 text-purple-500" />
              <span>Anotações Canvas</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.canvas}
            </span>
          </button>

          <button
            onClick={() => {
              setFilter("drive");
              setSelectedTag(null);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "drive"
                ? "bg-amber-500 text-white font-semibold shadow-xs"
                : "text-zinc-700 hover:bg-zinc-200/60 dark:text-zinc-300 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Cloud className="h-4 w-4 text-sky-600" />
              <span>Anexos do Google Drive</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.drive}
            </span>
          </button>
        </div>

        {/* Color Palette Filter */}
        <div className="space-y-2 border-t border-zinc-200 pt-4 dark:border-zinc-800">
          <div className="flex items-center justify-between px-3">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Cores (Keep)</span>
            {selectedColor && (
              <button
                onClick={() => setSelectedColor(null)}
                className="text-[10px] font-medium text-amber-600 hover:underline dark:text-amber-400"
              >
                Limpar
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-1.5 px-3">
            {colors.map((c) => (
              <button
                key={c.name}
                onClick={() => setSelectedColor(selectedColor === c.name ? null : c.name)}
                className={`h-5 w-5 rounded-full border transition-all ${c.class} ${
                  selectedColor === c.name ? "ring-2 ring-amber-500 ring-offset-2 dark:ring-offset-zinc-900" : "opacity-80 hover:opacity-100"
                }`}
                title={c.label}
              />
            ))}
          </div>
        </div>

        {/* Tags List */}
        {allTags.length > 0 && (
          <div className="space-y-2 border-t border-zinc-200 pt-4 dark:border-zinc-800">
            <div className="flex items-center justify-between px-3">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Etiquetas / Tags</span>
              {selectedTag && (
                <button
                  onClick={() => setSelectedTag(null)}
                  className="text-[10px] font-medium text-amber-600 hover:underline dark:text-amber-400"
                >
                  Limpar
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-1.5 px-2">
              {allTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
                  className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                    selectedTag === tag
                      ? "bg-amber-600 text-white shadow-xs"
                      : "bg-zinc-200/70 text-zinc-700 hover:bg-zinc-300/80 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
                  }`}
                >
                  <Tag className="h-3 w-3" />
                  <span>{tag}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* System Archives & Trash */}
        <div className="space-y-1 border-t border-zinc-200 pt-4 dark:border-zinc-800">
          <button
            onClick={() => setFilter("archive")}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "archive"
                ? "bg-amber-500 text-white font-semibold"
                : "text-zinc-600 hover:bg-zinc-200/60 dark:text-zinc-400 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Archive className="h-4 w-4" />
              <span>Arquivadas</span>
            </div>
          </button>

          <button
            onClick={() => setFilter("trash")}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all ${
              currentFilter === "trash"
                ? "bg-red-500 text-white font-semibold"
                : "text-zinc-600 hover:bg-zinc-200/60 dark:text-zinc-400 dark:hover:bg-zinc-800/60"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Trash2 className="h-4 w-4" />
              <span>Lixeira</span>
            </div>
            <span className="rounded-md bg-zinc-200/60 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {notesCounts.trash}
            </span>
          </button>
        </div>

        {/* Google Workspace Info Card */}
        <div className="rounded-2xl border border-amber-200 bg-amber-50/80 p-3.5 text-xs text-amber-900 shadow-xs dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
          <div className="flex items-center gap-1.5 font-bold">
            <Sparkles className="h-4 w-4 text-amber-600 dark:text-amber-400" />
            <span>Keep + Docs Integration</span>
          </div>
          <p className="mt-1 text-[11px] leading-relaxed text-amber-800 dark:text-amber-300/80">
            Alterne entre cartões do Keep e edite documentos completos com tabelas, formulários e canvas.
          </p>
        </div>
      </div>
    </aside>
  );
};
