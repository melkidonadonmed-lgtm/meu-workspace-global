"""Motor de descoberta, parsing e injeção dinâmica de habilidades (SKILL.md)."""

import re
from pathlib import Path
from typing import Any

from shared.logger import get_logger

logger = get_logger("SkillParser")

try:
    import yaml
except ImportError:
    yaml = None  # Fallback seguro para parsing manual de frontmatter


class SkillParser:
    """Carregador e parser de habilidades modulares alinhado ao padrão Antigravity Customizations."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or (Path(__file__).parent)
        self._skills_cache: dict[str, dict[str, Any]] = {}
        self.reload_skills()

    def reload_skills(self) -> None:
        """Varre o diretório de skills e mapeia os arquivos SKILL.md."""
        self._skills_cache.clear()
        if not self.skills_dir.exists():
            logger.warning(f"Diretório de skills não encontrado: {self.skills_dir}")
            return

        for skill_path in self.skills_dir.glob("*/SKILL.md"):
            skill_name = skill_path.parent.name
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
                logger.info(f"Habilidade carregada: {skill_name} (v{metadata.get('version', '1.0.0')})")
            except (OSError, ValueError) as e:
                logger.error(f"Erro ao analisar skill {skill_path}: {e}")

    @staticmethod
    def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
        """Extrai o frontmatter YAML e o corpo Markdown com fallback nativo."""
        frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
        match = frontmatter_pattern.match(content)
        if match:
            yaml_str = match.group(1)
            body = content[match.end():]
            
            if yaml is not None:
                try:
                    metadata = yaml.safe_load(yaml_str) or {}
                    return metadata, body
                except yaml.YAMLError as e:
                    logger.debug(f"Frontmatter YAML inválido, usando fallback manual: {e}")
            
            # Fallback nativo simples para parsing de chave-valor e listas
            meta: dict[str, Any] = {}
            current_list_key = None
            for line in yaml_str.splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith("#"):
                    continue
                if line_str.startswith("- ") and current_list_key:
                    item_val = line_str[2:].strip().strip("\"'")
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

    def match_skills_by_query(self, query: str) -> list[str]:
        """Identifica habilidades relevantes para a mensagem do usuário com base em palavras-chave e triggers."""
        matched = []
        query_lower = query.lower()
        query_words = set(re.findall(r"\w+", query_lower))

        for skill_id, data in self._skills_cache.items():
            meta = data["metadata"]
            triggers = meta.get("triggers", [])
            name = str(meta.get("name", "")).lower()

            # 1. Match exato de ID ou nome da skill
            if skill_id in query_lower or name in query_lower:
                matched.append(skill_id)
                continue

            # 2. Match por frase do trigger
            if any(str(t).lower() in query_lower for t in triggers):
                matched.append(skill_id)
                continue

            # 3. Match por interseção semântica de palavras-chave dos triggers/descrição
            all_trigger_words = set()
            for t in triggers:
                all_trigger_words.update(re.findall(r"\w+", str(t).lower()))
            
            # Palavras relevantes ignorando stopwords curtas
            relevant_trigger_words = {w for w in all_trigger_words if len(w) > 3}
            if relevant_trigger_words and len(query_words.intersection(relevant_trigger_words)) >= 1:
                matched.append(skill_id)
                continue

        return matched
