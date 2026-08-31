import React, { useState } from "react";
import {
  X,
  FileSpreadsheet,
  Plus,
  Trash2,
  Bold,
  AlignLeft,
  AlignRight,
  Check,
  Download,
  Calculator,
} from "lucide-react";
import { SheetData, SheetCell, Note } from "../types";
import { evaluateFormula, getColumnLetter } from "../utils/helpers";

interface MiniSheetEditorProps {
  note?: Note | null;
  onClose: () => void;
  onSaveAsNote: (note: Note) => void;
}

export const MiniSheetEditor: React.FC<MiniSheetEditorProps> = ({
  note,
  onClose,
  onSaveAsNote,
}) => {
  const [title, setTitle] = useState(note?.title || "Nova Planilha Mini-Sheet");
  const [sheetData, setSheetData] = useState<SheetData>(
    note?.sheetData || {
      rows: 6,
      cols: 5,
      data: {
        A1: { value: "Item / Descrição", bold: true },
        B1: { value: "Valor (R$)", bold: true, align: "right" },
        C1: { value: "Qtd", bold: true, align: "right" },
        D1: { value: "Total", bold: true, align: "right" },

        A2: { value: "Desenvolvimento Web" },
        B2: { value: "1500" },
        C2: { value: "2" },
        D2: { value: "=B2*C2", formula: "=B2*C2", bold: true, align: "right" },

        A3: { value: "Design UI/UX KeepDocs" },
        B3: { value: "800" },
        C3: { value: "3" },
        D3: { value: "=B3*C3", formula: "=B3*C3", bold: true, align: "right" },

        A4: { value: "TOTAL GERAL", bold: true },
        B4: { value: "" },
        C4: { value: "" },
        D4: { value: "=SUM(D2:D3)", formula: "=SUM(D2:D3)", bold: true, align: "right" },
      },
    }
  );

  const [selectedCellKey, setSelectedCellKey] = useState<string>("A1");
  const [formulaInputValue, setFormulaInputValue] = useState<string>(
    sheetData.data["A1"]?.formula || sheetData.data["A1"]?.value || ""
  );

  const handleSelectCell = (key: string) => {
    setSelectedCellKey(key);
    const cell = sheetData.data[key];
    setFormulaInputValue(cell?.formula || cell?.value || "");
  };

  const handleCellChange = (key: string, val: string) => {
    const isFormula = val.startsWith("=");
    setSheetData((prev) => {
      const existing = prev.data[key] || {};
      const updatedCell: SheetCell = {
        ...existing,
        value: val,
        formula: isFormula ? val : undefined,
      };
      return {
        ...prev,
        data: {
          ...prev.data,
          [key]: updatedCell,
        },
      };
    });
  };

  const handleToggleCellBold = () => {
    setSheetData((prev) => {
      const cell = prev.data[selectedCellKey] || { value: "" };
      return {
        ...prev,
        data: {
          ...prev.data,
          [selectedCellKey]: { ...cell, bold: !cell.bold },
        },
      };
    });
  };

  const handleCellAlign = (align: "left" | "right") => {
    setSheetData((prev) => {
      const cell = prev.data[selectedCellKey] || { value: "" };
      return {
        ...prev,
        data: {
          ...prev.data,
          [selectedCellKey]: { ...cell, align },
        },
      };
    });
  };

  const handleAddRow = () => {
    setSheetData((prev) => ({ ...prev, rows: prev.rows + 1 }));
  };

  const handleAddCol = () => {
    setSheetData((prev) => ({ ...prev, cols: prev.cols + 1 }));
  };

  const handleSave = () => {
    const newNote: Note = {
      id: note ? note.id : "sheet_note_" + Date.now(),
      title: title || "Mini-Sheet Planilha",
      content: "<p>Planilha interativa com cálculos e fórmulas integradas.</p>",
      type: "sheet",
      color: "green",
      tags: ["Planilha", "Finanças"],
      pinned: note ? note.pinned : false,
      archived: false,
      trashed: false,
      createdAt: note ? note.createdAt : new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      sheetData,
    };
    onSaveAsNote(newNote);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm sm:p-6">
      <div className="relative flex h-full max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-950">
        {/* Top Header */}
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-emerald-500/10 p-2 text-emerald-600 dark:text-emerald-400">
              <FileSpreadsheet className="h-6 w-6" />
            </span>
            <div>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="bg-transparent font-bold text-zinc-900 outline-none dark:text-zinc-100 text-base"
              />
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Suporte a fórmulas: <code className="text-emerald-600 font-mono">=SUM(A1:A5)</code>, <code className="text-emerald-600 font-mono">=AVERAGE()</code>, <code className="text-emerald-600 font-mono">=A1+B1</code>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-xl p-2 text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Formula Toolbar */}
        <div className="flex flex-wrap items-center gap-2 border-b border-zinc-200 bg-zinc-50 px-6 py-2.5 dark:border-zinc-800 dark:bg-zinc-900/70">
          <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-100/80 dark:bg-emerald-950/80 px-2.5 py-1 rounded-lg">
            <Calculator className="h-3.5 w-3.5" />
            <span>{selectedCellKey}</span>
          </div>

          <input
            type="text"
            value={formulaInputValue}
            onChange={(e) => {
              setFormulaInputValue(e.target.value);
              handleCellChange(selectedCellKey, e.target.value);
            }}
            placeholder="Digite valor ou fórmula (ex: =SUM(A1:D1))..."
            className="flex-1 rounded-xl border border-zinc-200 bg-white px-3 py-1 text-xs font-mono text-zinc-900 outline-none focus:border-emerald-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
          />

          <div className="h-4 w-px bg-zinc-300 dark:bg-zinc-700 mx-1" />

          {/* Formatting buttons */}
          <button
            onClick={handleToggleCellBold}
            className="rounded-lg p-1.5 text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800 font-bold"
            title="Negrito"
          >
            <Bold className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleCellAlign("left")}
            className="rounded-lg p-1.5 text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Alinhar Esquerda"
          >
            <AlignLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleCellAlign("right")}
            className="rounded-lg p-1.5 text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Alinhar Direita"
          >
            <AlignRight className="h-4 w-4" />
          </button>

          <div className="h-4 w-px bg-zinc-300 dark:bg-zinc-700 mx-1" />

          <button
            onClick={handleAddRow}
            className="flex items-center gap-1 rounded-lg border border-zinc-200 bg-white px-2.5 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-800 dark:text-zinc-300"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>+ Linha</span>
          </button>
          <button
            onClick={handleAddCol}
            className="flex items-center gap-1 rounded-lg border border-zinc-200 bg-white px-2.5 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-800 dark:text-zinc-300"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>+ Coluna</span>
          </button>
        </div>

        {/* Interactive Spreadsheet Grid */}
        <div className="flex-1 overflow-auto p-6 bg-zinc-100/50 dark:bg-zinc-900/40">
          <div className="mx-auto max-w-full rounded-2xl border border-zinc-200 bg-white shadow-md dark:border-zinc-800 dark:bg-zinc-900 overflow-hidden">
            <table className="w-full border-collapse text-xs">
              <thead>
                <tr className="bg-zinc-100 text-zinc-500 dark:bg-zinc-800/80 dark:text-zinc-400 font-mono">
                  <th className="w-12 border-b border-r border-zinc-200 px-2 py-1.5 text-center dark:border-zinc-800">
                    #
                  </th>
                  {Array.from({ length: sheetData.cols }).map((_, cIdx) => (
                    <th
                      key={cIdx}
                      className="border-b border-r border-zinc-200 px-3 py-1.5 text-center font-bold dark:border-zinc-800"
                    >
                      {getColumnLetter(cIdx)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: sheetData.rows }).map((_, rIdx) => (
                  <tr key={rIdx} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/30">
                    {/* Row Index */}
                    <td className="border-b border-r border-zinc-200 bg-zinc-100/60 text-center font-mono font-bold text-zinc-400 dark:border-zinc-800 dark:bg-zinc-800/40">
                      {rIdx + 1}
                    </td>

                    {/* Cells */}
                    {Array.from({ length: sheetData.cols }).map((_, cIdx) => {
                      const colLetter = getColumnLetter(cIdx);
                      const cellKey = `${colLetter}${rIdx + 1}`;
                      const cell = sheetData.data[cellKey];
                      const isSelected = selectedCellKey === cellKey;
                      const displayValue = cell?.formula
                        ? evaluateFormula(cell.formula, sheetData)
                        : cell?.value || "";

                      return (
                        <td
                          key={cellKey}
                          onClick={() => handleSelectCell(cellKey)}
                          className={`relative border-b border-r border-zinc-200 p-0 text-zinc-900 dark:border-zinc-800 dark:text-zinc-100 ${
                            isSelected ? "ring-2 ring-emerald-500 z-10" : ""
                          }`}
                        >
                          <input
                            type="text"
                            value={displayValue}
                            onChange={(e) => handleCellChange(cellKey, e.target.value)}
                            className={`w-full bg-transparent px-3 py-2 outline-none text-xs ${
                              cell?.bold ? "font-bold text-zinc-900 dark:text-zinc-100" : ""
                            } ${cell?.align === "right" ? "text-right" : "text-left"}`}
                          />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <p className="text-xs text-zinc-400">
            A mini-sheet recalcula automaticamente fórmulas em tempo real.
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="rounded-xl border border-zinc-200 bg-white px-4 py-2 text-xs font-semibold text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2 text-xs font-bold text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-700"
            >
              <Check className="h-4 w-4" />
              <span>Salvar Mini-Sheet</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
