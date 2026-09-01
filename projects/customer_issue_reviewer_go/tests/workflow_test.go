package tests

import (
	"testing"

	"customer-issue-reviewer/pkg/models"
	"customer-issue-reviewer/pkg/store"
	"customer-issue-reviewer/pkg/workflow"
)

func TestMockIssuesData(t *testing.T) {
	issues := store.GetMockIssues()
	if len(issues) == 0 {
		t.Fatalf("Esperava pelo menos 1 chamado simulado, mas obteve 0")
	}

	for _, iss := range issues {
		if iss.ID == "" {
			t.Errorf("ID do chamado não pode ser vazio")
		}
		if iss.Title == "" {
			t.Errorf("Título do chamado %s não pode ser vazio", iss.ID)
		}
		if iss.Module == "" {
			t.Errorf("Módulo do chamado %s não pode ser vazio", iss.ID)
		}
		if iss.Severity == "" {
			t.Errorf("Severidade do chamado %s não pode ser vazia", iss.ID)
		}
	}
}

func TestGenerateDirectReportOffline(t *testing.T) {
	issues := store.GetMockIssues()
	report := workflow.GenerateDirectReportOffline(issues)

	if report.TotalIssues != len(issues) {
		t.Errorf("Total de chamados esperado: %d, obtido: %d", len(issues), report.TotalIssues)
	}

	if report.CriticalCount != 2 {
		t.Errorf("Esperava 2 chamados críticos, obteve %d", report.CriticalCount)
	}

	if report.HighCount != 1 {
		t.Errorf("Esperava 1 chamado de alta severidade, obteve %d", report.HighCount)
	}

	if report.CategoryBreakdown["Payments"] != 1 {
		t.Errorf("Esperava 1 chamado no módulo Payments, obteve %d", report.CategoryBreakdown["Payments"])
	}

	if report.CategoryBreakdown["Auth"] != 1 {
		t.Errorf("Esperava 1 chamado no módulo Auth, obteve %d", report.CategoryBreakdown["Auth"])
	}

	if len(report.TopActionItems) == 0 {
		t.Errorf("Esperava lista de planos de ação preenchida")
	}

	if len(report.Analyses) != len(issues) {
		t.Errorf("Esperava %d análises de chamados, obteve %d", len(issues), len(report.Analyses))
	}
}

func TestModelMapping(t *testing.T) {
	issues := []models.Issue{
		{
			ID:           "TEST-01",
			CustomerName: "Cliente Teste",
			Title:        "Bug crítico teste",
			Description:  "Descrição detalhada",
			Severity:     models.SeverityCritical,
			Module:       "Core",
		},
	}

	report := workflow.GenerateDirectReportOffline(issues)
	if len(report.Analyses) != 1 {
		t.Fatalf("Esperava 1 análise, obteve %d", len(report.Analyses))
	}

	analysis := report.Analyses[0]
	if analysis.ImpactScore != 10 {
		t.Errorf("Score de impacto para crítico esperado 10, obteve %d", analysis.ImpactScore)
	}

	if analysis.Urgency != "Imediata (SLA < 2h)" {
		t.Errorf("Urgência esperada 'Imediata (SLA < 2h)', obteve '%s'", analysis.Urgency)
	}
}
