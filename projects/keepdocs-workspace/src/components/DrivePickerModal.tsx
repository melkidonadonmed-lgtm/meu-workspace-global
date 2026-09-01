import React, { useState } from "react";
import {
  X,
  Cloud,
  FileText,
  FileSpreadsheet,
  FileCode,
  Link,
  Upload,
  RefreshCw,
  CheckCircle2,
  ExternalLink,
  Plus,
} from "lucide-react";
import { DriveAttachment } from "../types";

interface DrivePickerModalProps {
  attachments: DriveAttachment[];
  onAddAttachment: (att: DriveAttachment) => void;
  onSyncDrive: () => Promise<void>;
  onClose: () => void;
  driveSyncedAt: string | null;
}

export const DrivePickerModal: React.FC<DrivePickerModalProps> = ({
  attachments,
  onAddAttachment,
  onSyncDrive,
  onClose,
  driveSyncedAt,
}) => {
  const [fileName, setFileName] = useState("");
  const [driveUrl, setDriveUrl] = useState("");
  const [fileType, setFileType] = useState<"doc" | "sheet" | "slide" | "pdf" | "image" | "file">("doc");
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");

  const handleManualAdd = () => {
    if (!fileName.trim() || !driveUrl.trim()) return;
    const newAtt: DriveAttachment = {
      id: "drive_" + Date.now(),
      name: fileName.trim(),
      mimeType: fileType === "sheet" ? "application/vnd.google-apps.spreadsheet" : "application/pdf",
      size: "1.5 MB",
      driveUrl: driveUrl.trim(),
      syncedAt: new Date().toISOString(),
      fileType,
    };
    onAddAttachment(newAtt);
    setFileName("");
    setDriveUrl("");
  };

  const handleTriggerSync = async () => {
    setIsSyncing(true);
    setSyncMessage("");
    await onSyncDrive();
    setIsSyncing(false);
    setSyncMessage("Workspace sincronizado com sucesso com o Google Drive!");
    setTimeout(() => setSyncMessage(""), 4000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm sm:p-6">
      <div className="relative flex h-full max-h-[85vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-950">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-sky-500/10 p-2 text-sky-600 dark:text-sky-400">
              <Cloud className="h-6 w-6" />
            </span>
            <div>
              <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                Google Drive Connector & Sync
              </h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Anexe arquivos do Google Drive e mantenha seu mosaico de notas sincronizado na nuvem
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

        {/* Sync Action Status Card */}
        <div className="m-6 rounded-2xl border border-sky-200 bg-sky-50/80 p-4 dark:border-sky-900/50 dark:bg-sky-950/40">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 font-bold text-sky-900 dark:text-sky-300 text-xs">
                <CheckCircle2 className="h-4 w-4 text-sky-500" />
                <span>Sincronização em Tempo Real com Google Workspace</span>
              </div>
              <p className="mt-1 text-[11px] text-sky-800 dark:text-sky-300/80">
                {driveSyncedAt
                  ? `Última sincronização completa: ${new Date(driveSyncedAt).toLocaleString("pt-BR")}`
                  : "Ainda não sincronizado nesta sessão."}
              </p>
            </div>

            <button
              disabled={isSyncing}
              onClick={handleTriggerSync}
              className="flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2 text-xs font-bold text-white hover:bg-sky-700 disabled:opacity-50 shadow-xs"
            >
              <RefreshCw className={`h-4 w-4 ${isSyncing ? "animate-spin" : ""}`} />
              <span>{isSyncing ? "Sincronizando..." : "Sincronizar Agora"}</span>
            </button>
          </div>

          {syncMessage && (
            <p className="mt-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
              ✓ {syncMessage}
            </p>
          )}
        </div>

        {/* Content Body: Attached Files List + Link Form */}
        <div className="flex-1 overflow-y-auto px-6 space-y-6">
          {/* Form to Attach Google Drive File Link */}
          <div className="rounded-2xl border border-zinc-200 bg-zinc-50/60 p-4 dark:border-zinc-800 dark:bg-zinc-900/40 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
              Anexar Novo Link do Google Drive
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <input
                type="text"
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                placeholder="Nome do Arquivo (ex: Proposta_Comercial.pdf)"
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-900 outline-none dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
              />
              <input
                type="text"
                value={driveUrl}
                onChange={(e) => setDriveUrl(e.target.value)}
                placeholder="URL do Google Drive (https://drive.google.com/...)"
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs text-zinc-900 outline-none dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
              />
            </div>

            <div className="flex items-center justify-between pt-1">
              <select
                value={fileType}
                onChange={(e: any) => setFileType(e.target.value)}
                className="rounded-xl border border-zinc-200 bg-white px-3 py-1.5 text-xs text-zinc-900 outline-none dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
              >
                <option value="doc">Documento Google Docs</option>
                <option value="sheet">Planilha Google Sheets</option>
                <option value="pdf">Arquivo PDF</option>
                <option value="image">Imagem</option>
              </select>

              <button
                disabled={!fileName.trim() || !driveUrl.trim()}
                onClick={handleManualAdd}
                className="flex items-center gap-1.5 rounded-xl bg-sky-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-sky-700 disabled:opacity-50"
              >
                <Plus className="h-4 w-4" />
                <span>Anexar Arquivo</span>
              </button>
            </div>
          </div>

          {/* List of Connected Attachments */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Arquivos Anexados ao Workspace ({attachments.length})
            </h3>

            {attachments.length === 0 ? (
              <p className="text-xs text-zinc-400 italic">Nenhum anexo cadastrado.</p>
            ) : (
              <div className="space-y-2">
                {attachments.map((att) => (
                  <div
                    key={att.id}
                    className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-3 text-xs shadow-2xs dark:border-zinc-800 dark:bg-zinc-900"
                  >
                    <div className="flex items-center gap-3">
                      <span className="rounded-lg bg-sky-100 p-2 text-sky-600 dark:bg-sky-950 dark:text-sky-400">
                        {att.fileType === "sheet" ? (
                          <FileSpreadsheet className="h-4 w-4" />
                        ) : (
                          <FileText className="h-4 w-4" />
                        )}
                      </span>
                      <div>
                        <div className="font-bold text-zinc-900 dark:text-zinc-100">{att.name}</div>
                        <div className="text-[10px] text-zinc-400">
                          {att.size} • Sincronizado em {new Date(att.syncedAt).toLocaleTimeString("pt-BR")}
                        </div>
                      </div>
                    </div>

                    <a
                      href={att.driveUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 rounded-lg border border-zinc-200 px-2.5 py-1 text-xs font-medium text-sky-600 hover:bg-sky-50 dark:border-zinc-800 dark:text-sky-400 dark:hover:bg-sky-950/40"
                    >
                      <span>Abrir no Drive</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <button
            onClick={onClose}
            className="rounded-xl bg-zinc-900 px-5 py-2 text-xs font-bold text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900"
          >
            Concluir
          </button>
        </div>
      </div>
    </div>
  );
};
