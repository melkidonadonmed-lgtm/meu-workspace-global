# Canvas IDE & Frontend UI Client

Aplicação cliente frontend isolada (React + TypeScript + Vite) para interação visual com os agentes e monitoramento das ferramentas MCP.

## Isolamento de Stack
- **Node.js**: As dependências do Node.js (`node_modules`, `package.json`) ficam estritamente contidas neste diretório.
- **Python**: A raiz do workspace e os agentes não sofrem poluição de dependências de frontend.

## Como Executar
```bash
cd projects/canvas_ide
npm install
npm run dev
```
Ou utilizando o script global na raiz:
```powershell
.\run.ps1 dev
```
