import { NoteColor, SheetData } from "../types";

// Note Background Color Mapper (Google Keep Palette)
export function getNoteColorClasses(color: NoteColor): { bg: string; border: string; hover: string; tagBg: string } {
  switch (color) {
    case "yellow":
      return {
        bg: "bg-amber-50/90 dark:bg-amber-950/40",
        border: "border-amber-200/80 dark:border-amber-800/60",
        hover: "hover:bg-amber-100/70 dark:hover:bg-amber-900/50",
        tagBg: "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200",
      };
    case "green":
      return {
        bg: "bg-emerald-50/90 dark:bg-emerald-950/40",
        border: "border-emerald-200/80 dark:border-emerald-800/60",
        hover: "hover:bg-emerald-100/70 dark:hover:bg-emerald-900/50",
        tagBg: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200",
      };
    case "teal":
      return {
        bg: "bg-teal-50/90 dark:bg-teal-950/40",
        border: "border-teal-200/80 dark:border-teal-800/60",
        hover: "hover:bg-teal-100/70 dark:hover:bg-teal-900/50",
        tagBg: "bg-teal-100 text-teal-800 dark:bg-teal-900/60 dark:text-teal-200",
      };
    case "blue":
      return {
        bg: "bg-sky-50/90 dark:bg-sky-950/40",
        border: "border-sky-200/80 dark:border-sky-800/60",
        hover: "hover:bg-sky-100/70 dark:hover:bg-sky-900/50",
        tagBg: "bg-sky-100 text-sky-800 dark:bg-sky-900/60 dark:text-sky-200",
      };
    case "purple":
      return {
        bg: "bg-purple-50/90 dark:bg-purple-950/40",
        border: "border-purple-200/80 dark:border-purple-800/60",
        hover: "hover:bg-purple-100/70 dark:hover:bg-purple-900/50",
        tagBg: "bg-purple-100 text-purple-800 dark:bg-purple-900/60 dark:text-purple-200",
      };
    case "pink":
      return {
        bg: "bg-rose-50/90 dark:bg-rose-950/40",
        border: "border-rose-200/80 dark:border-rose-800/60",
        hover: "hover:bg-rose-100/70 dark:hover:bg-rose-900/50",
        tagBg: "bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-200",
      };
    case "amber":
      return {
        bg: "bg-orange-50/90 dark:bg-orange-950/40",
        border: "border-orange-200/80 dark:border-orange-800/60",
        hover: "hover:bg-orange-100/70 dark:hover:bg-orange-900/50",
        tagBg: "bg-orange-100 text-orange-800 dark:bg-orange-900/60 dark:text-orange-200",
      };
    case "red":
      return {
        bg: "bg-red-50/90 dark:bg-red-950/40",
        border: "border-red-200/80 dark:border-red-800/60",
        hover: "hover:bg-red-100/70 dark:hover:bg-red-900/50",
        tagBg: "bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-200",
      };
    case "gray":
      return {
        bg: "bg-zinc-100/90 dark:bg-zinc-900/80",
        border: "border-zinc-300/80 dark:border-zinc-700/60",
        hover: "hover:bg-zinc-200/70 dark:hover:bg-zinc-800/80",
        tagBg: "bg-zinc-200 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200",
      };
    default:
      return {
        bg: "bg-white dark:bg-zinc-900",
        border: "border-zinc-200 dark:border-zinc-800",
        hover: "hover:bg-zinc-50 dark:hover:bg-zinc-800/50",
        tagBg: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
      };
  }
}

// Format Relative Date
export function formatRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return "Agora mesmo";
    if (diffInSeconds < 3600) return `Há ${Math.floor(diffInSeconds / 60)} min`;
    if (diffInSeconds < 86400) return `Há ${Math.floor(diffInSeconds / 3600)} h`;
    if (diffInSeconds < 86400 * 7) return `Há ${Math.floor(diffInSeconds / 86400)} d`;

    return date.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
  } catch {
    return dateString;
  }
}

