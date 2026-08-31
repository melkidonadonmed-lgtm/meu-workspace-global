import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { MasonryGrid } from "./components/MasonryGrid";
import { DocsEditorModal } from "./components/DocsEditorModal";
import { FormFillerModal } from "./components/FormFillerModal";
import { MiniSheetEditor } from "./components/MiniSheetEditor";
import { ImageAnnotatorModal } from "./components/ImageAnnotatorModal";
import { DrivePickerModal } from "./components/DrivePickerModal";
import { CommandPalette } from "./components/CommandPalette";
import { AIAssistantModal } from "./components/AIAssistantModal";
import { FloatingQuickMenu } from "./components/FloatingQuickMenu";

import { Note, NoteColor, ViewFilter, LayoutMode, DriveAttachment, EmbeddedTableData } from "./types";
import { INITIAL_NOTES } from "./data/initialNotes";
import { DocumentIngestionService } from "./services/DocumentIngestionService";

export default function App() {
  // Persistence in LocalStorage
  const [notes, setNotes] = useState<Note[]>(() => {
    try {
      const saved = localStorage.getItem("keepdocs_workspace_notes_v1");
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.warn("Failed to parse saved notes from localStorage:", e);
    }
    return INITIAL_NOTES;
  });

  // Global Sync timestamp
  const [driveSyncedAt, setDriveSyncedAt] = useState<string | null>(() => {
    return localStorage.getItem("keepdocs_drive_synced_at");
  });

  // UI Navigation & Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [currentFilter, setFilter] = useState<ViewFilter>("all");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<NoteColor | null>(null);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>("masonry");

  // Active Modals State
  const [activeNoteForDocs, setActiveNoteForDocs] = useState<Note | null>(null);
  const [showFormModal, setShowFormModal] = useState(false);
  const [activeFormNote, setActiveFormNote] = useState<Note | null>(null);
  const [showSheetModal, setShowSheetModal] = useState(false);
  const [activeSheetNote, setActiveSheetNote] = useState<Note | null>(null);
  const [showCanvasModal, setShowCanvasModal] = useState(false);
  const [activeCanvasNote, setActiveCanvasNote] = useState<Note | null>(null);
  const [showDriveModal, setShowDriveModal] = useState(false);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showAIAssistant, setShowAIAssistant] = useState(false);

  // Sync to localStorage
  useEffect(() => {
    try {
      localStorage.setItem("keepdocs_workspace_notes_v1", JSON.stringify(notes));
    } catch (e) {
      console.warn("Failed to save notes to localStorage:", e);
    }
  }, [notes]);

  // Extract all unique tags
  const allTags = Array.from(new Set(notes.flatMap((n) => n.tags)));

  // Calculate notes counts for Sidebar
  const notesCounts = {
    all: notes.filter((n) => !n.trashed && !n.archived).length,
    pinned: notes.filter((n) => n.pinned && !n.trashed && !n.archived).length,
    docs: notes.filter((n) => n.type === "doc" && !n.trashed && !n.archived).length,
    forms: notes.filter((n) => n.type === "form" && !n.trashed && !n.archived).length,
    sheets: notes.filter((n) => n.type === "sheet" && !n.trashed && !n.archived).length,
    canvas: notes.filter((n) => n.type === "canvas" && !n.trashed && !n.archived).length,
    drive: notes.filter((n) => n.driveAttachments && n.driveAttachments.length > 0 && !n.trashed).length,
    trash: notes.filter((n) => n.trashed).length,
  };

  // Filter notes based on active sidebar tab & search
  const filteredNotes = notes.filter((note) => {
    if (currentFilter === "trash") return note.trashed;
    if (note.trashed) return false;

    if (currentFilter === "archive") return note.archived;
    if (note.archived) return false;

    if (currentFilter === "pinned" && !note.pinned) return false;
    if (currentFilter === "docs" && note.type !== "doc") return false;
    if (currentFilter === "forms" && note.type !== "form") return false;
    if (currentFilter === "sheets" && note.type !== "sheet") return false;
    if (currentFilter === "canvas" && note.type !== "canvas") return false;
    if (currentFilter === "drive" && (!note.driveAttachments || note.driveAttachments.length === 0)) return false;

    if (selectedTag && !note.tags.includes(selectedTag)) return false;
    if (selectedColor && note.color !== selectedColor) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = note.title.toLowerCase().includes(q);
      const matchContent = note.content.toLowerCase().includes(q);
      const matchTag = note.tags.some((t) => t.toLowerCase().includes(q));
      if (!matchTitle && !matchContent && !matchTag) return false;
    }

    return true;
  });

  // Open note depending on its type
  const handleOpenNote = (note: Note) => {
    if (note.type === "form") {
      setActiveFormNote(note);
      setShowFormModal(true);
    } else if (note.type === "sheet") {
      setActiveSheetNote(note);
      setShowSheetModal(true);
    } else if (note.type === "canvas") {
      setActiveCanvasNote(note);
      setShowCanvasModal(true);
    } else {
      setActiveNoteForDocs(note);
    }
  };

  // Create New Note Router
  const handleNewNote = (type: "doc" | "form" | "sheet" | "canvas" | "checklist") => {
    if (type === "form") {
      setActiveFormNote(null);
      setShowFormModal(true);
    } else if (type === "sheet") {
      setActiveSheetNote(null);
      setShowSheetModal(true);
    } else if (type === "canvas") {
      setActiveCanvasNote(null);
      setShowCanvasModal(true);
    } else {
      const newNote: Note = {
        id: "note_" + Date.now(),
        title: type === "checklist" ? "Nova Lista de Tarefas" : "Novo Documento Google Docs",
        content: type === "checklist" ? "<p>Checklist de atividades:</p>" : "<h2>Novo Documento</h2><p>Comece a escrever seu texto rico aqui...</p>",
        type: type === "checklist" ? "checklist" : "doc",
        color: "default",
        tags: [type === "checklist" ? "Checklist" : "Documento"],
        pinned: false,
        archived: false,
        trashed: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        checklist: type === "checklist" ? [{ id: "c1", text: "Primeira tarefa", completed: false }] : undefined,
      };
      setNotes((prev) => [newNote, ...prev]);
      setActiveNoteForDocs(newNote);
    }
  };

  // Note actions
  const handleTogglePin = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setNotes((prev) =>
      prev.map((n) => (n.id === id ? { ...n, pinned: !n.pinned, updatedAt: new Date().toISOString() } : n))
    );
  };

  const handleChangeColor = (id: string, color: NoteColor, e: React.MouseEvent) => {
    e.stopPropagation();
    setNotes((prev) =>
      prev.map((n) => (n.id === id ? { ...n, color, updatedAt: new Date().toISOString() } : n))
    );
  };

  const handleDuplicate = (note: Note, e: React.MouseEvent) => {
    e.stopPropagation();
    const dup: Note = {
      ...note,
      id: "note_" + Date.now(),
      title: `${note.title} (Cópia)`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setNotes((prev) => [dup, ...prev]);
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setNotes((prev) =>
      prev.map((n) => (n.id === id ? { ...n, trashed: true, updatedAt: new Date().toISOString() } : n))
    );
  };

  const handleSaveNote = (updatedNote: Note) => {
    setNotes((prev) => {
      const exists = prev.some((n) => n.id === updatedNote.id);
      if (exists) {
        return prev.map((n) => (n.id === updatedNote.id ? updatedNote : n));
      }
      return [updatedNote, ...prev];
    });
  };

  // Google Drive Sync API call
  const handleSyncDrive = async () => {
    try {
      const res = await fetch("/api/drive/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notesCount: notes.length, lastSync: driveSyncedAt }),
      });
      const data = await res.json();
      if (data.syncedAt) {
        setDriveSyncedAt(data.syncedAt);
        localStorage.setItem("keepdocs_drive_synced_at", data.syncedAt);
      }
    } catch (err) {
      console.error("Erro na sincronização Drive:", err);
    }
  };

  // Collect all drive attachments across notes
  const allDriveAttachments: DriveAttachment[] = notes.flatMap((n) => n.driveAttachments || []);

  const handleAddGlobalDriveAttachment = (att: DriveAttachment) => {
    if (notes.length > 0) {
      const updatedFirstNote = {
        ...notes[0],
        driveAttachments: [...(notes[0].driveAttachments || []), att],
      };
      handleSaveNote(updatedFirstNote);
    }
  };

  // Document Ingestion Handler for CSV, TXT, MD, JSON files
  const handleImportDocument = async (file: File) => {
    try {
      const ext = file.name.split(".").pop()?.toLowerCase();
      if (ext === "csv" || ext === "xlsx") {
        const table: EmbeddedTableData = await DocumentIngestionService.parseSpreadsheetToTable(file);
        const newNote: Note = {
          id: `imported_tbl_${Date.now()}`,
          title: file.name.replace(/\.[^/.]+$/, ""),
          content: `<p>Tabela importada do arquivo <strong>${file.name}</strong>.</p>`,
          type: "sheet",
          color: "green",
          tags: ["Importado", "Planilha"],
          tables: [table],
          pinned: false,
          archived: false,
          trashed: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        handleSaveNote(newNote);
        setActiveNoteForDocs(newNote);
      } else {
        const partialNote = await DocumentIngestionService.parseTextFileToNote(file);
        const newNote: Note = {
          id: partialNote.id || `imported_doc_${Date.now()}`,
          title: partialNote.title || "Nota Importada",
          content: partialNote.content || "<p>Conteúdo importado.</p>",
          type: "doc",
          color: partialNote.color || "blue",
          tags: partialNote.tags || ["Importado"],
          attachments: partialNote.attachments || [],
          pinned: false,
          archived: false,
          trashed: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        handleSaveNote(newNote);
        setActiveNoteForDocs(newNote);
      }
    } catch (err) {
      console.error("Erro ao importar documento:", err);
    }
  };

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-zinc-100 font-sans text-zinc-900 antialiased dark:bg-zinc-950 dark:text-zinc-100 selection:bg-amber-500/30">
      {/* Top Header */}
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        layoutMode={layoutMode}
        setLayoutMode={setLayoutMode}
        onOpenCommandPalette={() => setShowCommandPalette(true)}
        onOpenDriveModal={() => setShowDriveModal(true)}
        onNewNote={handleNewNote}
        onOpenAIAssistant={() => setShowAIAssistant(true)}
        driveSyncedAt={driveSyncedAt}
      />

      {/* Main Content Area: Sidebar + Masonry Grid */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          currentFilter={currentFilter}
          setFilter={setFilter}
          allTags={allTags}
          selectedTag={selectedTag}
          setSelectedTag={setSelectedTag}
          selectedColor={selectedColor}
          setSelectedColor={setSelectedColor}
          notesCounts={notesCounts}
        />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <MasonryGrid
            notes={filteredNotes}
            layoutMode={layoutMode}
            onOpenNote={handleOpenNote}
            onTogglePin={handleTogglePin}
            onChangeColor={handleChangeColor}
            onDuplicate={handleDuplicate}
            onDelete={handleDelete}
            onNewNote={handleNewNote}
          />
        </main>
      </div>

      {/* Modals Suite */}
      {activeNoteForDocs && (
        <DocsEditorModal
          note={activeNoteForDocs}
          onClose={() => setActiveNoteForDocs(null)}
          onSaveNote={handleSaveNote}
        />
      )}

      {showFormModal && (
        <FormFillerModal
          note={activeFormNote}
          onClose={() => {
            setShowFormModal(false);
            setActiveFormNote(null);
          }}
          onSaveAsNote={handleSaveNote}
        />
      )}

      {showSheetModal && (
        <MiniSheetEditor
          note={activeSheetNote}
          onClose={() => {
            setShowSheetModal(false);
            setActiveSheetNote(null);
          }}
          onSaveAsNote={handleSaveNote}
        />
      )}

      {showCanvasModal && (
        <ImageAnnotatorModal
          note={activeCanvasNote}
          onClose={() => {
            setShowCanvasModal(false);
            setActiveCanvasNote(null);
          }}
          onSaveAsNote={handleSaveNote}
        />
      )}

      {showDriveModal && (
        <DrivePickerModal
          attachments={allDriveAttachments}
          onAddAttachment={handleAddGlobalDriveAttachment}
          onSyncDrive={handleSyncDrive}
          onClose={() => setShowDriveModal(false)}
          driveSyncedAt={driveSyncedAt}
        />
      )}

      <CommandPalette
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        notes={notes}
        onOpenNote={handleOpenNote}
        onNewNote={handleNewNote}
        onOpenDriveModal={() => setShowDriveModal(true)}
        onOpenAIAssistant={() => setShowAIAssistant(true)}
      />

      <AIAssistantModal
        isOpen={showAIAssistant}
        onClose={() => setShowAIAssistant(false)}
        onCreateNoteFromAI={(title, content) => {
          const newNote: Note = {
            id: "ai_note_" + Date.now(),
            title,
            content,
            type: "doc",
            color: "purple",
            tags: ["IA", "Gemini"],
            pinned: false,
            archived: false,
            trashed: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
          handleSaveNote(newNote);
          setActiveNoteForDocs(newNote);
        }}
      />

      {/* Floating Quick Action Button & Popover */}
      <FloatingQuickMenu
        onCreateDoc={() => handleNewNote("doc")}
        onCreateTable={() => handleNewNote("sheet")}
        onCreateForm={() => handleNewNote("form")}
        onOpenCanvas={() => handleNewNote("canvas")}
        onImportDocument={handleImportDocument}
        onOpenCommandPalette={() => setShowCommandPalette(true)}
      />
    </div>
  );
}
