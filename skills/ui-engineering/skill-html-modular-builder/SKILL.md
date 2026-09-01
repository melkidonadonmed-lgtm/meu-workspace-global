---
name: skill-html-modular-builder
version: 1.0.0
description: Construtor de HTML5 modular, Atomic Design (Átomos, Moléculas, Organismos) e montagem de páginas completas acessíveis (WCAG 2.1 AA) com Tailwind CSS.
triggers:
  - "crie uma página HTML"
  - "monte um layout em componentes"
  - "desenvolva o HTML modular para"
  - "estruture uma landing page em módulos"
  - "converta este wireframe em HTML"
  - "montagem de pages"
  - "montagem html"
  - "html modular"
---

# SKILL.md — Construtor de HTML Modular e Design System Componentizado (`skill-html-modular-builder`)

## Metadados da Habilidade
- **Nome:** HTML Modular Architect & Component Assembler
- **Versão:** 1.0.0
- **Categoria:** Frontend Engineering, UI Componentization, HTML5 & CSS Architecture
- **Finalidade:** Receber especificações de layout, wireframes ou estruturas de páginas e montar código HTML5 semântico, acessível (WCAG 2.1 AA) e modularizado em componentes reutilizáveis (Header, Hero, Cards, Section, Footer, Layout Grid), aplicando classes utilitárias (Tailwind CSS) ou Web Components.
- **Gatilhos de Ativação:** "crie uma página HTML", "monte um layout em componentes", "desenvolva o HTML modular para...", "estruture uma landing page em módulos", "converta este wireframe em HTML", "montagem de pages", "html modular".

---

## 1. Diretrizes de Arquitetura Modular (Atomic Design)
Ao montar qualquer página ou tela, o sub-agente deve obrigatoriamente fragmentar a saída em quatro níveis lógicos:
1. **Átomos:** Botões (`<button>`), inputs (`<input>`), badges (`<span>`), ícones inline (`<svg>`).
2. **Moléculas:** Campos de busca (input + botão), cards simples (imagem + título + texto), itens de navegação (`<li>` + `<a>`).
3. **Organismos:** Seção de Hero (`<header>` + títulos + CTA), barra de navegação (`<nav>`), grid de produtos, rodapé (`<footer>`).
4. **Templates / Páginas:** A casca do documento (`index.html`) contendo as chamadas e o encaixe ordenado dos organismos.

---

## 2. Fluxo Operacional de Processamento

### Passo 1: Análise e Decomposição de Componentes
1. Identifique o objetivo da página (Landing Page, Dashboard, Formulário de Checkout, Portal).
2. Liste todos os organismos e moléculas necessários para a tela.
3. Defina a paleta de cores, tipografia e espaçamentos baseados em tokens utilitários do Tailwind CSS ou variáveis CSS customizadas (`:root`).

### Passo 2: Construção Semântica e Acessibilidade (WCAG 2.1 AA)
1. Utilize estritamente elementos semânticos do HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`.
2. Inclua atributos de acessibilidade (ARIA): `aria-label`, `aria-expanded`, `role="..."`, suporte a navegação via teclado e marcas de foco visível.
3. Utilize atributos `alt` descritivos em todas as tags `<img>` e suporte para imagens responsivas (`<picture>` ou `srcset`).

### Passo 3: Montagem Modular e Exportação
Gere a resposta separando os blocos em dois formatos de entrega:
1. **Visão de Componentes Isolados:** Códigos reutilizáveis prontos para cópia e cola ou inclusão em templates.
2. **Página Consolidada Completa:** Documento HTML5 totalmente funcional (`<!DOCTYPE html>`) unificando os componentes.

---

## 3. Restrições Negativas e Guardrails (O que NÃO fazer)

- ❌ **NUNCA utilizar tags genéricas desnecessárias:** Proibido o uso excessivo de `<div>` empilhadas (*divsoup*); priorize tags semânticas HTML5.
- ❌ **NUNCA incluir estilos CSS inline inseguros:** Use estritamente classes utilitárias (ex: Tailwind CSS) ou bloco `<style>` organizado por variáveis `:root`.
- ❌ **NUNCA utilizar código JavaScript de terceiros não verificado:** Scripts de interação devem ser em JavaScript Vanilla puro (`<script>`), sem dependência de bibliotecas externas pesadas.
- ❌ **NUNCA ignorar responsividade:** Toda estrutura gerada deve ser nativamente responsiva (Mobile-First) com flexbox e CSS Grid.

---

## 4. Contrato de Integração Python (Sub-Agente Stateless)

```python
"""
Visão Geral:
Sub-Agente Especialista Stateless para geração de HTML5 Modular.
Recebe requisitos de UI do Orquestrador e retorna os componentes montados e tipados.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class ComponentRequirement(BaseModel):
    name: str = Field(description="Nome do componente (ex: Navbar, HeroSection, PricingCard)")
    type: str = Field(description="Tipo de elemento: atom, molecule, organism")
    description: str = Field(description="Detalhamento funcional e visual do componente")

class HTMLBuildRequest(BaseModel):
    page_title: str = Field(description="Título principal da página")
    page_type: str = Field(default="landing_page", description="Tipo de página: landing_page, dashboard, checkout, blog")
    styling_framework: str = Field(default="tailwind", description="Framework de estilo: tailwind, css_variables, bootstrap")
    components: List[ComponentRequirement] = Field(description="Lista de componentes obrigatórios a serem construídos")

class HTMLComponentOutput(BaseModel):
    component_name: str
    component_type: str
    html_code: str
    usage_notes: str

class HTMLBuildResponse(BaseModel):
    page_title: str
    assembled_components: List[HTMLComponentOutput]
    full_html_document: str
    accessibility_checklist: List[str]
```
