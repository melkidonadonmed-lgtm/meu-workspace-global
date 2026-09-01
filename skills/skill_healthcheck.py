"""Motor de Auditoria Contínua e Integridade do Catálogo de Skills (SkillHealthChecker)."""

import re
import unicodedata
from pathlib import Path
from typing import Any

from shared.logger import get_logger

logger = get_logger("SkillHealthChecker")

STOPWORDS = {
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "em",
    "no",
    "na",
    "para",
    "com",
    "um",
    "uma",
    "o",
    "a",
    "os",
    "as",
    "ou",
    "ao",
    "que",
    "se",
    "por",
    "use",
    "quando",
    "skill",
    "agente",
    "ecossistema",
}


def _tokenize(text: str) -> set[str]:
    norm = "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )
    tokens = set(re.findall(r"[a-z0-9]+", norm))
    return {t for t in tokens if t not in STOPWORDS and len(t) > 2}


class SkillHealthChecker:
    """Auditor em tempo de execução para garantir conformidade e prevenir degradação do catálogo."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or (Path(__file__).resolve().parent)

    def parse_frontmatter(self, content: str) -> tuple[dict[str, str] | None, str | None]:
        """Extrai o frontmatter YAML."""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return None, "Frontmatter YAML delimitado por '---' ausente."

        data: dict[str, str] = {}
        current_key = None
        multiline = []
        for line in match.group(1).splitlines():
            trimmed = line.strip()
            if not trimmed or trimmed.startswith("#"):
                continue

            if ":" in line and not line.startswith((" ", "\t")):
                if current_key and multiline:
                    data[current_key] = " ".join(multiline).strip()
                    multiline = []
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if v in (">", "|", ""):
                    current_key = k
                else:
                    data[k] = v
                    current_key = None
            elif current_key and line.startswith((" ", "\t")):
                multiline.append(trimmed)

        if current_key and multiline:
            data[current_key] = " ".join(multiline).strip()

        return data, None

    def audit_catalog(self, redundancy_threshold: float = 0.5) -> dict[str, Any]:
        """Executa varredura completa do catálogo e retorna relatório estruturado."""
        if not self.skills_dir.exists():
            return {
                "status": "error",
                "error": f"Diretório não encontrado: {self.skills_dir}",
                "total_skills": 0,
            }

        catalog: dict[str, dict[str, str]] = {}
        syntax_failures: list[str] = []
        name_mismatches: list[str] = []
        missing_sections: list[str] = []

        skill_files = list(self.skills_dir.glob("**/SKILL.md"))

        for file_path in skill_files:
            rel_path = file_path.relative_to(self.skills_dir).as_posix()
            folder_name = file_path.parent.name
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:  # noqa: BLE001
                syntax_failures.append(f"{rel_path}: Erro ao ler arquivo ({e})")
                continue

            fm, err = self.parse_frontmatter(content)
            if err or not fm:
                syntax_failures.append(f"{rel_path}: {err}")
                continue

            name = fm.get("name", "")
            desc = fm.get("description", "")

            if not name:
                syntax_failures.append(f"{rel_path}: Atributo 'name' obrigatório ausente.")
            else:
                if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
                    syntax_failures.append(f"{rel_path}: 'name' ('{name}') não está em kebab-case.")
                if name != folder_name:
                    name_mismatches.append(f"{rel_path}: name='{name}' != pasta='{folder_name}'")

            if not desc or len(desc) < 20:
                syntax_failures.append(f"{rel_path}: 'description' ausente ou curta (<20 chars).")

            # Verifica seções recomendadas
            if not any(s in content for s in ["O que NÃO Fazer", "O que NÃO fazer", "Restrições", "Negative Bounds"]):
                missing_sections.append(f"{rel_path}: Seção de restrições ('O que NÃO Fazer') ausente.")

            catalog[rel_path] = {"name": name, "description": desc, "folder": folder_name}

        # Análise de redundâncias semânticas (Jaccard)
        redundancies: list[dict[str, Any]] = []
        keys = sorted(catalog.keys())
        for i, k1 in enumerate(keys):
            t1 = _tokenize(catalog[k1]["description"])
            for k2 in keys[i + 1 :]:
                t2 = _tokenize(catalog[k2]["description"])
                if not t1 or not t2:
                    continue
                score = len(t1 & t2) / len(t1 | t2)
                if score >= redundancy_threshold:
                    redundancies.append({
                        "skill_a": k1,
                        "skill_b": k2,
                        "similarity_score": round(score, 3),
                    })

        total_issues = len(syntax_failures) + len(name_mismatches)
        is_healthy = total_issues == 0

        report = {
            "status": "healthy" if is_healthy else "issues_detected",
            "total_skills": len(skill_files),
            "is_healthy": is_healthy,
            "total_issues": total_issues,
            "syntax_failures": syntax_failures,
            "name_mismatches": name_mismatches,
            "missing_sections_warnings": missing_sections,
            "semantic_redundancies": redundancies,
        }

        if is_healthy:
            logger.info(f"✅ Catálogo de Skills 100% íntegro ({len(skill_files)} skills auditadas).")
        else:
            logger.warning(
                f"⚠️ Auditoria de Skills detectou {total_issues} problema(s) em {len(skill_files)} skills."
            )

        return report
