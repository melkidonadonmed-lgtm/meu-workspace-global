# Web Visual Auditor

Pacote autônomo em Python 3.11+ para pesquisa web semântica, inspeção geométrica do DOM com Playwright headless e auditoria de regressão visual diferencial pixel a pixel (tela inteira e micro-componentes de design systems).

## Instalação e Desenvolvimento

```bash
uv pip install -e ".[dev]"
```

## Módulos

- `web_visual_auditor.models`: Modelos de dados canônicos Pydantic v2 estritos.
- `web_visual_auditor.exceptions`: Hierarquia de exceções especializadas.
- `web_visual_auditor.researcher`: Pesquisa estruturada e extração semântica limpa de HTML.
- `web_visual_auditor.dom_auditor`: Inspeção de coordenadas geométricas computadas e visibilidade via Playwright.
- `web_visual_auditor.visual_regression`: Comparação de imagens pixel a pixel com tolerância de canal e mapa de calor `#FF0000`.
- `web_visual_auditor.component_auditor`: Isolamento de seletores CSS e auditoria de micro-componentes.
- `web_visual_auditor.suite`: Orquestrador integrado de auditoria completa.
- `web_visual_auditor.cli`: Interface unificada de linha de comando.
