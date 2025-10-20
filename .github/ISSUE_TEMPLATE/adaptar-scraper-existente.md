---
name: "\U0001F527 Adaptar Scraper Existente"
about: Adaptar um scraper existente para extrair conteúdo de notícias (título, descrição,
  corpo, tags)
title: "[ADAPTAÇÃO] Portal: [NOME_DO_PORTAL]"
labels: ''
assignees: ''

---

## 📋 Informações do Portal

**Portal:** [Nome do portal - ex: R7, UOL, Folha]
**URL:** [URL do portal - ex: https://www.r7.com]
**Status atual:** [Funcional/Em desenvolvimento/Quebrado]

## 🎯 Objetivo

Adaptar o scraper existente do portal para extrair **conteúdo de notícias** em vez de anúncios.

### ✅ Campos a serem extraídos:
- [ ] **Título** - Título principal da notícia
- [ ] **Descrição** - Subtítulo ou resumo da notícia  
- [ ] **Corpo** - Texto completo da matéria
- [ ] **Tags** - Categorias e etiquetas associadas

## 🔍 Análise Atual

### Spider (Coleta de URLs)
- [ ] **Filtragem de URLs**: Verificar se `allow_url()` está funcionando corretamente
- [ ] **Remoção de crawling recursivo**: Remover `yield scrapy.Request` desnecessários
- [ ] **Teste de coleta**: URLs coletados são realmente de notícias?

### Play (Extração de Conteúdo)
- [ ] **Re-inspeção do portal**: Estrutura HTML pode ter mudado
- [ ] **Seletores atualizados**: Verificar se seletores existentes ainda funcionam
- [ ] **Novos seletores**: Identificar seletores para descrição e tags
- [ ] **Remoção de código de anúncios**: Remover `take_screenshot` e código relacionado

## 🧪 Testes Necessários

### URLs de Teste
Forneça 3-5 URLs reais de notícias do portal para teste:
1. [URL exemplo 1]
2. [URL exemplo 2] 
3. [URL exemplo 3]
4. [URL exemplo 4]
5. [URL exemplo 5]

### Validação
- [ ] Spider coleta apenas URLs de notícias válidas
- [ ] Play extrai título corretamente
- [ ] Play extrai descrição (quando disponível)
- [ ] Play extrai corpo completo da notícia
- [ ] Play extrai tags (quando disponível)
- [ ] Não há erros de timeout ou seletores quebrados

## 📚 Recursos

- **Tutorial completo**: [TUTORIAL_SPIDERS_PLAYS.md](../TUTORIAL_SPIDERS_PLAYS.md)
- **Exemplos de referência**: 
  - `gazetaDoPovo.py` (spider com boa filtragem)
  - `metropoles.py` (play com extração completa)

## 🔧 Checklist de Implementação

### Spider
- [ ] Remove `yield scrapy.Request` recursivo
- [ ] Implementa `allow_url()` com boa filtragem
- [ ] Coleta apenas URLs da página inicial
- [ ] URLs coletados são realmente de notícias

### Play  
- [ ] **RE-INSPECIONA** o portal no navegador atual
- [ ] **ATUALIZA seletores existentes** (título, corpo) - não usar código antigo cegamente
- [ ] **IDENTIFICA seletores novos** para description e tags
- [ ] Remove `take_screenshot()` e variáveis relacionadas
- [ ] **TESTA extração** de título com seletores atualizados
- [ ] **IMPLEMENTA extração** de descrição (NOVO campo)
- [ ] **TESTA extração** de corpo com seletores atualizados
- [ ] **IMPLEMENTA extração** de tags (NOVO campo)
- [ ] **VALIDA** que todos os 4 campos são extraídos corretamente
- [ ] Retorna `EntryItem` com os dados corretos
- [ ] **TESTA com URLs reais** do portal atual

## 📝 Notas Adicionais

[Adicione qualquer informação adicional relevante, como problemas específicos encontrados, seletores identificados, etc.]

---

**⚠️ IMPORTANTE**: Antes de começar, leia o [TUTORIAL_SPIDERS_PLAYS.md](../TUTORIAL_SPIDERS_PLAYS.md) para entender o processo completo de adaptação.
