#!/usr/bin/env python3
"""Exemplo Canônico de Persistência de Conversa no Google Antigravity SDK.

Localização: C:\\Users\\melki\\meu-workspace-global\\examples\\getting_started\\persistence.py
"""

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

try:
    from google.antigravity import Agent, LocalAgentConfig
except ImportError:
    print(
        "Erro: Pacote 'google-antigravity' não encontrado. "
        "Instale via: pip install google-antigravity",
        file=sys.stderr,
    )
    sys.exit(1)


async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("DEMO: Persistência de Conversas no Google Antigravity SDK")
    print("=" * 70)

    temp_dir = tempfile.mkdtemp(prefix="antigravity_persistence_")
    save_dir = Path(temp_dir)
    print(f"📂 Diretório de persistência configurado: {save_dir}\n")

    conversation_id = None

    try:
        print("🔹 [Sessão 1] Inicializando agente com save_dir...")
        config_session1 = LocalAgentConfig(save_dir=str(save_dir))

        prompt_1 = (
            "Guarde esta informação na memória para consultas futuras:\n"
            "- Nome do Projeto: 'Antigravity Studio'\n"
            "- Código de Acesso: 'AGY-2026-X'\n"
            "- Cor Primária: 'Verde Esmeralda'\n"
            "Confirme que memorizou em uma frase curta em Português BR."
        )

        async with Agent(config_session1) as agent1:
            print(f"💬 [Sessão 1] Enviando dados para memorização...")
            response1 = await agent1.chat(prompt_1)
            print(f"🤖 [Sessão 1] Resposta: {await response1.text()}")

            conversation_id = agent1.conversation_id
            print(f"🔑 [Sessão 1] Conversation ID capturado: {conversation_id}")

        print("🛑 [Sessão 1] Sessão 1 encerrada e descarregada em disco.\n")

        print("🔹 [Sessão 2] Inicializando NOVO agente conectando ao conversation_id anterior...")
        config_session2 = LocalAgentConfig(
            conversation_id=conversation_id,
            save_dir=str(save_dir),
        )

        prompt_2 = (
            "Com base nas informações que lhe passei na mensagem anterior desta conversa, "
            "responda: qual é o Nome do Projeto, o Código de Acesso e a Cor Primária? "
            "Responda em Português BR."
        )

        async with Agent(config_session2) as agent2:
            print(f"💬 [Sessão 2] Perguntando sobre o contexto anterior...")
            response2 = await agent2.chat(prompt_2)
            print("-" * 70)
            print("🤖 [Sessão 2] Resposta Restaurada com Sucesso:")
            print(await response2.text())
            print("-" * 70)

        files_saved = list(save_dir.rglob("*"))
        print(f"\n📁 Arquivos de estado gravados em disco ({len(files_saved)} itens encontrados):")
        for f in files_saved[:5]:
            if f.is_file():
                print(f"   • {f.relative_to(save_dir)} ({f.stat().st_size} bytes)")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Limpeza: Diretório temporário removido com sucesso.")


if __name__ == "__main__":
    asyncio.run(main())
