import React from "react";
import {
  Pin,
  Tag,
  Cloud,
  Copy,
  Trash2,
  FileText,
  ClipboardList,
  FileSpreadsheet,
  PenTool,
  CheckSquare,
  Palette,
  ExternalLink,
  MessageSquare,
} from "lucide-react";
import { Note, NoteColor } from "../types";
import { getNoteColorClasses, evaluateFormula, formatRelativeTime, stripHtml } from "../utils/helpers";

interface NoteCardProps {
  note: Note;
  onOpen: (note: Note) => void;
  onTogglePin: (id: string, e: React.MouseEvent) => void;
  onChangeColor: (id: string, color: NoteColor, e: React.MouseEvent) => void;
  onDuplicate: (note: Note, e: React.MouseEvent) => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
}

export const NoteCard: React.FC<NoteCardProps> = ({
  note,
  onOpen,
  onTogglePin,
  onChangeColor,
  onDuplicate,
  onDelete,
}) => {
  const [showColorPicker, setShowColorPicker] = React.useState(false);
  const colorStyle = getNoteColorClasses(note.color);

  const colors: { name: NoteColor; bgClass: string }[] = [
    { name: "default", bgClass: "bg-white border-zinc-300 dark:bg-zinc-800" },
    { name: "yellow", bgClass: "bg-amber-300" },
    { name: "green", bgClass: "bg-emerald-300" },
    { name: "teal", bgClass: "bg-teal-300" },
    { name: "blue", bgClass: "bg-sky-300" },
    { name: "purple", bgClass: "bg-purple-300" },
    { name: "pink", bgClass: "bg-rose-300" },
    { name: "amber", bgClass: "bg-orange-300" },
  ];

  const getTypeIcon = () => {
    switch (note.type) {
      case "form":
        return <ClipboardList className="h-3.5 w-3.5 text-sky-600" />;
      case "sheet":
        return <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />;
      case "canvas":
        return <PenTool className="h-3.5 w-3.5 text-purple-600" />;
      case "checklist":
        return <CheckSquare className="h-3.5 w-3.5 text-teal-600" />;
      default:
        return <FileText className="h-3.5 w-3.5 text-amber-600" />;
    }
  };

  return (
    <div
      onClick={() => onOpen(note)}
      className={`group relative flex flex-col justify-between rounded-2xl border p-4 transition-all duration-200 cursor-pointer shadow-xs hover:shadow-md ${colorStyle.bg} ${colorStyle.border} ${colorStyle.hover}`}
    >
      {/* Top Header Row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="rounded-md bg-white/70 p-1 dark:bg-zinc-800/80 shadow-2xs">
            {getTypeIcon()}
          </span>
          <h3 className="line-clamp-2 text-sm font-bold text-zinc-900 dark:text-zinc-100">
            {note.title || "Nota Sem Título"}
          </h3>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onTogglePin(note.id, e);
          }}
          className={`rounded-lg p-1.5 transition-colors ${
            note.pinned
              ? "text-amber-600 bg-amber-100/80 dark:bg-amber-900/60 dark:text-amber-300"
              : "opacity-0 group-hover:opacity-100 text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
          }`}
          title={note.pinned ? "Desafixar nota" : "Fixar nota no topo"}
        >
          <Pin className={`h-4 w-4 ${note.pinned ? "fill-amber-600" : ""}`} />
        </button>
      </div>

      {/* Main Content Preview Area */}
      <div className="my-3 flex-1 text-xs text-zinc-700 dark:text-zinc-300">
        {/* Module 1: Mini-Sheet Preview */}
        {note.type === "sheet" && note.sheetData ? (
          <div className="my-2 overflow-x-auto rounded-xl border border-zinc-200/80 bg-white/80 p-1.5 dark:border-zinc-800 dark:bg-zinc-900/80">
            <table className="w-full text-left text-[11px]">
              <tbody>
                {Array.from({ length: Math.min(note.sheetData.rows, 4) }).map((_, rIdx) => (
                  <tr key={rIdx} className="border-b border-zinc-100 last:border-0 dark:border-zinc-800/50">
                    {Array.from({ length: Math.min(note.sheetData?.cols || 3, 3) }).map((_, cIdx) => {
                      const key = `${String.fromCharCode(65 + cIdx)}${rIdx + 1}`;
                      const cell = note.sheetData?.data[key];
                      const evaluated = cell?.formula ? evaluateFormula(cell.formula, note.sheetData!) : cell?.value || "";
                      return (
                        <td
                          key={key}
                          className={`px-1.5 py-1 ${cell?.bold ? "font-bold text-zinc-900 dark:text-zinc-100" : ""} ${
                            cell?.align === "right" ? "text-right" : ""
                          }`}
                        >
                          {evaluated}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}

        {/* Module 2: Image Canvas Preview */}
        {note.type === "canvas" && note.imageAnnotation ? (
          <div className="relative my-2 overflow-hidden rounded-xl border border-zinc-200/80 bg-white dark:border-zinc-800 dark:bg-zinc-900 h-32 flex items-center justify-center">
            {note.imageAnnotation.base64Image ? (
              <img
                src={note.imageAnnotation.base64Image}
                alt="Canvas Preview"
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex flex-col items-center justify-center p-3 text-center text-zinc-400">
                <PenTool className="h-6 w-6 text-purple-500/70 mb-1" />
                <span className="text-[10px]">Canvas Vetorial ({note.imageAnnotation.layers.length} camadas)</span>
              </div>
            )}
          </div>
        ) : null}

        {/* Module 3: Checklist Items Preview */}
        {note.type === "checklist" && note.checklist ? (
          <div className="my-2 space-y-1">
            {note.checklist.slice(0, 4).map((item) => (
              <div key={item.id} className="flex items-center gap-2 text-xs">
                <span
                  className={`flex h-3.5 w-3.5 items-center justify-center rounded-sm border ${
                    item.completed
                      ? "border-emerald-500 bg-emerald-500 text-white"
                      : "border-zinc-300 dark:border-zinc-600"
                  }`}
                >
                  {item.completed && "✓"}
                </span>
                <span className={item.completed ? "line-through text-zinc-400" : ""}>{item.text}</span>
              </div>
            ))}
            {note.checklist.length > 4 && (
              <div className="text-[10px] font-medium text-zinc-400 pl-5">
                +{note.checklist.length - 4} mais itens
              </div>
            )}
          </div>
        ) : null}

        {/* Default / Doc / Form Text Snippet */}
        {note.type !== "sheet" && note.type !== "canvas" && note.type !== "checklist" && (
          <p className="line-clamp-4 leading-relaxed font-normal text-zinc-600 dark:text-zinc-300">
            {stripHtml(note.content) || "Sem conteúdo em texto."}
          </p>
        )}
      </div>

      {/* Tags and Attachments Bar */}
      <div className="flex flex-wrap items-center gap-1.5 my-1">
        {note.tags.map((tag) => (
          <span key={tag} className={`rounded-md px-2 py-0.5 text-[10px] font-semibold ${colorStyle.tagBg}`}>
            #{tag}
          </span>
        ))}

        {note.driveAttachments && note.driveAttachments.length > 0 && (
          <span className="flex items-center gap-1 rounded-md bg-sky-100 px-2 py-0.5 text-[10px] font-semibold text-sky-800 dark:bg-sky-950/80 dark:text-sky-300">
            <Cloud className="h-3 w-3" />
            <span>{note.driveAttachments.length} Anexo Drive</span>
          </span>
        )}

        {note.tables && note.tables.length > 0 && (
          <span className="flex items-center gap-1 rounded-md bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
            <FileSpreadsheet className="h-3 w-3" />
            <span>{note.tables.length} Tabela Sheets</span>
          </span>
        )}

        {note.attachments && note.attachments.length > 0 && (
          <span className="flex items-center gap-1 rounded-md bg-purple-100 px-2 py-0.5 text-[10px] font-semibold text-purple-800 dark:bg-purple-950/80 dark:text-purple-300">
            <Tag className="h-3 w-3" />
            <span>{note.attachments.length} Arquivo(s)</span>
          </span>
        )}

        {note.comments && note.comments.length > 0 && (
          <span className="flex items-center gap-1 rounded-md bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-800 dark:bg-indigo-950/80 dark:text-indigo-300">
            <MessageSquare className="h-3 w-3" />
            <span>{note.comments.length}</span>
          </span>
        )}
      </div>

      {/* Footer Controls & Timestamp */}
      <div className="mt-2 flex items-center justify-between border-t border-zinc-200/50 pt-2 text-[11px] text-zinc-400 dark:border-zinc-800/50">
        <span>{formatRelativeTime(note.updatedAt)}</span>

        {/* Quick Hover Actions Toolbar */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Color Picker Toggle */}
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowColorPicker(!showColorPicker);
              }}
              className="rounded-lg p-1 text-zinc-500 hover:bg-white/80 hover:text-zinc-900 dark:hover:bg-zinc-800"
              title="Mudar cor do card"
            >
              <Palette className="h-3.5 w-3.5" />
            </button>

            {showColorPicker && (
              <div
                className="absolute bottom-full left-0 z-50 mb-1 flex items-center gap-1 rounded-xl border border-zinc-200 bg-white p-1.5 shadow-xl dark:border-zinc-800 dark:bg-zinc-900"
                onClick={(e) => e.stopPropagation()}
              >
                {colors.map((c) => (
                  <button
                    key={c.name}
                    onClick={(e) => {
                      onChangeColor(note.id, c.name, e);
                      setShowColorPicker(false);
                    }}
                    className={`h-4 w-4 rounded-full border ${c.bgClass}`}
                  />
                ))}
              </div>
            )}
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDuplicate(note, e);
            }}
            className="rounded-lg p-1 text-zinc-500 hover:bg-white/80 hover:text-zinc-900 dark:hover:bg-zinc-800"
            title="Duplicar nota"
          >
            <Copy className="h-3.5 w-3.5" />
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(note.id, e);
            }}
            className="rounded-lg p-1 text-zinc-500 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-950/60"
            title="Mover para lixeira"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>

          <button
            onClick={() => onOpen(note)}
            className="rounded-lg p-1 text-amber-600 hover:bg-amber-100/80 dark:text-amber-400 dark:hover:bg-amber-950/60"
            title="Expandir no Editor Docs"
          >
            <ExternalLink className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
