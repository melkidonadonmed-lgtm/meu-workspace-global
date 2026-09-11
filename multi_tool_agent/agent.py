import os
import math
import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from google.adk.agents import Agent

# Garante o carregamento do .env do agente ou da raiz do workspace
load_dotenv()

# =====================================================================
# 🛠️ Ferramentas (Function Tools do Google ADK)
# Regras canônicas ADK:
# 1. Type hints obrigatórios em todos os parâmetros.
# 2. Sem valores padrão (default values) nos parâmetros para o schema do LLM.
# 3. Docstrings descritivas com blocos Args / Returns para orientação do modelo.
# 4. Retorno estruturado em dict serializável em JSON.
# =====================================================================

def calculate(expression: str) -> Dict[str, Any]:
    """Calcula com segurança expressões matemáticas e aritméticas básicas.

    Args:
        expression: Expressão matemática a ser calculada (ex: '15 * 4', 'sqrt(144) + 10', 'pow(2, 8)').

    Returns:
        Dicionário com o status da operação e o resultado numérico calculado.
    """
    allowed_names = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "abs": abs,
        "round": round,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        # Avaliação segura sem acesso a builtins
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return {
            "status": "success",
            "expression": expression,
            "result": float(result) if isinstance(result, (int, float)) else result,
        }
    except Exception as exc:
        return {
            "status": "error",
            "expression": expression,
            "message": f"Erro na avaliação matemática: {str(exc)}",
        }


def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Converte valores entre unidades de temperatura ou unidades de comprimento.

    Args:
        value: Valor numérico da grandeza a ser convertida.
        from_unit: Unidade de origem ('celsius', 'fahrenheit', 'km', 'miles', 'meters', 'feet').
        to_unit: Unidade de destino ('celsius', 'fahrenheit', 'km', 'miles', 'meters', 'feet').

    Returns:
        Dicionário com o valor original, unidade de destino e o resultado numérico convertido.
    """
    f = from_unit.lower().strip()
    t = to_unit.lower().strip()

    # Conversão de Temperatura
    if f == "celsius" and t == "fahrenheit":
        converted = (value * 9 / 5) + 32
        return {"status": "success", "original_value": value, "converted_value": round(converted, 2), "unit": t}
    if f == "fahrenheit" and t == "celsius":
        converted = (value - 32) * 5 / 9
        return {"status": "success", "original_value": value, "converted_value": round(converted, 2), "unit": t}

    # Conversão de Comprimento / Distância (normalizado em metros)
    dist_to_meters = {
        "meters": 1.0,
        "km": 1000.0,
        "miles": 1609.344,
        "feet": 0.3048,
    }
    if f in dist_to_meters and t in dist_to_meters:
        meters = value * dist_to_meters[f]
        converted = meters / dist_to_meters[t]
        return {"status": "success", "original_value": value, "converted_value": round(converted, 4), "unit": t}

    return {
        "status": "error",
        "message": f"Conversão incompatível ou não suportada de '{from_unit}' para '{to_unit}'.",
    }


def get_current_time(timezone_name: str) -> Dict[str, Any]:
    """Obtém a data e o horário atual no fuso horário informado ou em UTC.

    Args:
        timezone_name: Nome do fuso ou região horária desejada ('UTC', 'America/Sao_Paulo', 'GMT').

    Returns:
        Dicionário com carimbo ISO, data/hora formatada e o fuso horário requisitado.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "status": "success",
        "utc_iso": now.isoformat(),
        "formatted_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "timezone_requested": timezone_name,
    }

# =====================================================================
# 🤖 Definição Canônica do Root Agent
# =====================================================================

root_agent = Agent(
    name="multi_tool_agent",
    model=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "Você é um assistente analítico multi-ferramentas de alta precisão. "
        "Sempre utilize as ferramentas disponíveis quando o usuário solicitar cálculos matemáticos, "
        "conversão de unidades métricas/imperiais ou consulta de horário atual. "
        "Explique os passos com clareza e responda sempre em Português BR."
    ),
    description="Agente multi-ferramentas especializado em cálculos aritméticos, conversões de medidas e data/hora.",
    tools=[calculate, convert_units, get_current_time],
)