// Mini-Sheet Formula Engine
export function evaluateFormula(formula: string, sheetData: SheetData): string {
  if (!formula || !formula.startsWith("=")) return formula;

  const rawFormula = formula.trim().substring(1).toUpperCase();

  const getCellValue = (key: string): number => {
    const cell = sheetData.data[key];
    if (!cell) return 0;
    const val = cell.value?.toString().trim() || "0";
    if (val.startsWith("=")) {
      const evaled = evaluateFormula(val, sheetData);
      return parseFloat(evaled.replace(/[^0-9.-]+/g, "")) || 0;
    }
    const cleanVal = val.replace(/[^0-9.-]+/g, "");
    return parseFloat(cleanVal) || 0;
  };

  const parseRangeKeys = (rangeStr: string): string[] => {
    if (!rangeStr.includes(":")) return [rangeStr.trim()];
    const [start, end] = rangeStr.split(":").map((s) => s.trim());
    const startCol = start.charAt(0);
    const startRow = parseInt(start.substring(1));
    const endCol = end.charAt(0);
    const endRow = parseInt(end.substring(1));

    const keys: string[] = [];
    const colStartCharCode = startCol.charCodeAt(0);
    const colEndCharCode = endCol.charCodeAt(0);

    for (let c = colStartCharCode; c <= colEndCharCode; c++) {
      const col = String.fromCharCode(c);
      for (let r = Math.min(startRow, endRow); r <= Math.max(startRow, endRow); r++) {
        keys.push(`${col}${r}`);
      }
    }
    return keys;
  };

  try {
    // 1. Check for SUM(A1:A5)
    if (rawFormula.startsWith("SUM(")) {
      const arg = rawFormula.slice(4, -1);
      const keys = parseRangeKeys(arg);
      const total = keys.reduce((acc, k) => acc + getCellValue(k), 0);
      return total.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // 2. Check for AVERAGE(A1:A5)
    if (rawFormula.startsWith("AVERAGE(")) {
      const arg = rawFormula.slice(8, -1);
      const keys = parseRangeKeys(arg);
      if (keys.length === 0) return "0.00";
      const total = keys.reduce((acc, k) => acc + getCellValue(k), 0);
      return (total / keys.length).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // 3. Check for COUNT(A1:A5)
    if (rawFormula.startsWith("COUNT(")) {
      const arg = rawFormula.slice(6, -1);
      const keys = parseRangeKeys(arg);
      return keys.length.toString();
    }

    // 4. Check for MIN or MAX
    if (rawFormula.startsWith("MIN(")) {
      const arg = rawFormula.slice(4, -1);
      const keys = parseRangeKeys(arg);
      const nums = keys.map((k) => getCellValue(k));
      return Math.min(...nums).toString();
    }
    if (rawFormula.startsWith("MAX(")) {
      const arg = rawFormula.slice(4, -1);
      const keys = parseRangeKeys(arg);
      const nums = keys.map((k) => getCellValue(k));
      return Math.max(...nums).toString();
    }

    // 5. Basic Arithmetic (A1+B1, A1-B1, A1*B1, A1/B1)
    const expressionWithValues = rawFormula.replace(/([A-Z][0-9]+)/g, (match) => {
      return getCellValue(match).toString();
    });

    // Safe eval for arithmetic
    if (/^[0-9.+\-*/()\s]+$/.test(expressionWithValues)) {
      // eslint-disable-next-line no-eval
      const result = eval(expressionWithValues);
      return typeof result === "number" && !isNaN(result)
        ? result.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 2 })
        : "0";
    }

    return formula;
  } catch (err) {
    console.warn("Formula eval error:", err);
    return "#ERRO!";
  }
}

// Convert HTML to Plain Text for search indexing & snippet previews
export function stripHtml(html: string): string {
  if (!html) return "";
  const tmp = document.createElement("DIV");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}

// Column Letter Helper (0 -> A, 1 -> B, etc)
export function getColumnLetter(colIndex: number): string {
  return String.fromCharCode(65 + colIndex);
}
