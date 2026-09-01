package workflow

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"customer-issue-reviewer/pkg/models"
	"customer-issue-reviewer/pkg/store"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/agent/workflowagent"
	"google.golang.org/adk/v2/model"
	"google.golang.org/adk/v2/workflow"
)

// IssuesPayload representa o pacote de chamados passado entre os nós do workflow.
type IssuesPayload struct {
	Issues        []models.Issue `json:"issues"`
	FilterSummary string         `json:"filter_summary"`
}

// BuildCustomerReviewerWorkflow constrói o workflow de agentes ADK Go v2.
func BuildCustomerReviewerWorkflow(ctx context.Context, llm model.LLM) (agent.Agent, error) {
	// 1. Nó de Função: Carrega e formata os tickets do repositório
	loadIssuesFn := func(_ agent.Context, query string) (string, error) {
		issues := store.GetMockIssues()
		var sb strings.Builder
		sb.WriteString("### Lista de Chamados de Clientes Recentes:\n\n")
		for _, iss := range issues {
			sb.WriteString(fmt.Sprintf(
				"- **[%s] (%s)** %s (Cliente: %s | Módulo: %s)\n  *Descrição:* %s\n\n",
				iss.ID, iss.Severity, iss.Title, iss.CustomerName, iss.Module, iss.Description,
			))
		}
		return sb.String(), nil
	}

	loadIssuesNode := workflow.NewFunctionNode("load_customer_issues", loadIssuesFn, workflow.NodeConfig{})

	// 2. Agente Especialista: Análise e Diagnóstico de Causa Raiz
	analyzerAgent, err := llmagent.New(llmagent.Config{
		Name:        "issue_analyzer_agent",
		Model:       llm,
		Description: "Analisa chamados de clientes, detecta padrões de causa raiz, severidade e urgência.",
		Instruction: `Você é um Engenheiro Sênior de Confiabilidade e Suporte (SRE/Tech Lead).
Analise a lista de chamados fornecida:
1. Agrupe os problemas por módulo e severidade.
2. Identifique as causas raiz prováveis de cada incidente.
3. Destaque quais problemas têm impacto financeiro ou bloqueio de usuários.
4. Escreva uma análise técnica clara em Português BR.`,
	})
	if err != nil {
		return nil, fmt.Errorf("falha ao criar issue_analyzer_agent: %w", err)
	}

	analyzerNode, err := workflow.NewAgentNode(analyzerAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("falha ao criar analyzerNode: %w", err)
	}

	// 3. Agente Especialista: Gerador de Relatório Executivo
	reportAgent, err := llmagent.New(llmagent.Config{
		Name:        "executive_report_agent",
		Model:       llm,
		Description: "Gera um relatório executivo final em Markdown com métricas, resumo e plano de ação.",
		Instruction: `Você é um Diretor de Engenharia de Produto (VP of Engineering).
Com base na análise técnica recebida, formate um Relatório Executivo de Incidentes e Chamados de Clientes em Markdown.
O relatório DEVE conter as seguintes seções obrigatórias:
# 📊 Relatório Executivo de Revisão de Chamados de Clientes

## 1. 📌 Resumo Executivo & Métricas Chave
- Total de Chamados Analisados
- Distribuição por Severidade (Críticos, Altos, Médios, Baixos)
- Principais Módulos Afetados

## 2. 🚨 Incidentes Críticos & Bloqueios Imediatos
- Detalhamento dos chamados críticos e clientes impactados.

## 3. 🔍 Análise de Causa Raiz & Padrões Sistêmicos
- Pontos de fragilidade identificados na arquitetura ou processos.

## 4. 🎯 Plano de Ação Recomendado (Próximos Passos)
- Ações Imediatas (Hotfixes / Mitigações)
- Ações Preventivas de Médio Prazo (Refatoração / Monitoramento)

Escreva em tom profissional, assertivo e em Português BR.`,
	})
	if err != nil {
		return nil, fmt.Errorf("falha ao criar executive_report_agent: %w", err)
	}

	reportNode, err := workflow.NewAgentNode(reportAgent, workflow.NodeConfig{})
	if err != nil {
		return nil, fmt.Errorf("falha ao criar reportNode: %w", err)
	}

	// 4. Cria o Agente de Workflow conectando a cadeia de nós
	edges := workflow.Chain(workflow.Start, loadIssuesNode, analyzerNode, reportNode)

	workflowRoot, err := workflowagent.New(workflowagent.Config{
		Name:        "customer_issue_reviewer_pipeline",
		Description: "Pipeline de agentes ADK Go para revisão de chamados de clientes e síntese de relatórios.",
		Edges:       edges,
		SubAgents:   []agent.Agent{analyzerAgent, reportAgent},
	})
	if err != nil {
		return nil, fmt.Errorf("falha ao criar workflowagent: %w", err)
	}

	return workflowRoot, nil
}

// GenerateDirectReportOffline gera o relatório offline formatado para fallback e testes locais determinísticos.
func GenerateDirectReportOffline(issues []models.Issue) *models.ExecutiveReport {
	report := &models.ExecutiveReport{
		Title:             "Relatório Executivo de Revisão de Chamados de Clientes (Modo Local/Offline)",
		TotalIssues:       len(issues),
		CategoryBreakdown: make(map[string]int),
		TopActionItems: []string{
			"Corrigir o processamento de webhooks de confirmação do PIX imediatamente (Módulo Payments).",
			"Resolver loop de redirecionamento OAuth no SSO Google após renovação de certificados (Módulo Auth).",
			"Aumentar timeout e implementar paginação assíncrona na exportação de relatórios em CSV (Módulo Reporting).",
			"Ajustar fuso horário padrão para America/Sao_Paulo nos agendamentos (Módulo Scheduling).",
			"Adicionar validação clara de tamanho máximo de arquivo (5MB) na UI de upload (Módulo Storage).",
		},
	}

	for _, iss := range issues {
		report.CategoryBreakdown[iss.Module]++
		switch iss.Severity {
		case models.SeverityCritical:
			report.CriticalCount++
		case models.SeverityHigh:
			report.HighCount++
		case models.SeverityMedium:
			report.MediumCount++
		case models.SeverityLow:
			report.LowCount++
		}

		report.Analyses = append(report.Analyses, models.IssueAnalysis{
			IssueID:           iss.ID,
			Category:          iss.Module,
			RootCauseSummary:  iss.Description,
			ImpactScore:       mapImpact(iss.Severity),
			Urgency:           mapUrgency(iss.Severity),
			RecommendedAction: fmt.Sprintf("Investigar componente %s para resolver '%s'", iss.Module, iss.Title),
		})
	}

	return report
}

func mapImpact(sev models.SeverityLevel) int {
	switch sev {
	case models.SeverityCritical:
		return 10
	case models.SeverityHigh:
		return 8
	case models.SeverityMedium:
		return 5
	default:
		return 2
	}
}

func mapUrgency(sev models.SeverityLevel) string {
	switch sev {
	case models.SeverityCritical:
		return "Imediata (SLA < 2h)"
	case models.SeverityHigh:
		return "Alta (SLA < 12h)"
	case models.SeverityMedium:
		return "Média (Próxima Sprint)"
	default:
		return "Baixa (Backlog)"
	}
}

// ToJSON serializa qualquer struct de relatório em JSON identado.
func ToJSON(v any) string {
	b, _ := json.MarshalIndent(v, "", "  ")
	return string(b)
}
