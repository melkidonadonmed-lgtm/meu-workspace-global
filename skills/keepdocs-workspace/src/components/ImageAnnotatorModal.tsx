import React, { useRef, useState, useEffect } from "react";
import {
  X,
  PenTool,
  Highlighter,
  Square,
  Circle,
  MoveRight,
  Type,
  Eraser,
  Undo2,
  Redo2,
  Upload,
  Sparkles,
  Download,
  Check,
  Image as ImageIcon,
} from "lucide-react";
import { ImageAnnotation, ImageAnnotationLayer, Note } from "../types";

interface ImageAnnotatorModalProps {
  note?: Note | null;
  onClose: () => void;
  onSaveAsNote: (note: Note) => void;
}

export const ImageAnnotatorModal: React.FC<ImageAnnotatorModalProps> = ({
  note,
  onClose,
  onSaveAsNote,
}) => {
  const [title, setTitle] = useState(note?.title || "Nova Anotação Canvas Visual");
  const [selectedTool, setSelectedTool] = useState<"pen" | "highlighter" | "rect" | "circle" | "arrow" | "text" | "eraser">("pen");
  const [color, setColor] = useState<string>("#ef4444");
  const [strokeWidth, setStrokeWidth] = useState<number>(3);
  const [bgImage, setBgImage] = useState<string>(note?.imageAnnotation?.base64Image || "");
  const [layers, setLayers] = useState<ImageAnnotationLayer[]>(note?.imageAnnotation?.layers || []);
  const [history, setHistory] = useState<ImageAnnotationLayer[][]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const [isDrawing, setIsDrawing] = useState<boolean>(false);
  const [currentPath, setCurrentPath] = useState<{ x: number; y: number }[]>([]);
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);
  const [textInputVal, setTextInputVal] = useState<string>("");
  const [textPos, setTextPos] = useState<{ x: number; y: number } | null>(null);
  const [aiImagePrompt, setAiImagePrompt] = useState<string>("");
  const [isAiGenerating, setIsAiGenerating] = useState<boolean>(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Redraw Canvas on layers or bgImage changes
  const redrawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Background Image if present
    if (bgImage) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        drawLayers(ctx);
      };
      img.src = bgImage;
    } else {
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      drawLayers(ctx);
    }
  };

  const drawLayers = (ctx: CanvasRenderingContext2D) => {
    layers.forEach((layer) => {
      ctx.strokeStyle = layer.color;
      ctx.fillStyle = layer.color;
      ctx.lineWidth = layer.width;
      ctx.lineCap = "round";

      if (layer.type === "pen" || layer.type === "highlighter") {
        if (layer.type === "highlighter") {
          ctx.globalAlpha = 0.4;
        } else {
          ctx.globalAlpha = 1.0;
        }
        if (layer.points && layer.points.length > 1) {
          ctx.beginPath();
          ctx.moveTo(layer.points[0].x, layer.points[0].y);
          for (let i = 1; i < layer.points.length; i++) {
            ctx.lineTo(layer.points[i].x, layer.points[i].y);
          }
          ctx.stroke();
        }
        ctx.globalAlpha = 1.0;
      } else if (layer.type === "rect" && layer.x !== undefined && layer.y !== undefined && layer.x2 !== undefined && layer.y2 !== undefined) {
        ctx.strokeRect(layer.x, layer.y, layer.x2 - layer.x, layer.y2 - layer.y);
      } else if (layer.type === "circle" && layer.x !== undefined && layer.y !== undefined && layer.x2 !== undefined && layer.y2 !== undefined) {
        const radius = Math.sqrt(Math.pow(layer.x2 - layer.x, 2) + Math.pow(layer.y2 - layer.y, 2));
        ctx.beginPath();
        ctx.arc(layer.x, layer.y, radius, 0, 2 * Math.PI);
        ctx.stroke();
      } else if (layer.type === "arrow" && layer.x !== undefined && layer.y !== undefined && layer.x2 !== undefined && layer.y2 !== undefined) {
        const headlen = 15;
        const dx = layer.x2 - layer.x;
        const dy = layer.y2 - layer.y;
        const angle = Math.atan2(dy, dx);
        ctx.beginPath();
        ctx.moveTo(layer.x, layer.y);
        ctx.lineTo(layer.x2, layer.y2);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(layer.x2, layer.y2);
        ctx.lineTo(layer.x2 - headlen * Math.cos(angle - Math.PI / 6), layer.y2 - headlen * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(layer.x2 - headlen * Math.cos(angle + Math.PI / 6), layer.y2 - headlen * Math.sin(angle + Math.PI / 6));
        ctx.closePath();
        ctx.fill();
      } else if (layer.type === "text" && layer.text && layer.x !== undefined && layer.y !== undefined) {
        ctx.font = `bold ${layer.width * 5}px sans-serif`;
        ctx.fillText(layer.text, layer.x, layer.y);
      }
    });
  };

  useEffect(() => {
    redrawCanvas();
  }, [layers, bgImage]);

  // Handle Mouse Canvas Drawing
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (selectedTool === "text") {
      setTextPos({ x, y });
      return;
    }

    setIsDrawing(true);
    setStartPos({ x, y });
    setCurrentPath([{ x, y }]);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (selectedTool === "pen" || selectedTool === "highlighter") {
      setCurrentPath((prev) => [...prev, { x, y }]);
    }
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (!canvas || !startPos) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    let newLayer: ImageAnnotationLayer | null = null;

    if (selectedTool === "pen" || selectedTool === "highlighter") {
      newLayer = {
        id: "layer_" + Date.now(),
        type: selectedTool,
        points: [...currentPath, { x, y }],
        color,
        width: selectedTool === "highlighter" ? strokeWidth * 4 : strokeWidth,
      };
    } else if (selectedTool === "rect") {
      newLayer = {
        id: "layer_" + Date.now(),
        type: "rect",
        x: startPos.x,
        y: startPos.y,
        x2: x,
        y2: y,
        color,
        width: strokeWidth,
      };
    } else if (selectedTool === "circle") {
      newLayer = {
        id: "layer_" + Date.now(),
        type: "circle",
        x: startPos.x,
        y: startPos.y,
        x2: x,
        y2: y,
        color,
        width: strokeWidth,
      };
    } else if (selectedTool === "arrow") {
      newLayer = {
        id: "layer_" + Date.now(),
        type: "arrow",
        x: startPos.x,
        y: startPos.y,
        x2: x,
        y2: y,
        color,
        width: strokeWidth,
      };
    }

    if (newLayer) {
      const updated = [...layers, newLayer];
      setLayers(updated);
      setHistory((prev) => [...prev.slice(0, historyIndex + 1), updated]);
      setHistoryIndex((prev) => prev + 1);
    }
  };

  const handleAddTextLayer = () => {
    if (!textInputVal.trim() || !textPos) return;
    const newLayer: ImageAnnotationLayer = {
      id: "layer_" + Date.now(),
      type: "text",
      text: textInputVal.trim(),
      x: textPos.x,
      y: textPos.y,
      color,
      width: strokeWidth,
    };
    const updated = [...layers, newLayer];
    setLayers(updated);
    setTextPos(null);
    setTextInputVal("");
  };

  // Image File Upload
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setBgImage(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Gemini AI Image Generation
  const handleGeminiGenerateImage = async () => {
    if (!aiImagePrompt.trim()) return;
    setIsAiGenerating(true);
    try {
      const res = await fetch("/api/gemini/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: aiImagePrompt, base64Image: bgImage }),
      });
      const data = await res.json();
      if (data.imageUrl) {
        setBgImage(data.imageUrl);
        setAiImagePrompt("");
      }
    } catch (err) {
      console.error("Erro na imagem Gemini:", err);
    } finally {
      setIsAiGenerating(false);
    }
  };

  const handleSave = () => {
    const canvas = canvasRef.current;
    const exportedBase64 = canvas ? canvas.toDataURL("image/png") : "";

    const newNote: Note = {
      id: note ? note.id : "canvas_note_" + Date.now(),
      title: title || "Anotação Canvas",
      content: `<p>Anotação visual vetorial com ${layers.length} camadas e marcações de revisão.</p>`,
      type: "canvas",
      color: "purple",
      tags: ["Canvas", "Design", "Anotação"],
      pinned: note ? note.pinned : false,
      archived: false,
      trashed: false,
      createdAt: note ? note.createdAt : new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      imageAnnotation: {
        base64Image: exportedBase64,
        layers,
        width: 700,
        height: 450,
      },
    };
    onSaveAsNote(newNote);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm sm:p-6">
      <div className="relative flex h-full max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-950">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-purple-500/10 p-2 text-purple-600 dark:text-purple-400">
              <PenTool className="h-6 w-6" />
            </span>
            <div>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="bg-transparent font-bold text-zinc-900 outline-none dark:text-zinc-100 text-base"
              />
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Anotação visual sobre imagens com camada de desenho libre e formas
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

        {/* Drawing Tools Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-200 bg-zinc-50 px-6 py-2.5 dark:border-zinc-800 dark:bg-zinc-900/80">
          {/* Tools selector */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setSelectedTool("pen")}
              className={`rounded-xl p-2 transition-all ${
                selectedTool === "pen"
                  ? "bg-purple-600 text-white shadow-xs"
                  : "text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
              title="Caneta Lápis"
            >
              <PenTool className="h-4 w-4" />
            </button>
            <button
              onClick={() => setSelectedTool("highlighter")}
              className={`rounded-xl p-2 transition-all ${
                selectedTool === "highlighter"
                  ? "bg-purple-600 text-white shadow-xs"
                  : "text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
              title="Marca-Texto Relevo"
            >
              <Highlighter className="h-4 w-4" />
            </button>
            <button
              onClick={() => setSelectedTool("rect")}
              className={`rounded-xl p-2 transition-all ${
                selectedTool === "rect"
                  ? "bg-purple-600 text-white shadow-xs"
                  : "text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
              title="Retângulo"
            >
              <Square className="h-4 w-4" />
            </button>
            <button
              onClick={() => setSelectedTool("circle")}
              className={`rounded-xl p-2 transition-all ${
                selectedTool === "circle"
                  ? "bg-purple-600 text-white shadow-xs"
                  : "text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
              title="Círculo"
            >
              <Circle className="h-4 w-4" />
            </button>
            <button
              onClick={() => setSelectedTool("arrow")}
              className={`rounded-xl p-2 transition-all ${
                selectedTool === "arrow"
                  ? "bg-purple-600 text-white shadow-xs"
                  : "text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
              title="Seta Indicativa"
            >
              <MoveRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => setSelectedTool("text")}
              className={`rounded-xl p-2 transition-all ${
                selectedTool === "text"
                  ? "bg-purple-600 text-white shadow-xs"
                  : "text-zinc-700 hover:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
              title="Inserir Texto"
            >
              <Type className="h-4 w-4" />
            </button>
          </div>

          {/* Color Palette & Stroke Width */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              {["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#1e293b"].map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className={`h-5 w-5 rounded-full border border-white transition-all ${
                    color === c ? "ring-2 ring-purple-500 scale-110" : ""
                  }`}
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>

            <div className="h-4 w-px bg-zinc-300 dark:bg-zinc-700" />

            <input
              type="range"
              min={1}
              max={12}
              value={strokeWidth}
              onChange={(e) => setStrokeWidth(Number(e.target.value))}
              className="w-20 accent-purple-600"
              title="Espessura do traço"
            />
          </div>

          {/* Upload or Gemini Prompt */}
          <div className="flex items-center gap-2">
            <label className="flex cursor-pointer items-center gap-1.5 rounded-xl border border-zinc-200 bg-white px-3 py-1.5 text-xs font-semibold text-zinc-700 shadow-2xs hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
              <Upload className="h-3.5 w-3.5 text-purple-500" />
              <span>Upload Imagem</span>
              <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
            </label>
          </div>
        </div>

        {/* Gemini AI Background Generation Bar */}
        <div className="flex items-center gap-2 border-b border-purple-200 bg-purple-50/80 px-6 py-2 dark:border-purple-900/50 dark:bg-purple-950/40">
          <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400 animate-pulse" />
          <span className="text-xs font-bold text-purple-900 dark:text-purple-200">✨ Gerar/Editar Imagem com IA:</span>
          <input
            type="text"
            value={aiImagePrompt}
            onChange={(e) => setAiImagePrompt(e.target.value)}
            placeholder="Ex: 'Um mapa conceitual com nós azuis' ou 'Adicione notas adesivas amarelas...'"
            className="flex-1 rounded-xl border border-purple-200 bg-white px-3 py-1 text-xs text-zinc-900 outline-none dark:border-purple-800 dark:bg-zinc-900 dark:text-zinc-100"
          />
          <button
            disabled={isAiGenerating || !aiImagePrompt.trim()}
            onClick={handleGeminiGenerateImage}
            className="rounded-xl bg-purple-600 px-3 py-1 text-xs font-bold text-white hover:bg-purple-700 disabled:opacity-50"
          >
            {isAiGenerating ? "Gerando..." : "Criar Fundo"}
          </button>
        </div>

        {/* Main Canvas Area */}
        <div className="relative flex flex-1 items-center justify-center overflow-auto p-6 bg-zinc-100/60 dark:bg-zinc-900/60">
          <canvas
            ref={canvasRef}
            width={720}
            height={420}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            className="rounded-2xl border border-zinc-300 bg-white shadow-lg dark:border-zinc-700 cursor-crosshair"
          />

          {/* Text Input Overlay popup */}
          {textPos && (
            <div
              className="absolute z-20 flex items-center gap-1 rounded-xl border border-purple-300 bg-white p-2 shadow-xl dark:border-purple-800 dark:bg-zinc-900"
              style={{ top: textPos.y + 20, left: textPos.x + 20 }}
            >
              <input
                type="text"
                autoFocus
                value={textInputVal}
                onChange={(e) => setTextInputVal(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddTextLayer()}
                placeholder="Insira seu texto..."
                className="w-48 rounded-lg border border-zinc-200 bg-zinc-50 px-2 py-1 text-xs text-zinc-900 outline-none dark:border-zinc-800 dark:bg-zinc-800 dark:text-zinc-100"
              />
              <button
                onClick={handleAddTextLayer}
                className="rounded-lg bg-purple-600 px-2 py-1 text-xs font-bold text-white hover:bg-purple-700"
              >
                OK
              </button>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <p className="text-xs text-zinc-400">
            A imagem anotada é preservada no KeepDocs com suporte a edição de camadas.
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
              className="flex items-center gap-2 rounded-xl bg-purple-600 px-5 py-2 text-xs font-bold text-white shadow-md shadow-purple-600/20 hover:bg-purple-700"
            >
              <Check className="h-4 w-4" />
              <span>Salvar Anotação Canvas</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
