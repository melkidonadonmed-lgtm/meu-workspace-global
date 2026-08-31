import React, { useState, useEffect } from "react";
import {
  X,
  Sparkles,
  ClipboardList,
  Check,
  FileText,
  Plus,
  Wand2,
} from "lucide-react";
import { FormTemplate, Note } from "../types";
import { INITIAL_TEMPLATES } from "../data/initialTemplates";

interface FormFillerModalProps {
  note?: Note | null;
  onClose: () => void;
  onSaveAsNote: (note: Note) => void;
}

export const FormFillerModal: React.FC<FormFillerModalProps> = ({
  note,
  onClose,
  onSaveAsNote,
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<FormTemplate>(
    INITIAL_TEMPLATES[0]
  );
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [docTitle, setDocTitle] = useState("");
  const [generatedHtml, setGeneratedHtml] = useState("");
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiTopicPrompt, setAiTopicPrompt] = useState("");

  useEffect(() => {
    if (note && note.formValues) {
      setFormValues(note.formValues);
      setDocTitle(note.title);
      const tmpl = INITIAL_TEMPLATES.find((t) => t.id === note.formTemplateId) || INITIAL_TEMPLATES[0];
      setSelectedTemplate(tmpl);
    } else {
      // Initialize default field values
      const initialVals: Record<string, string> = {};
      selectedTemplate.fields.forEach((f) => {
        initialVals[f.id] = f.defaultValue || "";
      });
      setFormValues(initialVals);
      setDocTitle(selectedTemplate.title);
    }
  }, [selectedTemplate, note]);

  // Real-time document generation as user types
  useEffect(() => {
    let result = selectedTemplate.templateContent;
    Object.keys(formValues).forEach((key) => {
      const val = formValues[key] || `<span class="text-amber-500 font-bold">[${key}]</span>`;
      const regex = new RegExp(`{{${key}}}`, "g");
      result = result.replace(regex, val);
    });
    setGeneratedHtml(result);
  }, [formValues, selectedTemplate]);

  const handleInputChange = (fieldId: string, val: string) => {
    setFormValues((prev) => ({ ...prev, [fieldId]: val }));
  };

  // AI Auto-Fill Form Fields using Gemini
  const handleAiAutoFill = async () => {
    setIsAiLoading(true);
    try {
      const promptText = `Você é o assistente inteligente do KeepDocs.
Por favor, preencha o formulário para o modelo "${selectedTemplate.title}" com base no seguinte tópico/instrução: "${aiTopicPrompt || 'Dados de exemplo profissionais e realistas'}".

Campos do formulário a serem preenchidos:
${JSON.stringify(selectedTemplate.fields, null, 2)}

Retorne estritamente um objeto JSON com o formato:
{
  "values": {
    "NOME_CAMPO_1": "Valor 1",
    "NOME_CAMPO_2": "Valor 2"
  }
}`;

      const res = await fetch("/api/gemini/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: promptText }),
      });
      const data = await res.json();

      if (data.text) {
        const cleanJsonStr = data.text.replace(/```json|```/g, "").trim();
        const parsed = JSON.parse(cleanJsonStr);
        if (parsed.values) {
          setFormValues((prev) => ({ ...prev, ...parsed.values }));
        }
      }
    } catch (err) {
      console.error("Erro ao preencher com IA:", err);
    } finally {
      setIsAiLoading(false);
    }
  };

  const handleSaveDoc = () => {
    const newNote: Note = {
      id: note ? note.id : "form_note_" + Date.now(),
      title: docTitle || selectedTemplate.title,
      content: generatedHtml,
      type: "form",
      color: "blue",
      tags: ["Formulário", selectedTemplate.category],
      pinned: note ? note.pinned : false,
      archived: false,
      trashed: false,
      createdAt: note ? note.createdAt : new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      formTemplateId: selectedTemplate.id,
      formValues,
    };
    onSaveAsNote(newNote);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm sm:p-6">
      <div className="relative flex h-full max-h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-950">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-sky-500/10 p-2 text-sky-600 dark:text-sky-400">
              <ClipboardList className="h-6 w-6" />
            </span>
            <div>
              <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                Formulário Inteligente Auto-Preenchível
              </h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Preencha os campos dinâmicos e visualize o documento gerado em tempo real
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

        {/* Template Selector Tabs */}
        <div className="flex items-center gap-2 border-b border-zinc-200 bg-zinc-50 px-6 py-2.5 overflow-x-auto dark:border-zinc-800 dark:bg-zinc-900/60">
          <span className="text-xs font-bold text-zinc-400 mr-2 uppercase">Templates:</span>
          {INITIAL_TEMPLATES.map((tmpl) => (
            <button
              key={tmpl.id}
              onClick={() => setSelectedTemplate(tmpl)}
              className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition-all ${
                selectedTemplate.id === tmpl.id
                  ? "bg-sky-600 text-white shadow-xs"
                  : "bg-white text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              {tmpl.title}
            </button>
          ))}
        </div>

        {/* Main Split Body: Left Inputs Form + Right Real-time Preview */}
        <div className="flex flex-1 overflow-hidden">
          {/* Left Panel: Form Inputs */}
          <div className="w-full md:w-1/2 overflow-y-auto border-r border-zinc-200 p-6 dark:border-zinc-800">
            {/* Title Override Input */}
            <div className="mb-6">
              <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-1">
                Título do Documento Final
              </label>
              <input
                type="text"
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm font-semibold text-zinc-900 outline-none focus:border-sky-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
              />
            </div>

            {/* AI Auto-Fill Widget */}
            <div className="mb-6 rounded-2xl border border-sky-200 bg-sky-50/80 p-4 dark:border-sky-900/50 dark:bg-sky-950/40">
              <div className="flex items-center gap-2 font-bold text-sky-900 dark:text-sky-300 text-xs">
                <Sparkles className="h-4 w-4 text-sky-500 animate-pulse" />
                <span>✨ Auto-Preenchimento por Inteligência Artificial (Gemini)</span>
              </div>
              <p className="mt-1 text-[11px] text-sky-800 dark:text-sky-300/80">
                Digite um resumo ou instruções para preencher automaticamente todos os campos do formulário.
              </p>
              <div className="mt-2 flex items-center gap-2">
                <input
                  type="text"
                  value={aiTopicPrompt}
                  onChange={(e) => setAiTopicPrompt(e.target.value)}
                  placeholder="Ex: 'Contrato de R$ 12.000 para consultoria em tecnologia de 3 meses...'"
                  className="w-full rounded-xl border border-sky-200 bg-white px-3 py-1.5 text-xs text-zinc-900 outline-none focus:ring-2 focus:ring-sky-500/20 dark:border-sky-800 dark:bg-zinc-900 dark:text-zinc-100"
                />
                <button
                  disabled={isAiLoading}
                  onClick={handleAiAutoFill}
                  className="flex items-center gap-1.5 rounded-xl bg-sky-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-sky-700 disabled:opacity-50"
                >
                  <Wand2 className="h-3.5 w-3.5" />
                  <span>{isAiLoading ? "Preenchendo..." : "Auto-Preencher"}</span>
                </button>
              </div>
            </div>

            {/* Form Fields Generator */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
                Campos do Formulário ({selectedTemplate.fields.length})
              </h3>

              {selectedTemplate.fields.map((field) => (
                <div key={field.id} className="space-y-1">
                  <label className="flex items-center justify-between text-xs font-medium text-zinc-700 dark:text-zinc-300">
                    <span>
                      {field.label} {field.required && <span className="text-red-500">*</span>}
                    </span>
                    <span className="font-mono text-[10px] text-zinc-400">{"{{" + field.id + "}}"}</span>
                  </label>

                  {field.type === "text_area" ? (
                    <textarea
                      rows={3}
                      value={formValues[field.id] || ""}
                      onChange={(e) => handleInputChange(field.id, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full rounded-xl border border-zinc-200 bg-white p-3 text-xs text-zinc-900 outline-none focus:border-sky-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
                    />
                  ) : field.type === "select" ? (
                    <select
                      value={formValues[field.id] || ""}
                      onChange={(e) => handleInputChange(field.id, e.target.value)}
                      className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-900 outline-none focus:border-sky-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
                    >
                      <option value="">Selecione uma opção...</option>
                      {field.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"}
                      value={formValues[field.id] || ""}
                      onChange={(e) => handleInputChange(field.id, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-900 outline-none focus:border-sky-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel: Live Document Preview */}
          <div className="hidden md:flex w-1/2 flex-col overflow-y-auto bg-zinc-100/70 p-6 dark:bg-zinc-900/50">
            <div className="flex items-center justify-between pb-3 text-xs font-bold uppercase tracking-wider text-zinc-400">
              <span className="flex items-center gap-1.5">
                <FileText className="h-4 w-4 text-sky-500" />
                <span>Pré-Visualização do Documento Final</span>
              </span>
              <span className="text-emerald-600 font-semibold text-[11px]">Atualizando em tempo real</span>
            </div>

            <div className="mx-auto my-2 w-full max-w-xl flex-1 rounded-2xl border border-zinc-200 bg-white p-8 shadow-md dark:border-zinc-800 dark:bg-zinc-900 overflow-y-auto">
              <div
                dangerouslySetInnerHTML={{ __html: generatedHtml }}
                className="prose prose-zinc dark:prose-invert max-w-none text-xs text-zinc-800 dark:text-zinc-200 leading-relaxed"
              />
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <p className="text-xs text-zinc-400">
            O documento formatado será salvo como uma nota editável no seu mosaico KeepDocs.
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="rounded-xl border border-zinc-200 bg-white px-4 py-2 text-xs font-semibold text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300"
            >
              Cancelar
            </button>
            <button
              onClick={handleSaveDoc}
              className="flex items-center gap-2 rounded-xl bg-sky-600 px-5 py-2 text-xs font-bold text-white shadow-md shadow-sky-600/20 hover:bg-sky-700"
            >
              <Check className="h-4 w-4" />
              <span>Gerar e Salvar no KeepDocs</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
