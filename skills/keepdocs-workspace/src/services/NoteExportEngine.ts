import { Note, EmbeddedTableData } from "../types";
import { stripHtml } from "../utils/helpers";

export class NoteExportEngine {
  /**
   * Exporta a nota completa para formato Markdown (.md)
   */
  static exportToMarkdown(note: Note): void {
    let md = `# ${note.title}\n\n`;

    // Data e tags
    md += `*Criado em: ${new Date(note.createdAt).toLocaleDateString("pt-BR")}*\n`;
    if (note.tags && note.tags.length > 0) {
      md += `*Tags: ${note.tags.map((t) => `#${t}`).join(", ")}*\n`;
    }
    md += `\n---\n\n`;

    // Converte HTML do editor para texto Markdown básico
    const plainText = stripHtml(note.content);
    md += plainText + "\n\n";

    // Se houver tabelas vinculadas (Embedded Tables)
    if (note.tables && note.tables.length > 0) {
      note.tables.forEach((table) => {
        md += `### 📊 ${table.title}\n\n`;
        md += `| ${table.headers.join(" | ")} |\n`;
        md += `| ${table.headers.map(() => "---").join(" | ")} |\n`;
        table.rows.forEach((row) => {
          md += `| ${row.map((cell) => cell.computedValue || cell.value || "").join(" | ")} |\n`;
        });
        md += "\n";
      });
    }

    // Se for uma Mini-Sheet Planilha
    if (note.sheetData) {
      md += `### 📊 Dados da Planilha Mini-Sheet\n\n`;
      const { rows, cols, data } = note.sheetData;
      const headers = Array.from({ length: cols }).map((_, c) => String.fromCharCode(65 + c));
      md += `| # | ${headers.join(" | ")} |\n`;
      md += `| --- | ${headers.map(() => "---").join(" | ")} |\n`;

      for (let r = 1; r <= rows; r++) {
        const rowVals = headers.map((h) => data[`${h}${r}`]?.value || "");
        md += `| ${r} | ${rowVals.join(" | ")} |\n`;
      }
      md += "\n";
    }

    this.downloadFile(`${this.sanitizeFilename(note.title)}.md`, md, "text/markdown");
  }

  /**
   * Exporta uma tabela interativa específica para formato CSV (.csv)
   */
  static exportTableToCSV(table: EmbeddedTableData): void {
    let csv = `${table.headers.map((h) => `"${h}"`).join(",")}\n`;
    table.rows.forEach((row) => {
      csv += `${row.map((c) => `"${(c.computedValue || c.value || "").replace(/"/g, '""')}"`).join(",")}\n`;
    });

    this.downloadFile(`${this.sanitizeFilename(table.title)}.csv`, csv, "text/csv");
  }

  /**
   * Exporta o estado completo da nota para backup ou reimportação (.json)
   */
  static exportToJSON(note: Note): void {
    const data = JSON.stringify(note, null, 2);
    this.downloadFile(`${this.sanitizeFilename(note.title)}.json`, data, "application/json");
  }

  /**
   * Exporta para documento HTML formatado (.html)
   */
  static exportToHTML(note: Note): void {
    const htmlContent = `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>${note.title}</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; max-w: 800px; margin: 40px auto; padding: 0 20px; color: #202124; line-height: 1.6; }
    h1 { color: #1a73e8; border-bottom: 2px solid #e8eaed; padding-bottom: 10px; }
    .badge { background: #e8f0fe; color: #1a73e8; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { border: 1px solid #dadce0; padding: 8px 12px; text-align: left; }
    th { background: #f8f9fa; }
  </style>
</head>
<body>
  <h1>${note.title}</h1>
  <p><strong>Criado:</strong> ${new Date(note.createdAt).toLocaleString("pt-BR")}</p>
  <div>${note.tags.map((t) => `<span class="badge">#${t}</span>`).join("")}</div>
  <hr style="border: none; border-top: 1px solid #dadce0; margin: 20px 0;">
  <div>${note.content}</div>
</body>
</html>`;

    this.downloadFile(`${this.sanitizeFilename(note.title)}.html`, htmlContent, "text/html");
  }

  private static sanitizeFilename(filename: string): string {
    return (filename || "nota")
      .toLowerCase()
      .replace(/[^a-z0-9_-]/g, "_")
      .replace(/_+/g, "_");
  }

  private static downloadFile(filename: string, content: string, mimeType: string): void {
    const blob = new Blob([content], { type: `${mimeType};charset=utf-8;` });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}
