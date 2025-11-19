---
name: 🆕 Novo Scraper de Portal
about: Criar um novo scraper para um portal de notícias que ainda não está presente no projeto
title: '[NOVO] Portal: [NOME_DO_PORTAL]'
labels: ['novo', 'scraper', 'portal', 'notícias']
assignees: ''
---

## 📋 Informações do Portal

**Portal:** [Nome do portal - ex: Correio Braziliense, G1, CNN Brasil]
**URL:** [URL do portal - ex: https://www.correiobraziliense.com.br]
**Categoria:** [Nacional/Regional/Internacional]
**Tipo de conteúdo:** [Notícias gerais/Política/Esportes/Economia/etc]

## 🎯 Objetivo

Criar um novo scraper completo para extrair **conteúdo de notícias** do portal.

### ✅ Campos a serem extraídos:
- [ ] **Título** - Título principal da notícia
- [ ] **Descrição** - Subtítulo ou resumo da notícia  
- [ ] **Corpo** - Texto completo da matéria
- [ ] **Tags** - Categorias e etiquetas associadas

## 🔍 Análise do Portal

### Estrutura da Página Inicial
- [ ] **Identificar seção de notícias**: Onde estão os links das notícias principais?
- [ ] **Padrão de URLs**: Como são estruturadas as URLs das notícias?
- [ ] **Filtros necessários**: Que tipos de páginas devem ser ignoradas?

### Estrutura das Páginas de Notícia
- [ ] **Seletor do título**: Qual elemento contém o título principal?
- [ ] **Seletor da descrição**: Existe subtítulo/resumo? Qual elemento?
- [ ] **Seletor do corpo**: Onde está o texto principal da notícia?
- [ ] **Seletor das tags**: Onde estão as categorias/etiquetas?

## 🧪 URLs de Teste

Forneça 5-10 URLs reais de notícias do portal para desenvolvimento e teste:

### URLs da Página Inicial
- [URL da página inicial]

### URLs de Notícias para Teste
1. [URL notícia 1 - política]
2. [URL notícia 2 - esportes] 
3. [URL notícia 3 - economia]
4. [URL notícia 4 - tecnologia]
5. [URL notícia 5 - cultura]
6. [URL notícia 6 - internacional]
7. [URL notícia 7 - saúde]
8. [URL notícia 8 - educação]

## 🛠️ Implementação Necessária

### 1. Adicionar Portal ao Banco de Dados
```bash
make bash
python add_portal.py "[Nome do Portal]" "[URL do Portal]"
```

### 2. Criar Spider (spiders/[nome].py)
- [ ] Herdar de `BaseSpider`
- [ ] Implementar `allow_url()` com filtragem adequada
- [ ] Coletar apenas URLs da página inicial (sem crawling recursivo)
- [ ] Testar coleta de URLs válidos

### 3. Criar Play (plays/[nome].py)
- [ ] Herdar de `BasePlay`
- [ ] Implementar método `match()` para identificar URLs do portal
- [ ] Implementar extração de título
- [ ] Implementar extração de descrição
- [ ] Implementar extração de corpo
- [ ] Implementar extração de tags
- [ ] Retornar `EntryItem` com todos os campos

### 4. Adicionar Comandos Makefile
- [ ] `make crawl_[nome]` - para coleta de URLs
- [ ] `make scrape_[nome]` - para extração de conteúdo

## 🧪 Testes e Validação

### Teste do Spider
- [ ] Coleta URLs apenas da página inicial
- [ ] URLs coletados são realmente de notícias
- [ ] Não coleta URLs de outras seções (vídeos, podcasts, etc.)
- [ ] Filtragem funciona corretamente

### Teste do Play
- [ ] Extrai título corretamente em todas as URLs de teste
- [ ] Extrai descrição quando disponível
- [ ] Extrai corpo completo da notícia
- [ ] Extrai tags quando disponível
- [ ] Não há erros de timeout ou seletores quebrados
- [ ] Funciona com diferentes tipos de notícia

### Teste de Integração
- [ ] Pipeline completo funciona: `make crawl_[nome]` + `make scrape_[nome]`
- [ ] Dados são salvos corretamente no banco PostgreSQL
- [ ] Logs não mostram erros críticos

## 📚 Recursos e Referências

- **Tutorial de criação do zero**: [TUTORIAL_CRIACAO_DO_ZERO.md](../TUTORIAL_CRIACAO_DO_ZERO.md) - Guia completo passo-a-passo
- **Tutorial de adaptação**: [TUTORIAL_SPIDERS_PLAYS.md](../TUTORIAL_SPIDERS_PLAYS.md) - Para adaptar scrapers existentes
- **Exemplos de referência**: 
  - `gazetaDoPovo.py` (spider com boa filtragem)
  - `metropoles.py` (play com extração completa)
- **Base classes**: `spiders/base.py` e `plays/base.py`

## 🔧 Checklist de Implementação

### Preparação
- [ ] Portal adicionado ao banco de dados
- [ ] URLs de teste coletadas e validadas
- [ ] Estrutura HTML analisada no navegador

### Spider
- [ ] Arquivo `spiders/[nome].py` criado
- [ ] Herda de `BaseSpider`
- [ ] Implementa `allow_url()` com boa filtragem
- [ ] Coleta apenas URLs da página inicial
- [ ] Testado com URLs reais

### Play
- [ ] Arquivo `plays/[nome].py` criado
- [ ] Herda de `BasePlay`
- [ ] Implementa método `match()`
- [ ] **IDENTIFICA seletores** para título, descrição, corpo e tags
- [ ] **TESTA extração** de todos os 4 campos
- [ ] **VALIDA** com todas as URLs de teste
- [ ] Retorna `EntryItem` com dados corretos

### Integração
- [ ] Comandos adicionados ao Makefile
- [ ] Pipeline completo testado
- [ ] Dados salvos no banco corretamente

## 📝 Informações Técnicas

### Seletores Identificados
```css
/* Título */
[seletor do título]

/* Descrição */
[seletor da descrição]

/* Corpo */
[seletor do corpo]

/* Tags */
[seletor das tags]
```

### Padrões de URL
```
[Descrever o padrão das URLs de notícias]
```

### Observações Especiais
[Adicione qualquer informação especial sobre o portal, como:
- Necessidade de autenticação
- JavaScript necessário
- Rate limiting
- Estrutura específica
- etc.]

---

**⚠️ IMPORTANTE**: Antes de começar, leia o [TUTORIAL_SPIDERS_PLAYS.md](../TUTORIAL_SPIDERS_PLAYS.md) para entender o processo completo de criação de scrapers.
