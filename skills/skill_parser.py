"""Motor de descoberta, parsing e injeção dinâmica de habilidades (SKILL.md)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from shared.logger import get_logger
from skills.skill_healthcheck import STOPWORDS, SkillHealthChecker

logger = get_logger("SkillParser")

try:
    import yaml
except ImportError:
    yaml = None


class SkillParser:
    """Carregador e parser de habilidades modulares com auditoria contínua de integridade."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or (Path(__file__).resolve().parent)
        self._skills_cache: dict[str, dict[str, Any]] = {}
        self.health_checker = SkillHealthChecker(skills_dir=self.skills_dir)
        self.reload_skills()

    def reload_skills(self) -> None:
        """Varre recursivamente o diretório de skills e mapeia os arquivos SKILL.md."""
        self._skills_cache.clear()
        if not self.skills_dir.exists():
            logger.warning(f"Diretório de skills não encontrado: {self.skills_dir}")
            return

        search_dirs = [self.skills_dir]
        agents_skills_dir = self.skills_dir.parent / ".agents" / "skills"
        if agents_skills_dir.exists() and agents_skills_dir != self.skills_dir:
            search_dirs.append(agents_skills_dir)

        seen_skills: set[str] = set()
        for sdir in search_dirs:
            for skill_path in sorted(sdir.glob("**/SKILL.md")):
                skill_name = skill_path.parent.name
                if skill_name in seen_skills:
                    continue
                seen_skills.add(skill_name)
                try:
                    content = skill_path.read_text(encoding="utf-8")
                    metadata, body = self._parse_frontmatter(content)
                    metadata["name"] = metadata.get("name", skill_name)
                    metadata["path"] = str(skill_path.resolve())

                    self._skills_cache[skill_name] = {
                        "metadata": metadata,
                        "body": body,
                        "full_content": content,
                    }
                    logger.debug(f"Habilidade carregada: {skill_name} (v{metadata.get('version', '1.0.0')})")
                except (OSError, ValueError) as e:
                    logger.error(f"Erro ao analisar skill {skill_path}: {e}")

        report = self.health_checker.audit_catalog()
        if report.get("is_healthy"):
            logger.info(f"Catálogo de Skills carregado e validado ({len(self._skills_cache)} skills ativas).")
        else:
            logger.warning(f"Catálogo carregado com {report.get('total_issues')} alerta(s) de integridade.")

    def audit_catalog(self) -> dict[str, Any]:
        """Executa auditoria sob demanda."""
        return self.health_checker.audit_catalog()

    @staticmethod
    def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
        """Extrai o frontmatter YAML e o corpo Markdown com fallback nativo."""
        frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
        match = frontmatter_pattern.match(content)
        if match:
            yaml_str = match.group(1)
            body = content[match.end() :]

            if yaml is not None:
                try:
                    metadata = yaml.safe_load(yaml_str) or {}
                    if not isinstance(metadata, dict):
                        raise TypeError("Frontmatter YAML deve produzir um dicionário de metadados.")
                    return metadata, body
                except (yaml.YAMLError, ValueError, TypeError) as e:
                    logger.debug(f"Frontmatter YAML com formato especial, usando fallback manual: {e}")

            meta: dict[str, Any] = {}
            current_list_key: str | None = None
            for line in yaml_str.splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith("#"):
                    continue
                if line_str.startswith("- ") and current_list_key:
                    item_val = line_str[2:].strip().strip("\"'")
                    if not isinstance(meta.get(current_list_key), list):
                        meta[current_list_key] = []
                    meta[current_list_key].append(item_val)
                    continue

                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    if not val:
                        meta[key] = []
                        current_list_key = key
                    else:
                        meta[key] = val
                        current_list_key = None
            return meta, body

        return {}, content

    def list_available_skills(self) -> list[dict[str, Any]]:
        """Retorna uma lista resumida de todas as habilidades para Progressive Disclosure."""
        return [
            {
                "id": skill_id,
                "name": data["metadata"].get("name", skill_id),
                "description": data["metadata"].get("description", "Sem descrição"),
                "version": data["metadata"].get("version", "1.0.0"),
                "triggers": data["metadata"].get("triggers", []),
            }
            for skill_id, data in self._skills_cache.items()
        ]

    def get_skill_full_content(self, skill_id: str) -> str | None:
        """Recupera o conteúdo completo de uma habilidade sob demanda."""
        skill = self._skills_cache.get(skill_id)
        if skill:
            return skill["full_content"]
        return None

    def get_skills_for_scope(self, scope_ids: list[str]) -> list[dict[str, Any]]:
        """Retorna os metadados das habilidades pertencentes a um subcatálogo específico de agente."""
        result = []
        for s_id in scope_ids:
            data = self._skills_cache.get(s_id)
            if data:
                result.append({
                    "id": s_id,
                    "name": data["metadata"].get("name", s_id),
                    "description": data["metadata"].get("description", "Sem descrição"),
                    "version": data["metadata"].get("version", "1.0.0"),
                    "triggers": data["metadata"].get("triggers", []),
                })
        return result

    def match_skills_by_query(
        self,
        query: str | None,
        max_matches: int = 3,
        allowed_skills: list[str] | None = None,
    ) -> list[str]:
        """Identifica habilidades relevantes para a mensagem com auto-ativação contextual e Top-K preventivo.

        Hubs de bundle (frontmatter has-sub-skill: true) são ignorados aqui.
        Se allowed_skills for informado, restringe a busca ao subcatálogo do agente.
        """
        if query is None:
            return []
        matched: list[str] = []
        query_lower = str(query).lower()
        query_words = set(re.findall(r"\w+", query_lower))

        candidate_items = self._skills_cache.items()
        if allowed_skills is not None:
            allowed_set = set(allowed_skills)
            candidate_items = [(k, v) for k, v in candidate_items if k in allowed_set]

        # Prioridade 1: Match exato por ID ou Nome
        for skill_id, data in candidate_items:
            meta = data["metadata"]
            if str(meta.get("has-sub-skill", "")).strip().lower() in ("true", "yes", "1"):
                continue
            name = str(meta.get("name", "")).lower()
            if (skill_id in query_lower or name in query_lower) and skill_id not in matched:
                matched.append(skill_id)
            if len(matched) >= max_matches:
                return matched

        # Prioridade 2: Match por Trigger completo
        for skill_id, data in candidate_items:
            if skill_id in matched:
                continue
            meta = data["metadata"]
            if str(meta.get("has-sub-skill", "")).strip().lower() in ("true", "yes", "1"):
                continue
            triggers = meta.get("triggers", [])
            if not isinstance(triggers, list):
                triggers = [triggers] if triggers else []
            if any(str(t).lower() in query_lower for t in triggers):
                matched.append(skill_id)
            if len(matched) >= max_matches:
                return matched

        # Prioridade 3: Intersecção de palavras-chave relevantes dos triggers
        for skill_id, data in candidate_items:
            if skill_id in matched:
                continue
            meta = data["metadata"]
            if str(meta.get("has-sub-skill", "")).strip().lower() in ("true", "yes", "1"):
                continue
            triggers = meta.get("triggers", [])
            if not isinstance(triggers, list):
                triggers = [triggers] if triggers else []
            all_trigger_words = set()
            for t in triggers:
                all_trigger_words.update(re.findall(r"\w+", str(t).lower()))

            relevant_trigger_words = {w for w in all_trigger_words if len(w) > 3 and w not in STOPWORDS}
            if relevant_trigger_words and len(query_words.intersection(relevant_trigger_words)) >= 1:
                matched.append(skill_id)
            if len(matched) >= max_matches:
                return matched

        # Prioridade 4: Busca por palavras-chave técnicas na descrição
        for skill_id, data in candidate_items:
            if skill_id in matched:
                continue
            meta = data["metadata"]
            if str(meta.get("has-sub-skill", "")).strip().lower() in ("true", "yes", "1"):
                continue
            desc = str(meta.get("description", "")).lower()
            desc_words = set(re.findall(r"\w+", desc))
            relevant_desc_words = {w for w in desc_words if len(w) > 3 and w not in STOPWORDS}
            if len(query_words.intersection(relevant_desc_words)) >= 2:
                matched.append(skill_id)
            if len(matched) >= max_matches:
                return matched

        return matched

    def get_catalog_summary_markdown(self) -> str:
        """Gera índice legível em Markdown com todas as habilidades disponíveis no catálogo."""
        lines = [
            "# Catálogo de Habilidades do Ecossistema",
            "",
            "| Habilidade | Versão | Descrição | Gatilhos |",
            "|---|---|---|---|",
        ]
        for skill_id, data in sorted(self._skills_cache.items()):
            meta = data.get("metadata", {})
            desc = meta.get("description", "Sem descrição").replace("\n", " ")[:80]
            ver = meta.get("version", "1.0.0")
            triggers = ", ".join(meta.get("triggers", [])[:3])
            lines.append(f"| `{skill_id}` | v{ver} | {desc} | {triggers} |")
        return "\n".join(lines)
