package models

import "time"

// SeverityLevel representa o nível de severidade do chamado.
type SeverityLevel string

const (
	SeverityCritical SeverityLevel = "Critical"
	SeverityHigh     SeverityLevel = "High"
	SeverityMedium   SeverityLevel = "Medium"
	SeverityLow      SeverityLevel = "Low"
)

// Issue representa um chamado/reclamação de cliente.
type Issue struct {
	ID           string        `json:"id"`
	CustomerName string        `json:"customer_name"`
	Title        string        `json:"title"`
	Description  string        `json:"description"`
	Severity     SeverityLevel `json:"severity"`
	Module       string        `json:"module"`
	CreatedAt    time.Time     `json:"created_at"`
}

// IssueAnalysis armazena a análise detalhada de um chamado individual.
type IssueAnalysis struct {
	IssueID           string `json:"issue_id"`
	Category          string `json:"category"`
	RootCauseSummary  string `json:"root_cause_summary"`
	ImpactScore       int    `json:"impact_score"` // 1 a 10
	Urgency           string `json:"urgency"`      // Imediato, Curto Prazo, Monitoramento
	RecommendedAction string `json:"recommended_action"`
}

// ExecutiveReport representa o relatório consolidado gerado pelo agente.
type ExecutiveReport struct {
	Title             string          `json:"title"`
	GeneratedAt       time.Time       `json:"generated_at"`
	TotalIssues       int             `json:"total_issues"`
	CriticalCount     int             `json:"critical_count"`
	HighCount         int             `json:"high_count"`
	MediumCount       int             `json:"medium_count"`
	LowCount          int             `json:"low_count"`
	CategoryBreakdown map[string]int  `json:"category_breakdown"`
	Analyses          []IssueAnalysis `json:"analyses"`
	SummaryMarkdown   string          `json:"summary_markdown"`
	TopActionItems    []string        `json:"top_action_items"`
}
