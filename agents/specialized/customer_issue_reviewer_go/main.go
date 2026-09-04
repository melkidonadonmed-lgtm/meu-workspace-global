package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"customer-issue-reviewer/pkg/store"
	"customer-issue-reviewer/pkg/workflow"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/cmd/launcher"
	"google.golang.org/adk/v2/cmd/launcher/full"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()

	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		apiKey = os.Getenv("GOOGLE_API_KEY")
	}

	// Verifica se foi solicitado o relatório direto/estruturado
	wantReport := false
	for _, arg := range os.Args[1:] {
		if arg == "-report" || arg == "--report" || arg == "-offline" {
			wantReport = true
			break
		}
	}

	// Caso tenha sido passado -report ou não haja chave configurada sem subcomandos
	if wantReport || (apiKey == "" && len(os.Args) == 1) {
		fmt.Println("================================================================================")
		fmt.Println("🚀 Customer Issue Reviewer Agent (Google ADK Go v2)")
		if apiKey == "" {
			fmt.Println("⚠️ Nenhuma GEMINI_API_KEY ou GOOGLE_API_KEY encontrada no ambiente.")
		}
		fmt.Println("Executando análise de chamados do cliente...")
		fmt.Println("================================================================================")
		fmt.Println()

		issues := store.GetMockIssues()
		report := workflow.GenerateDirectReportOffline(issues)

		fmt.Printf("📊 %s\n", report.Title)
		fmt.Printf("Total de Chamados: %d | Críticos: %d | Altos: %d | Médios: %d | Baixos: %d\n\n",
			report.TotalIssues, report.CriticalCount, report.HighCount, report.MediumCount, report.LowCount)

		fmt.Println("📌 Distribuição por Módulo:")
		for mod, count := range report.CategoryBreakdown {
			fmt.Printf("  - %s: %d chamado(s)\n", mod, count)
		}

		fmt.Println("\n🚨 Detalhamento dos Chamados Analisados:")
		for _, a := range report.Analyses {
			fmt.Printf("  • [%s] Módulo: %s | Impacto: %d/10 | Urgência: %s\n    Diagnóstico: %s\n    Ação: %s\n",
				a.IssueID, a.Category, a.ImpactScore, a.Urgency, a.RootCauseSummary, a.RecommendedAction)
		}

		fmt.Println("\n🎯 Plano de Ação Recomendado:")
		for i, item := range report.TopActionItems {
			fmt.Printf("  %d. %s\n", i+1, item)
		}

		fmt.Println("\n💡 Para executar o pipeline interativo com o modelo Gemini pelo ADK Go Launcher:")
		fmt.Println("   $env:GEMINI_API_KEY=\"sua_chave\"")
		fmt.Println("   go run main.go")
		fmt.Println("   go run main.go web api webui  # Abre playground web em http://localhost:8080")
		return
	}

	modelName := os.Getenv("GEMINI_MODEL")
	if modelName == "" {
		modelName = "gemini-3.6-flash"
	}

	// Inicializa o modelo Gemini via ADK Go v2
	geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{
		APIKey: apiKey,
	})
	if err != nil {
		log.Fatalf("❌ Erro ao inicializar modelo Gemini: %v", err)
	}

	// Constrói o pipeline de agentes em grafo
	workflowAgent, err := workflow.BuildCustomerReviewerWorkflow(ctx, geminiModel)
	if err != nil {
		log.Fatalf("❌ Erro ao construir workflow de agentes: %v", err)
	}

	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(workflowAgent),
	}

	l := full.NewLauncher()
	if err = l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("Execução do Launcher falhou: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
