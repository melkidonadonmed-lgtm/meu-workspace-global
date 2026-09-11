"""Script de teste unitário e validação do multi_tool_agent."""

import sys
from pathlib import Path

# Adiciona o diretório pai ao sys.path para importação
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from multi_tool_agent.agent import root_agent, calculate, convert_units, get_current_time


def test_agent_structure():
    print(f"--- 1. Validando Estrutura do Agente ---")
    print(f"Nome do agente: {root_agent.name}")
    print(f"Modelo configurado: {root_agent.model}")
    print(f"Quantidade de tools registradas: {len(root_agent.tools)}")
    assert root_agent.name == "multi_tool_agent"
    assert len(root_agent.tools) == 3
    print("[OK] Estrutura do root_agent validada com sucesso!")


def test_tools_locally():
    print(f"\n--- 2. Validando Execucao das Tools ---")
    
    # Teste 1: Cálculo
    calc_res = calculate("sqrt(256) + 14")
    print(f"Teste calculate('sqrt(256) + 14'): {calc_res}")
    assert calc_res["status"] == "success"
    assert calc_res["result"] == 30.0

    # Teste 2: Conversão de unidades
    conv_res = convert_units(100.0, "celsius", "fahrenheit")
    print(f"Teste convert_units(100, 'celsius', 'fahrenheit'): {conv_res}")
    assert conv_res["status"] == "success"
    assert conv_res["converted_value"] == 212.0

    # Teste 3: Data e Hora
    time_res = get_current_time("America/Sao_Paulo")
    print(f"Teste get_current_time('America/Sao_Paulo'): {time_res}")
    assert time_res["status"] == "success"
    assert "utc_iso" in time_res

    print("[OK] Todas as tools responderam perfeitamente!")


if __name__ == "__main__":
    test_agent_structure()
    test_tools_locally()
    print("\n[SUCESSO] Todos os testes do multi_tool_agent passaram 100%!")

