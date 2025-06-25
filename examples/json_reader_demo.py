#!/usr/bin/env python3
"""
Demonstração simples do DataReader para leitura de dados JSON.

Este script mostra como usar a funcionalidade básica de leitura de JSON
implementada no módulo data_reader.py.
"""

import sys
import os
import json
import tempfile
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_reader import DataReader, read_json_file
from plog import logger


def create_sample_json_data():
    """Cria dados JSON de exemplo para demonstração."""
    return {
        "portal": "metropoles",
        "url": "https://www.metropoles.com/artigo-exemplo",
        "title": "Artigo de Exemplo sobre Saúde Mental",
        "body": "Este é um artigo completo sobre saúde mental e bem-estar. Contém informações importantes sobre prevenção e tratamento.",
        "description": "Descrição do artigo sobre saúde mental",
        "tags": ["saúde", "medicina", "bem-estar", "prevenção"],
        "scraped_at": "2024-12-25T15:30:00",
        "entry_id": 12345,
        "ads": [
            {
                "title": "Plano de Saúde Premium",
                "url": "https://example.com/plano-saude",
                "thumbnail": "https://example.com/thumb-saude.jpg",
                "tag": "Saúde",
                "excerpt": "Cobertura completa para toda família"
            },
            {
                "title": "Consulta Online",
                "url": "https://example.com/consulta-online",
                "thumbnail": "https://example.com/thumb-consulta.jpg",
                "tag": "Telemedicina",
                "excerpt": "Consultas médicas pelo seu smartphone"
            },
            {
                "title": "Exames Laboratoriais",
                "url": "https://example.com/exames",
                "thumbnail": "https://example.com/thumb-exames.jpg",
                "tag": "Diagnóstico",
                "excerpt": "Exames com resultados em 24h"
            }
        ]
    }


def demo_basic_usage():
    """Demonstra uso básico do DataReader."""
    print("=" * 60)
    print("🚀 DEMO: Uso Básico do DataReader")
    print("=" * 60)
    
    try:
        # Criar dados de exemplo
        sample_data = create_sample_json_data()
        print(f"\n📝 Dados de exemplo criados:")
        print(f"   - Portal: {sample_data['portal']}")
        print(f"   - Título: {sample_data['title']}")
        print(f"   - Anúncios: {len(sample_data['ads'])}")
        
        # Mock do cliente MinIO para demonstração
        print("\n📖 Demonstrando leitura com dados mockados:")
        
        # Mock do objeto MinIO
        mock_obj = Mock()
        
        with patch('json.load', return_value=sample_data):
            with patch('data_reader.DataReader._get_minio_client') as mock_minio:
                mock_client = Mock()
                mock_client.get_object.return_value = mock_obj
                mock_minio.return_value = mock_client
                
                # Testar função de conveniência
                data = read_json_file("exemplo_file.json")
                
                if data:
                    print("✅ JSON carregado com sucesso!")
                    print(f"   - Portal: {data.get('portal', 'N/A')}")
                    print(f"   - Título: {data.get('title', 'N/A')}")
                    print(f"   - URL: {data.get('url', 'N/A')}")
                    print(f"   - Anúncios: {len(data.get('ads', []))}")
                    print(f"   - Tags: {', '.join(data.get('tags', []))}")
                    
                    # Mostrar alguns anúncios
                    ads = data.get('ads', [])
                    if ads:
                        print(f"\n📢 Primeiros 2 anúncios encontrados:")
                        for i, ad in enumerate(ads[:2]):
                            print(f"   {i+1}. {ad.get('title', 'N/A')} ({ad.get('tag', 'N/A')})")
                
                # Testar usando a classe diretamente
                print("\n📖 Usando DataReader diretamente:")
                reader = DataReader()
                data2 = reader.read_single_json("exemplo_file2.json")
                
                if data2:
                    print("✅ Arquivo lido com sucesso usando DataReader!")
                    print(f"   - Estrutura de dados está completa: {bool(data2.get('portal') and data2.get('title'))}")
                else:
                    print("⚠️ Dados não encontrados (simulação)")
        
        # Demonstrar estrutura de dados esperada
        print("\n📋 Estrutura de dados JSON esperada:")
        print("   Campos principais:")
        for field in ['portal', 'url', 'title', 'body', 'description', 'tags', 'scraped_at', 'entry_id', 'ads']:
            if field in sample_data:
                field_type = type(sample_data[field]).__name__
                print(f"   - {field}: {field_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no demo: {e}")
        return False


def demo_with_real_data():
    """Demonstra tentativa de leitura de dados reais (pode falhar se não houver dados)."""
    print("\n" + "=" * 60)
    print("🔍 DEMO: Tentativa de Dados Reais")
    print("=" * 60)
    
    try:
        print("\n⚠️  Tentando conectar ao MinIO real...")
        print("   (Isso pode falhar se o bucket não existir)")
        
        # Tentar leitura real (pode falhar)
        reader = DataReader()
        data = reader.read_single_json("test_file.json")
        
        if data:
            print("✅ Dados reais encontrados!")
            print(f"   - Portal: {data.get('portal', 'N/A')}")
            print(f"   - Título: {data.get('title', 'N/A')}")
        else:
            print("ℹ️  Nenhum dado real encontrado (isso é normal)")
            print("   Para ter dados reais, execute: make scrape-no-ai")
        
        return True
        
    except Exception as e:
        print(f"ℹ️  Falha esperada: {str(e)[:100]}...")
        print("   Isso é normal quando não há dados no MinIO")
        return True  # Não é erro, é esperado


def main():
    """Executa a demonstração."""
    print("🎯 Demonstração Simples do Sistema de Leitura de JSON")
    print("=" * 60)
    
    success1 = demo_basic_usage()
    success2 = demo_with_real_data()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO")
    print("=" * 60)
    
    if success1:
        print("✅ Demo com dados mockados executado com sucesso!")
        if success2:
            print("✅ Teste de conexão real concluído!")
        
        print("\n💡 Como usar:")
        print("   1. Use read_json_file('caminho/arquivo.json') para leitura simples")
        print("   2. Use DataReader() para instanciar a classe diretamente")
        print("   3. Execute 'make scrape-no-ai' para gerar dados JSON reais")
        print("   4. Os dados são salvos no MinIO em buckets organizados por portal")
        
        print("\n📋 Estrutura de arquivo esperada:")
        print("   - Portal: string (ex: 'metropoles')")
        print("   - URL: string com URL do artigo")
        print("   - Título: string com título do artigo")
        print("   - Body: string com conteúdo completo")
        print("   - Tags: lista de strings")
        print("   - Ads: lista de objetos com anúncios")
        
        print("\n🔧 Próximos passos:")
        print("   - Use 'make test-json' para executar testes")
        print("   - Implemente buscas e análises conforme necessário")
        print("   - Funcionalidade de leitura está pronta para uso")
    else:
        print("❌ Demo falhou. Verifique logs para detalhes.")


if __name__ == "__main__":
    main() 