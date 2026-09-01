import { Note, EmbeddedTableData, AttachedDocument } from "../types";

export class DocumentIngestionService {
  /**
   * Converte arquivos CSV / XLSX ou valores delimitados em tabelas interativas da nota
   */
  static async parseSpreadsheetToTable(file: File): Promise<EmbeddedTableData> {
    const text = await file.text();
    const lines = text.split(/\r?\n/).filter((line) => line.trim() !== "");

    if (lines.length === 0) {
      throw new Error("O arquivo fornecido está vazio.");
    }

    // Detect delimiter (, or ;)
    const firstLine = lines[0];
    const delimiter = firstLine.includes(";") ? ";" : ",";

    const headers = firstLine.split(delimiter).map((h) => h.trim().replace(/^"|"$/g, ""));
    const rows = lines.slice(1).map((line, rIdx) => {
      const columns = line.split(delimiter);
      return headers.map((_, cIdx) => {
        const val = columns[cIdx] ? columns[cIdx].trim().replace(/^"|"$/g, "") : "";
        return {
          id: `cell-${rIdx}-${cIdx}-${Date.now()}`,
          value: val,
          computedValue: val,
        };
      });
    });

    return {
      id: `tbl-${Date.now()}`,
      title: file.name.replace(/\.[^/.]+$/, ""),
      headers: headers.length > 0 ? headers : ["Coluna 1", "Coluna 2"],
      rows,
      hasHeaderRow: true,
      hasSummaryRow: false,
    };
  }

  /**
   * Importa arquivos Markdown, TXT ou JSON direto para uma nova Nota Híbrida
   */
  static async parseTextFileToNote(file: File): Promise<Partial<Note>> {
    const fileName = file.name;
    const fileExt = fileName.split(".").pop()?.toLowerCase();
    const title = fileName.replace(/\.[^/.]+$/, "");
    const rawContent = await file.text();

    if (fileExt === "json") {
      try {
        const parsed = JSON.parse(rawContent);
        if (parsed.title && (parsed.content || parsed.contentHtml)) {
          return {
            ...parsed,
            id: `imported_json_${Date.now()}`,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
        }
      } catch (err) {
        console.warn("JSON não é uma estrutura de nota padrão, importando como texto puro.", err);
      }
    }

    // Converte parágrafos simples para tags HTML no editor Docs
    const htmlContent = rawContent
      .split(/\r?\n\r?\n/)
      .map((paragraph) => {
        const clean = paragraph.trim();
        if (clean.startsWith("# ")) return `<h1>${clean.slice(2)}</h1>`;
        if (clean.startsWith("## ")) return `<h2>${clean.slice(3)}</h2>`;
        if (clean.startsWith("### ")) return `<h3>${clean.slice(4)}</h3>`;
        if (clean.startsWith("- ") || clean.startsWith("* ")) {
          const items = clean.split(/\r?\n/).map((li) => `<li>${li.replace(/^[-*]\s*/, "")}</li>`).join("");
          return `<ul>${items}</ul>`;
        }
        return `<p>${clean.replace(/\n/g, "<br/>")}</p>`;
      })
      .join("");

    const fileTypeMap: Record<string, AttachedDocument["fileType"]> = {
      pdf: "pdf",
      docx: "docx",
      csv: "csv",
      xlsx: "xlsx",
      txt: "txt",
      md: "md",
      json: "json",
    };

    const attachment: AttachedDocument = {
      id: `att-${Date.now()}`,
      fileName,
      fileType: fileTypeMap[fileExt || "txt"] || "txt",
      fileSize: file.size,
      url: URL.createObjectURL(file),
      extractedText: rawContent.slice(0, 500),
    };

    return {
      title: title || "Nota Importada",
      content: htmlContent || "<p>Conteúdo importado sem texto.</p>",
      type: "doc",
      color: "blue",
      tags: ["Importado", fileExt ? fileExt.toUpperCase() : "Documento"],
      attachments: [attachment],
      pinned: false,
      archived: false,
      trashed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  }
}
