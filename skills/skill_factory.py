"""Fábrica de Habilidades (SkillFactory) — Criação, Padronização e Validação Pré-Save."""

import re
from pathlib import Path
from typing import Any

from shared.logger import get_logger

logger = get_logger("SkillFactory")

SKILL_TEMPLATE = """---
name: {name}
version: 1.0.0
description: {description}
triggers:
{triggers_yaml}
---

# {title} (`{name}`)

## 1. Diretrizes e Princípios
{principles}

## 2. Fluxo Operacional Passo a Passo
{workflow}

## 3. Formato de Saída Obrigatório
{output_format}

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
{negative_bounds}
"""


class SkillFactory:
    """Fábrica para gerar e registrar novas habilidades no catálogo governado."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or (Path(__file__).resolve().parent)

    def create_skill(
        self,
        name: str,
        description: str,
        category: str = "custom",
        triggers: list[str] | None = None,
        title: str | None = None,
        principles: str = "- Separar rigorosamente dados de instruções.\n- Respeitar tipagem e boas práticas.",
        workflow: str = "1. Analisar a entrada do usuário.\n2. Executar a transformação com zero placeholders.\n3. Validar a saída.",
        output_format: str = "Retornar resposta estruturada, código completo e comentários explicativos quando necessário.",
        negative_bounds: str = "- NUNCA utilizar placeholders ou código incompleto.\n- NUNCA executar ações destrutivas sem autorização explícita.",
    ) -> dict[str, Any]:
        """Gera, valida e salva um novo arquivo SKILL.md."""
        # 1. Validação do nome em kebab-case
        name_clean = name.strip().lower()
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name_clean):
            raise ValueError(f"O nome da skill ('{name}') deve usar apenas minúsculas e hífens (kebab-case).")

        # 2. Validação da descrição
        desc_clean = description.strip()
        if len(desc_clean) < 20:
            raise ValueError("A descrição deve conter no mínimo 20 caracteres detalhando objetivo e gatilhos.")

        # 3. Monta o diretório de destino
        bundle_dir = self.skills_dir / category
        target_dir = bundle_dir / name_clean if category != "." else self.skills_dir / name_clean
        target_dir.mkdir(parents=True, exist_ok=True)
        skill_file = target_dir / "SKILL.md"

        triggers_list = triggers or [name_clean.replace("-", " ")]
        triggers_yaml = "\n".join(f'  - "{t}"' for t in triggers_list)

        content = SKILL_TEMPLATE.format(
            name=name_clean,
            description=desc_clean,
            triggers_yaml=triggers_yaml,
            title=title or name_clean.replace("-", " ").title(),
            principles=principles.strip(),
            workflow=workflow.strip(),
            output_format=output_format.strip(),
            negative_bounds=negative_bounds.strip(),
        )

        skill_file.write_text(content, encoding="utf-8")
        logger.info(f"✨ Nova skill criada com sucesso: {skill_file.relative_to(self.skills_dir.parent).as_posix()}")

        return {
            "status": "success",
            "name": name_clean,
            "path": str(skill_file.resolve()),
            "category": category,
            "message": f"Skill '{name_clean}' registrada com sucesso no catálogo.",
        }
