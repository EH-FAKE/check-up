# Como Implementar Testes para Novos Scrapers

Este guia simplificado explica como criar testes para novos scrapers no projeto Check-Up.

## Passo a Passo

### 1. Use o Script de Criação de Template

O projeto possui um script para gerar automaticamente os templates de teste:

```bash
./scripts/create_test_template.sh nome_do_portal
```

Este comando criará:
- `tests/plays/test_nome_do_portal.py`
- `tests/spiders/test_nome_do_portal.py`

### 2. Adapte os Templates

Após a criação, você precisa adaptar os templates:

**Para Plays**:
- Ajuste os seletores CSS/XPath de acordo com o HTML do portal
- Atualize as URLs de exemplo para o formato do portal
- Verifique a extração de título, descrição, conteúdo e tags

**Para Spiders**:
- Ajuste as verificações de URLs permitidas
- Adapte o HTML simulado
- Atualize os padrões de extração de links

### 3. Adicione o Portal ao Script de Testes

Edite o arquivo `run_portal_tests.sh` para incluir seu portal:

```bash
PORTALS=("metropoles" "seu_novo_portal")
```

### 4. Execute os Testes

Para testar seu novo portal:

```bash
make test_portals
```

Ou para testar apenas seu portal:

```bash
python -m pytest tests/plays/test_nome_do_portal.py -v --cov=plays.nome_do_portal
python -m pytest tests/spiders/test_nome_do_portal.py -v --cov=spiders.nome_do_portal
```

### 5. Verifique a Cobertura

Procure atingir pelo menos 80% de cobertura de código nos testes.

## Dicas Importantes

1. Use mocks para evitar chamadas reais ao Playwright e sites externos
2. Teste tanto casos de sucesso quanto de falha
3. Verifique a integração com o CI/CD após implementar os testes

Para informações mais detalhadas, consulte o [Guia de Testes](../docs/GUIA_DE_TESTES.md).