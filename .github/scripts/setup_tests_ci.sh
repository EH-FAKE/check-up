#!/bin/bash

# Script para configurar ambiente de testes para CI/CD

# Instalar dependências
pip install pytest pytest-cov playwright

# Instalar navegadores Playwright com permissões corretas
playwright install --with-deps firefox
chmod -R 777 ~/.cache/ms-playwright

# Verificar se os navegadores foram instalados corretamente
python -c "from playwright.sync_api import sync_playwright; \
    with sync_playwright() as p: \
        browser = p.firefox.launch_persistent_context('/tmp/pw', headless=True); \
        page = browser.new_page(); \
        print('Playwright está funcionando corretamente!'); \
        browser.close()"
        
# Verificar instalação e listar dependências instaladas
pip list | grep -E 'pytest|playwright|coverage'