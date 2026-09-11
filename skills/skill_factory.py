"""Fábrica de Habilidades (SkillFactory) — Criação, Padronização e Importação de Skills."""

from __future__ import annotations

import re
import unicodedata
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


def slugify_skill_name(name: str) -> str:
    """Converte qualquer string para kebab-case estrito (sem acentos, minúsculas, hífens únicos)."""
    norm = "".join(
        c for c in unicodedata.normalize("NFD", name.lower()) if unicodedata.category(c) != "Mn"
    )
    clean = re.sub(r"[^a-z0-9]+", "-", norm).strip("-")
    clean = re.sub(r"-+", "-", clean)
    return clean or "custom-skill"


class SkillFactory:
    """Fábrica para gerar, importar e registrar novas habilidades no catálogo governado."""

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
        """Gera, valida e salva um novo arquivo SKILL.md estruturado."""
        # Validação estrita de formato e governança
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            raise ValueError(f"O nome da skill deve estar em kebab-case: '{name}'")

        desc_clean = description.strip()
        if len(desc_clean) < 20:
            raise ValueError("A descrição da skill deve ter no mínimo 20 caracteres.")

        name_clean = name
        category_clean = slugify_skill_name(category) or "custom"
        bundle_dir = self.skills_dir / category_clean if category_clean != "." else self.skills_dir
        target_dir = bundle_dir / name_clean
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
        logger.info(f"✨ Nova skill criada com sucesso em: {skill_file.as_posix()}")

        return {
            "status": "success",
            "name": name_clean,
            "path": str(skill_file.resolve()),
            "category": category_clean,
            "message": f"Skill '{name_clean}' registrada com sucesso no catálogo em {skill_file.name}.",
        }

    def import_skill_from_text(self, raw_markdown: str, category: str = "custom") -> dict[str, Any]:
        """Importa diretamente uma skill a partir de Markdown bruto fornecido pelo usuário."""
        # Extrai frontmatter se existir
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_markdown.strip(), re.DOTALL)
        if fm_match:
            yaml_block = fm_match.group(1)
            body = fm_match.group(2)
            name_match = re.search(r"^name:\s*(.+)$", yaml_block, re.MULTILINE)
            desc_match = re.search(r"^description:\s*(.+)$", yaml_block, re.MULTILINE)

            name = name_match.group(1).strip().strip("\"'") if name_match else "skill-importada"
            desc = desc_match.group(1).strip().strip("\"'") if desc_match else "Habilidade importada diretamente para o catálogo governado."
            name_clean = slugify_skill_name(name)

            if len(desc) < 20:
                desc = f"Habilidade governada {name_clean} importada a partir de instrução Markdown do usuário."

            category_clean = slugify_skill_name(category) or "custom"
            bundle_dir = self.skills_dir / category_clean if category_clean != "." else self.skills_dir
            target_dir = bundle_dir / name_clean
            target_dir.mkdir(parents=True, exist_ok=True)
            skill_file = target_dir / "SKILL.md"

            # Garante que o name no YAML coincide estritamente com a pasta
            corrected_yaml = re.sub(r"^name:\s*.+$", f"name: {name_clean}", yaml_block, flags=re.MULTILINE)
            if not re.search(r"^description:\s*.+$", corrected_yaml, flags=re.MULTILINE):
                corrected_yaml += f"\ndescription: {desc}"

            # Garante que a seção obrigatória de restrições ("O que NÃO Fazer") esteja presente
            required_sections = ["O que NÃO Fazer", "O que NÃO fazer", "Restrições", "Negative Bounds", "What NOT to Do"]
            if not any(s in body for s in required_sections):
                body = body.rstrip() + "\n\n## 4. Zonas de Não-Ação & O que NÃO Fazer\n- NUNCA utilizar placeholders ou código incompleto.\n- NUNCA executar ações destrutivas sem autorização explícita.\n"

            final_content = f"---\n{corrected_yaml.strip()}\n---\n\n{body.strip()}\n"
            skill_file.write_text(final_content, encoding="utf-8")

            return {
                "status": "success",
                "name": name_clean,
                "path": str(skill_file.resolve()),
                "category": category_clean,
                "message": f"Skill '{name_clean}' importada e gravada com sucesso em {skill_file.as_posix()}.",
            }

        # Se não tiver frontmatter, extrai título ou primeira linha
        title_match = re.search(r"^#\s+(.+)$", raw_markdown, re.MULTILINE)
        raw_name = title_match.group(1).strip() if title_match else "nova-skill"
        name_clean = slugify_skill_name(raw_name)

        desc = f"Habilidade importada {name_clean} para suporte a demandas técnicas especializadas no ecossistema."
        return self.create_skill(
            name=name_clean,
            description=desc,
            category=category,
            workflow=raw_markdown[:500] or "1. Executar comandos com base na instrução fornecida.",
        )

    def create_skill_from_text(self, raw_input: str, default_category: str = "custom") -> dict[str, Any]:
        """Alias para import_skill_from_text garantindo interoperabilidade total."""
        return self.import_skill_from_text(raw_input, category=default_category)

    def generate_skill(
        self,
        name: str,
        bundle: str,
        description: str,
        triggers: list[str] | None = None,
        when_to_use: str = "",
        when_not_to_use: str = "",
        rules: list[str] | None = None,
    ) -> dict[str, Any]:
        """Gera uma skill a partir de pesquisa ou diagnóstico de gap operacional."""
        principles = when_to_use.strip() or "- Aplicar a habilidade apenas dentro do escopo técnico pesquisado."
        if when_not_to_use.strip():
            principles += f"\n- **Quando NÃO usar:** {when_not_to_use.strip()}"

        rules_list = rules or ["Validar entradas e saídas antes de qualquer execução."]
        negative_bounds = "\n".join(f"- {r}" for r in rules_list)
        negative_bounds += "\n- NUNCA tratar este rascunho como definitivo sem validação de testes."

        return self.create_skill(
            name=name,
            description=description,
            category=bundle,
            triggers=triggers,
            principles=principles,
            negative_bounds=negative_bounds,
        )
