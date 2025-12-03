#!/bin/bash

# Script para executar os testes dos spiders e plays
# Este script pode ser usado na pipeline de CI/CD para monitorar o funcionamento dos componentes

# Definir cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=======================================${NC}"
echo -e "${YELLOW}= Iniciando testes dos spiders e plays =${NC}"
echo -e "${YELLOW}=======================================${NC}"

# Diretório atual
CURRENT_DIR=$(pwd)
echo -e "${BLUE}Diretório atual: $CURRENT_DIR${NC}"

# Verificar se pytest está instalado
if ! pip list | grep -q pytest; then
    echo -e "\n${YELLOW}Instalando pytest e dependências necessárias...${NC}"
    pip install pytest pytest-cov
fi

# Verificar existência dos diretórios de teste
if [ ! -d "tests/plays" ] || [ ! -d "tests/spiders" ]; then
    echo -e "\n${RED}Erro: Os diretórios de teste não existem. Verifique a estrutura do projeto.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Verificando existência dos arquivos de teste...${NC}"

# Lista de portais para testar
PORTALS=("metropoles")
# Adicione mais portais conforme são implementados:
# PORTALS=("metropoles" "uol" "folha" "veja" "r7" "ig" "terra" "globo" "estadao")

# Status para rastrear falhas
PLAYS_STATUS=0
SPIDERS_STATUS=0

# Verificar e executar testes para cada portal
for portal in "${PORTALS[@]}"; do
    PLAYS_TEST_FILE="tests/plays/test_${portal}.py"
    SPIDERS_TEST_FILE="tests/spiders/test_${portal}.py"
    
    # Verificar e executar testes dos plays
    if [ -f "$PLAYS_TEST_FILE" ]; then
        echo -e "${GREEN}✓ Arquivo de teste dos plays para ${portal} encontrado.${NC}"
        
        echo -e "\n${YELLOW}=======================================${NC}"
        echo -e "${YELLOW}=  Executando testes dos plays: ${portal}  =${NC}"
        echo -e "${YELLOW}=======================================${NC}"
        
        python -m pytest $PLAYS_TEST_FILE -v --cov=plays.${portal}
        
        # Atualizar status apenas se falhar
        if [ $? -ne 0 ]; then
            PLAYS_STATUS=1
        fi
    else
        echo -e "${YELLOW}⚠ Arquivo de teste dos plays para ${portal} não encontrado.${NC}"
    fi
    
    # Verificar e executar testes dos spiders
    if [ -f "$SPIDERS_TEST_FILE" ]; then
        echo -e "${GREEN}✓ Arquivo de teste dos spiders para ${portal} encontrado.${NC}"
        
        echo -e "\n${YELLOW}=======================================${NC}"
        echo -e "${YELLOW}= Executando testes dos spiders: ${portal} =${NC}"
        echo -e "${YELLOW}=======================================${NC}"
        
        python -m pytest $SPIDERS_TEST_FILE -v --cov=spiders.${portal}
        
        # Atualizar status apenas se falhar
        if [ $? -ne 0 ]; then
            SPIDERS_STATUS=1
        fi
    else
        echo -e "${YELLOW}⚠ Arquivo de teste dos spiders para ${portal} não encontrado.${NC}"
    fi
done

# Guardar o status dos testes dos spiders
SPIDERS_STATUS=$?

# Verificar se todos os testes passaram
echo -e "\n${YELLOW}=======================================${NC}"
echo -e "${YELLOW}=          Resumo dos testes          =${NC}"
echo -e "${YELLOW}=======================================${NC}"

if [ $PLAYS_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Testes dos plays: PASSOU${NC}"
else
    echo -e "${RED}✗ Testes dos plays: FALHOU${NC}"
fi

if [ $SPIDERS_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Testes dos spiders: PASSOU${NC}"
else
    echo -e "${RED}✗ Testes dos spiders: FALHOU${NC}"
fi

# Status final
if [ $PLAYS_STATUS -eq 0 ] && [ $SPIDERS_STATUS -eq 0 ]; then
    echo -e "\n${GREEN}✓ Todos os testes passaram com sucesso!${NC}"
    echo -e "${BLUE}Os componentes Metrópoles estão funcionando corretamente.${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Alguns testes falharam. Verifique os detalhes acima.${NC}"
    echo -e "${YELLOW}Atenção: Os componentes Metrópoles podem não estar funcionando corretamente.${NC}"
    exit 1
fi