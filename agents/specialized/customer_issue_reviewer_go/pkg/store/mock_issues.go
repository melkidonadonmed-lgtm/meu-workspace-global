package store

import (
	"time"

	"customer-issue-reviewer/pkg/models"
)

// GetMockIssues retorna um conjunto representativo de chamados de clientes para revisão.
func GetMockIssues() []models.Issue {
	now := time.Now()
	return []models.Issue{
		{
			ID:           "ISSUE-101",
			CustomerName: "FinTech Soluções Digitais",
			Title:        "Falha de confirmação em pagamentos via PIX no Checkout",
			Description:  "Clientes finais escaneiam o QR Code e pagam no banco, porém o webhook de confirmação não atualiza o status do pedido, travando vendas em produção.",
			Severity:     models.SeverityCritical,
			Module:       "Payments",
			CreatedAt:    now.Add(-2 * time.Hour),
		},
		{
			ID:           "ISSUE-102",
			CustomerName: "Logística Express Brasil",
			Title:        "Timeout HTTP 504 ao exportar relatórios mensais em CSV",
			Description:  "Contas com mais de 50.000 registros sofrem timeout de 60 segundos na API de exportação de conciliação financeira.",
			Severity:     models.SeverityHigh,
			Module:       "Reporting",
			CreatedAt:    now.Add(-5 * time.Hour),
		},
		{
			ID:           "ISSUE-103",
			CustomerName: "Varejo Global S/A",
			Title:        "Loop de redirecionamento no login via SSO Google Workspace",
			Description:  "Usuários corporativos são redirecionados infinitamente na rota /auth/callback após atualização do certificado SSL.",
			Severity:     models.SeverityCritical,
			Module:       "Auth",
			CreatedAt:    now.Add(-1 * time.Hour),
		},
		{
			ID:           "ISSUE-104",
			CustomerName: "Clinica Saúde & Vida",
			Title:        "Diferença de 3 horas nos agendamentos de consultas",
			Description:  "O calendário exibe o horário UTC em vez do fuso local (America/Sao_Paulo), gerando confusão nas consultas marcadas.",
			Severity:     models.SeverityMedium,
			Module:       "Scheduling",
			CreatedAt:    now.Add(-12 * time.Hour),
		},
		{
			ID:           "ISSUE-105",
			CustomerName: "Contabilidade Moderna",
			Title:        "Erro genérico no upload de comprovantes em PDF > 5MB",
			Description:  "Interface não informa o limite de tamanho e exibe 'Erro inesperado' ao anexar relatórios fiscais pesados.",
			Severity:     models.SeverityLow,
			Module:       "Storage",
			CreatedAt:    now.Add(-24 * time.Hour),
		},
	}
}
