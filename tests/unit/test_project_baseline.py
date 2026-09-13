"""Testes unitários para o Baseline Mínimo Universal de Projetos e seu verificador."""

from pathlib import Path

from scripts.verify_project_baseline import BaselineVerifier

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def test_project_baseline_rule_exists():
    """Valida se o documento de regra canônica existe e tem as seções obrigatórias."""
    rule_file = WORKSPACE_ROOT / "rules" / "project_baseline.md"
    assert rule_file.is_file(), "Arquivo rules/project_baseline.md não encontrado."

    content = rule_file.read_text(encoding="utf-8")
    assert "## 1. Estrutura de Pastas (Formato Padrão)" in content
    assert "## 2. Premissas Base (Checklist dos 6 Pilares)" in content
    assert "## 3. Ordem Prática para Organização Rápida (Regra 80/20)" in content
    assert "A. Documentação Mínima" in content
    assert "B. Qualidade de Código" in content
    assert "C. Git & GitHub" in content
    assert "D. CI/CD" in content
    assert "E. Configuração & Segurança" in content
    assert "F. Operação & Manutenção" in content


def test_project_baseline_templates_pass_verification():
    """Valida se o template base em templates/project_baseline é 100% aprovado pelo verificador."""
    template_dir = WORKSPACE_ROOT / "templates" / "project_baseline"
    assert template_dir.is_dir(), "Diretório templates/project_baseline não encontrado."

    verifier = BaselineVerifier(template_dir)
    report = verifier.verify_all()

    assert report["passed"] is True, f"Template falhou na validação de baseline: {report}"
    assert report["score"] == 100, f"Score esperado era 100%, obtido: {report['score']}%"


def test_agents_md_and_gemini_md_contain_baseline():
    """Valida se AGENTS.md e GEMINI.md global registram o baseline de projetos."""
    agents_md = WORKSPACE_ROOT / "AGENTS.md"
    assert agents_md.is_file()
    agents_content = agents_md.read_text(encoding="utf-8")
    assert "Padrão Canônico Mínimo para Projetos" in agents_content

    global_gemini_md = Path(r"C:\Users\melki\.gemini\GEMINI.md")
    if global_gemini_md.is_file():
        gemini_content = global_gemini_md.read_text(encoding="utf-8")
        assert "Padrão Canônico Mínimo para Projetos" in gemini_content
