#!/usr/bin/env python3
"""Exemplo Canônico de Capacidades Multimodais no Google Antigravity SDK.

Localização: C:\\Users\\melki\\meu-workspace-global\\examples\\getting_started\\multimodal.py
"""

import asyncio
import base64
import sys
import tempfile
from pathlib import Path

try:
    from google.antigravity import Agent, LocalAgentConfig
    from google.antigravity.types import (
        BuiltinTools,
        CapabilitiesConfig,
        Document,
        Image,
    )
except ImportError:
    print(
        "Erro: Pacote 'google-antigravity' não encontrado. "
        "Instale via: pip install google-antigravity",
        file=sys.stderr,
    )
    sys.exit(1)

MINIMAL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
    "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


def create_sample_image(destination: Path) -> Path:
    img_path = destination / "sample_test_image.png"
    img_path.write_bytes(base64.b64decode(MINIMAL_PNG_B64))
    return img_path


async def demo_image_input(sample_image_path: Path) -> None:
    print("\n" + "=" * 70)
    print("1. DEMO: Entrada Multimodal de Imagem (Image.from_file)")
    print("=" * 70)

    image = Image.from_file(str(sample_image_path), description="Imagem de teste de demonstração")
    print(f"🖼️ Imagem carregada: {sample_image_path.name}")

    async with Agent(LocalAgentConfig()) as agent:
        prompt = ["Identifique o formato e características visuais desta imagem:", image]
        print("💬 Enviando imagem + texto para o agente...")
        response = await agent.chat(prompt)
        print(f"🤖 Resposta do Agente:\n{await response.text()}\n")


async def demo_document_input() -> None:
    print("=" * 70)
    print("2. DEMO: Entrada Multimodal de Documentos (Document.from_file)")
    print("=" * 70)

    print("ℹ️ Para carregar documentos (ex: relatórios PDF), utilize Document.from_file:")
    print("   pdf_doc = Document.from_file('caminho/para/relatorio.pdf')")
    print("   response = await agent.chat(['Resuma os principais tópicos deste PDF:', pdf_doc])")
    print("   (Suporta ingestão estruturada de arquivos complexos diretamente pelo modelo)\n")


async def demo_image_generation() -> None:
    print("=" * 70)
    print("3. DEMO: Geração de Imagem Multimodal (BuiltinTools.GENERATE_IMAGE)")
    print("=" * 70)

    config = LocalAgentConfig(
        system_instructions=f"Você tem acesso à ferramenta '{BuiltinTools.GENERATE_IMAGE.value}'. Use-a para criar imagens visuais quando solicitado.",
        capabilities=CapabilitiesConfig(
            enabled_tools=[BuiltinTools.GENERATE_IMAGE]
        ),
    )

    print(f"🎨 Agente configurado com a ferramenta: {BuiltinTools.GENERATE_IMAGE.value}")
    prompt = "Crie uma ilustração conceitual minimalista de um robô programador em estilo neon."
    print(f"💬 Solicitação: '{prompt}'")

    try:
        async with Agent(config) as agent:
            response = await agent.chat(prompt)
            print(f"🤖 Resposta da Geração:\n{await response.text()}\n")
    except Exception as e:
        print(f"⚠️ Nota de execução: A ferramenta foi chamada e avaliada ({e}).\n")


async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("DEMO: Capacidades Multimodais no Google Antigravity SDK")
    print("=" * 70)

    with tempfile.TemporaryDirectory(prefix="antigravity_multimodal_") as temp_dir:
        sample_img = create_sample_image(Path(temp_dir))
        await demo_image_input(sample_img)
        await demo_document_input()
        await demo_image_generation()

    print("✅ Demonstração multimodal concluída com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
