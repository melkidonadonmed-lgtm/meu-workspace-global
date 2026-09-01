import React from "react";
import { Note, NoteColor, LayoutMode } from "../types";
import { NoteCard } from "./NoteCard";
import { Sparkles, Plus, FileText } from "lucide-react";

interface MasonryGridProps {
  notes: Note[];
  layoutMode: LayoutMode;
  onOpenNote: (note: Note) => void;
  onTogglePin: (id: string, e: React.MouseEvent) => void;
  onChangeColor: (id: string, color: NoteColor, e: React.MouseEvent) => void;
  onDuplicate: (note: Note, e: React.MouseEvent) => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
  onNewNote: (type: "doc" | "form" | "sheet" | "canvas" | "checklist") => void;
}

export const MasonryGrid: React.FC<MasonryGridProps> = ({
  notes,
  layoutMode,
  onOpenNote,
  onTogglePin,
  onChangeColor,
  onDuplicate,
  onDelete,
  onNewNote,
}) => {
  const pinnedNotes = notes.filter((n) => n.pinned);
  const unpinnedNotes = notes.filter((n) => !n.pinned);

  if (notes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-zinc-200 bg-zinc-50/50 py-16 text-center dark:border-zinc-800 dark:bg-zinc-950/30">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-100 text-amber-600 dark:bg-amber-950/60 dark:text-amber-400">
          <FileText className="h-7 w-7" />
        </div>
        <h3 className="mt-4 text-base font-bold text-zinc-900 dark:text-zinc-100">
          Nenhuma nota encontrada no filtro atual
        </h3>
        <p className="mt-1 max-w-sm text-xs text-zinc-500 dark:text-zinc-400">
          Crie um novo documento no estilo Google Docs, um formulário dinâmico auto-preenchível ou uma planilha mini-sheet.
        </p>

        <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
          <button
            onClick={() => onNewNote("doc")}
            className="flex items-center gap-1.5 rounded-xl bg-amber-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-amber-600/20 hover:bg-amber-700"
          >
            <Plus className="h-4 w-4" />
            <span>Criar Nova Nota Doc</span>
          </button>
          <button
            onClick={() => onNewNote("form")}
            className="flex items-center gap-1.5 rounded-xl border border-zinc-200 bg-white px-4 py-2 text-xs font-semibold text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300"
          >
            <Sparkles className="h-4 w-4 text-sky-500" />
            <span>Usar Template Dinâmico</span>
          </button>
        </div>
      </div>
    );
  }

  const renderCardList = (items: Note[]) => {
    if (layoutMode === "list") {
      return (
        <div className="flex flex-col space-y-3">
          {items.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              onOpen={onOpenNote}
              onTogglePin={onTogglePin}
              onChangeColor={onChangeColor}
              onDuplicate={onDuplicate}
              onDelete={onDelete}
            />
          ))}
        </div>
      );
    }

    if (layoutMode === "grid") {
      return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {items.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              onOpen={onOpenNote}
              onTogglePin={onTogglePin}
              onChangeColor={onChangeColor}
              onDuplicate={onDuplicate}
              onDelete={onDelete}
            />
          ))}
        </div>
      );
    }

    // Default: Masonry CSS Columns Flow (Google Keep Style)
    return (
      <div className="columns-1 gap-4 space-y-4 sm:columns-2 lg:columns-3 xl:columns-4">
        {items.map((note) => (
          <div key={note.id} className="break-inside-avoid">
            <NoteCard
              note={note}
              onOpen={onOpenNote}
              onTogglePin={onTogglePin}
              onChangeColor={onChangeColor}
              onDuplicate={onDuplicate}
              onDelete={onDelete}
            />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Pinned Notes Section */}
      {pinnedNotes.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
            <span>Fixadas no Topo ({pinnedNotes.length})</span>
          </div>
          {renderCardList(pinnedNotes)}
        </div>
      )}

      {/* Unpinned Notes Section */}
      {unpinnedNotes.length > 0 && (
        <div className="space-y-3">
          {pinnedNotes.length > 0 && (
            <div className="text-xs font-bold uppercase tracking-wider text-zinc-400 border-t border-zinc-200/80 pt-4 dark:border-zinc-800">
              Outras Notas
            </div>
          )}
          {renderCardList(unpinnedNotes)}
        </div>
      )}
    </div>
  );
};
