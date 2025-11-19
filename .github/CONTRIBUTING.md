# 🤝 Guia de Contribuição

## 🙏 Introdução

Obrigado por considerar contribuir para o projeto Check-up! Sua participação é fundamental para tornar este projeto ainda melhor e mais útil para a comunidade.

Este documento serve como **diretrizes** e não como regras rígidas. Use seu melhor julgamento e sinta-se à vontade para propor mudanças para melhorar este próprio documento de contribuição. Valorizamos todas as formas de contribuição e estamos sempre abertos a sugestões.

**Importante**: Todos os participantes devem seguir nosso [Código de Conduta](./CODE_OF_CONDUCT.md). Ao contribuir, você concorda em manter um ambiente respeitoso e acolhedor para todos.

## 📑 Índice

- [O que Saber Antes de Iniciar](#-o-que-saber-antes-de-iniciar)
  - [Documentação Essencial](#-documentação-essencial)
  - [Executando o Projeto Localmente](#-executando-o-projeto-localmente)
- [Fluxo de Contribuição](#-fluxo-de-contribuição)
  - [Fluxo Normal (Recomendado)](#-fluxo-normal-recomendado)
  - [Fluxo Rápido (Correções Pequenas)](#-fluxo-rápido-correções-pequenas)
  - [Sobre Issues](#-sobre-issues)
  - [Labels de Pull Request](#-labels-de-pull-request)
- [Como Contribuir](#-como-contribuir)
  - [Criar um Scraper Novo](#-criar-um-scraper-novo)
  - [Adaptar um Scraper Existente](#-adaptar-um-scraper-existente)
  - [Reportar um Bug](#-reportar-um-bug)
  - [Melhorar Documentação](#-melhorar-documentação)
  - [Sugerir Melhoria](#-sugerir-melhoria)
- [Guias de Estilo](#-guias-de-estilo)
  - [Política de Commits](#-política-de-commits)
  - [Pull Requests](#-pull-requests)

## ❓ O que Saber Antes de Iniciar

### 📚 Documentação Essencial

Antes de começar a contribuir, é fundamental que você se familiarize com a documentação do projeto:

- **Documentação Principal**: Acesse [https://eh-fake.github.io/docs/sobre/o-que-e](https://eh-fake.github.io/docs/sobre/o-que-e) para uma visão geral completa do projeto

- **Estrutura da Aplicação**: Entenda como o sistema funciona consultando o [Pipeline de Dados e Scraps](https://eh-fake.github.io/docs/sobre/Pipeline_dados_scraps/) - esta seção é **essencial** para compreender a arquitetura do projeto

### 🚀 Executando o Projeto Localmente

Para contribuir efetivamente, você precisará executar o projeto em sua máquina local. Todas as instruções detalhadas de instalação e configuração estão disponíveis no [README.md](../README.md) do projeto.

Certifique-se de seguir todos os passos de configuração antes de começar a desenvolver ou testar suas contribuições.

## 🔄 Fluxo de Contribuição

### 🌟 Fluxo Normal (Recomendado)

Para a maioria das contribuições, siga este processo:

1. **📝 Criar Issue**: Abra uma issue descrevendo sua proposta ou problema
2. **🍴 Fork do Projeto**: Faça um fork do repositório para sua conta
3. **🌿 Criar Branch**: Crie uma branch específica para sua contribuição
4. **💻 Implementar**: Desenvolva sua solução seguindo os padrões do projeto
5. **🧪 Testar**: Execute os testes existentes e crie novos quando aplicável
6. **📤 Pull Request**: Abra um PR referenciando a issue original
7. **🔍 Review**: Participe do processo de revisão e faça ajustes se necessário

### ⚡ Fluxo Rápido (Correções Pequenas)

Para correções simples como erros ortográficos, documentação menor, ou ajustes de formatação:

1. **🍴 Fork do Projeto**: Faça um fork do repositório
2. **✏️ Editar Diretamente**: Faça a correção diretamente no GitHub ou localmente
3. **📤 Pull Request**: Abra um PR com descrição clara da correção
4. **✅ Merge**: Após revisão rápida, a correção será integrada

> **💡 Dica**: Issues não são necessárias para correções muito pequenas, mas sempre descreva claramente o que foi corrigido no PR.

### 📝 Sobre Issues

#### Templates Disponíveis

O projeto oferece templates específicos para diferentes tipos de contribuição (cada um será detalhado nas seções seguintes):

- **🆕 Novo Scraper de Portal**: Para adicionar suporte a novos portais de notícias
- **🔧 Adaptar Scraper Existente**: Para melhorar scrapers que já existem
- **🐛 Bug Report**: Para reportar problemas e erros


#### Labels de Issues

| Label | Descrição |
|-------|-----------|
| `new scraper` | Criação de novos scrapers para portais |
| `adapt scraper` | Adaptação de scrapers existentes |
| `bug` | Problemas e erros confirmados |
| `documentation` | Melhorias na documentação | 
| `duplicate` | Issues que são duplicatas de outras já reportadas |
| `enhancement` | Solicitações de melhorias e novas funcionalidades |
| `good first issue` | Boas primeiras contribuições para novos colaboradores |
| `help wanted` | Ajuda da comunidade é bem-vinda |
| `invalid` | Issues que não são válidas (ex: erros do usuário) |
| `question` | Perguntas mais do que reports de bugs ou pedidos de features |
| `wontfix` | Issues que a equipe decidiu não corrigir no momento |

## 🛠️ Como Contribuir

Existem várias maneiras de contribuir para o projeto Check-up. Escolha a que melhor se adequa ao seu interesse e experiência:

### 🆕 Criar um Scraper Novo

Quer adicionar suporte a um portal de notícias que ainda não está no projeto?

**🎯 Ideal para:**
- O portal não existe no projeto
- Você quer adicionar suporte a um novo portal de notícias
- Precisa criar spider e play do zero

**📚 Recursos necessários:**
- Leia o **[TUTORIAL_CRIACAO_DO_ZERO.md](../TUTORIAL_CRIACAO_DO_ZERO.md)** - guia completo passo-a-passo
- Use o template de issue: [Novo Scraper de Portal](./ISSUE_TEMPLATE/novo-scraper-portal.md)

**📝 Processo:**  
Siga o [Fluxo Normal](#-fluxo-normal-recomendado) de contribuição:
1. Abra uma issue usando o template apropriado
2. Faça fork e crie uma branch específica
3. Siga o tutorial de criação do zero
4. Implemente o spider e play seguindo os padrões do projeto
5. Execute os testes e crie novos se necessário
6. Abra um Pull Request referenciando a issue

### 🔧 Adaptar um Scraper Existente

Quer melhorar um scraper que já existe mas precisa de ajustes?

**🎯 Ideal para:**
- Portal já existe no projeto mas ainda extrai anúncios
- Precisa atualizar seletores que podem ter mudado
- Quer implementar extração de novos campos (descrição, tags)
- Scraper não está funcionando corretamente

**📚 Recursos necessários:**
- Leia o **[TUTORIAL_SPIDERS_PLAYS.md](../TUTORIAL_SPIDERS_PLAYS.md)** - guia para adaptações
- Use o template de issue: [Adaptar Scraper Existente](.github/ISSUE_TEMPLATE/adaptar-scraper-existente.md)

**📝 Processo:**  
Siga o [Fluxo Normal](#-fluxo-normal-recomendado) de contribuição:
1. Identifique o scraper que precisa ser adaptado
2. Abra uma issue usando o template apropriado
3. Faça fork e crie uma branch específica
4. Siga o tutorial de adaptação
5. Teste as mudanças com URLs reais e valide usando o checklist
6. Abra um Pull Request referenciando a issue

### 🐛 Reportar um Bug

Encontrou algo que não está funcionando como deveria?

**🎯 Ideal para:**
- Scraper não está funcionando
- Erros durante execução
- Problemas de configuração
- Comportamento inesperado

**📝 Processo:**
1. Verifique se o bug já foi reportado nas [issues existentes](https://github.com/aosfatos/check-up/issues)
2. Use o template: [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
3. Forneça o máximo de detalhes possível:
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Logs de erro
   - Ambiente (SO, versão do Python, etc.)
4. Adicione labels relevantes

### 📖 Melhorar Documentação

Quer ajudar outros contribuidores com melhor documentação?

**📋 Tipos de contribuição:**
- Corrigir erros de digitação ou gramática
- Melhorar explicações existentes
- Adicionar exemplos práticos
- Criar novos tutoriais ou guias
- Melhorar comentários no código

**📝 Processo:**
1. Identifique áreas que podem ser melhoradas
2. Para mudanças pequenas: siga o [Fluxo Rápido](#-fluxo-rápido-correções-pequenas)
3. Para mudanças grandes: siga o [Fluxo Normal](#-fluxo-normal-recomendado) abrindo uma issue primeiro
4. Mantenha o tom consistente com a documentação existente
5. Inclua exemplos quando apropriado

### 💡 Sugerir Melhoria

Tem uma ideia para tornar o projeto ainda melhor?

**📋 Tipos de sugestão:**
- Melhorias na arquitetura do sistema
- Otimizações de performance
- Novas funcionalidades
- Melhorias na experiência do usuário
- Automatizações de processos

**📝 Processo:**  
1. Verifique se a sugestão já foi proposta nas [issues existentes](https://github.com/aosfatos/check-up/issues)
2. Abra uma issue com o label `enhancement`
3. Descreva claramente:
   - O problema ou oportunidade identificada
   - Sua proposta de solução
   - Benefícios esperados
   - Possíveis impactos ou considerações
4. Participe da discussão com a comunidade
5. Se aprovada, implemente seguindo o [Fluxo Normal](#-fluxo-normal-recomendado) de contribuição 

## 📏 Guias de Estilo

Para manter a consistência e qualidade do código, é essencial seguir nossos padrões estabelecidos:

### 📦 Política de Commits

Para garantir a consistência e rastreabilidade das mensagens de commit, siga nossa [Política de Commits](https://eh-fake.github.io/docs/guia-de-contribuicao/politica-de-commits/), que define:
- Formato de mensagens usando o padrão Conventional Commits
- Orientações para escrever descrições de commit claras e concisas
- Boas práticas para manter um histórico de commits organizado e fácil de entender

### 📤 Pull Requests

#### Formato do Título
O formato padrão para títulos de Pull Requests é o mesmo da [Política de Commits](https://eh-fake.github.io/docs/guia-de-contribuicao/politica-de-commits/):

```
<tipo>(<escopo>): resumo curto [<label>]
```

- `tipo`: tipo de mudança (feat, fix, docs, etc.)
- `escopo`: escopo da mudança (scraper, parser, etc.)
- `label`: label do PR (work-in-progress, needs-review, etc.) -> somente se aplicável


**Exemplos:**
```
feat(scraper): adiciona suporte ao portal Folha de S.Paulo [work-in-progress]
```
```
fix(parser): corrige extração de data no Estadão [needs-review]
```
```
docs(tutorial): atualiza guia de criação de scrapers
```

#### Labels de Pull Request

| Label | Descrição |
|-------|-----------|
| `work-in-progress` | Pull requests que ainda estão sendo desenvolvidos, mais mudanças virão |
| `needs-review` | Pull requests que precisam de revisão de código e aprovação dos mantenedores |
| `under-review` | Pull requests sendo revisados pelos mantenedores ou equipe principal |
| `requires-changes` | Pull requests que precisam ser atualizados baseado nos comentários de revisão |
| `needs-testing` | Pull requests que precisam de testes manuais |


#### Template de PR
O projeto utiliza um template automático que inclui:
- **Descrição**: Explicação do que foi alterado e por quê
- **Tipo de Mudança**: Checkboxes para categorizar (bug, feature, docs, etc.)
- **Checklist**: Verificações obrigatórias (commits, branches, testes, documentação)
- **Issues Relacionadas**: Referência às issues vinculadas
- **Como Testar**: Passos para validar as mudanças


> ⚠️ **Importante**: Aderir a essas convenções facilita a revisão do código, melhora a rastreabilidade das alterações e mantém o projeto organizado para todos os contribuidores.
