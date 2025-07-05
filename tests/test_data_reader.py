import pytest
import json
from unittest.mock import Mock, patch

from data_reader import DataReader, read_json_file


class TestDataReader:
    """Testes para a classe DataReader."""
    
    @pytest.fixture
    def mock_minio_client(self):
        """Mock do cliente MinIO."""
        client = Mock()
        client.list_buckets.return_value = []
        return client
    
    @pytest.fixture
    def sample_json_data(self):
        """Dados JSON de exemplo para testes."""
        return {
            "portal": "metropoles",
            "url": "https://www.metropoles.com/test-article",
            "title": "Artigo de Teste sobre Saúde",
            "body": "Conteúdo completo do artigo sobre medicina e hospitais.",
            "description": "Descrição do artigo",
            "tags": ["saúde", "medicina"],
            "scraped_at": "2024-01-15T10:30:00",
            "entry_id": 123,
            "ads": [
                {
                    "title": "Anúncio de Saúde",
                    "url": "https://example.com/ad1",
                    "thumbnail": "https://example.com/thumb1.jpg",
                    "tag": "Saúde",
                    "excerpt": "Produtos para saúde"
                }
            ]
        }
    
    @pytest.fixture
    def data_reader(self, mock_minio_client):
        """Instância do DataReader com mock."""
        with patch('data_reader.DataReader._get_minio_client', return_value=mock_minio_client):
            reader = DataReader()
            return reader
    
    def test_init(self, data_reader):
        """Testa inicialização do DataReader."""
        assert data_reader.minio_client is not None
        assert data_reader.bucket_name == "scraped-articles"
    
    def test_read_single_json_success(self, data_reader, sample_json_data):
        """Testa leitura bem-sucedida de um arquivo JSON."""
        mock_obj = Mock()
        
        with patch('json.load', return_value=sample_json_data):
            data_reader.minio_client.get_object.return_value = mock_obj
            
            result = data_reader.read_single_json("test_file.json")
            
            assert result == sample_json_data
    
    def test_read_single_json_invalid_json(self, data_reader):
        """Testa leitura de arquivo com JSON inválido."""
        mock_obj = Mock()
        
        with patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            data_reader.minio_client.get_object.return_value = mock_obj
            
            result = data_reader.read_single_json("invalid.json")
            
            assert result is None


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""
    
    @patch('data_reader.DataReader')
    def test_read_json_file(self, mock_data_reader_class):
        """Testa função de conveniência read_json_file."""
        mock_reader = Mock()
        mock_reader.read_single_json.return_value = {"test": "data"}
        mock_data_reader_class.return_value = mock_reader
        
        result = read_json_file("test.json")
        
        assert result == {"test": "data"}
        mock_reader.read_single_json.assert_called_once_with("test.json")


@pytest.mark.integration
class TestDataReaderIntegration:
    """Testes de integração que requerem ambiente configurado."""
    
    @pytest.mark.skip(reason="Requer MinIO configurado")
    def test_real_minio_connection(self):
        """Testa conexão real com MinIO (requer ambiente configurado)."""
        try:
            reader = DataReader()
            assert reader.minio_client is not None
        except Exception:
            pytest.skip("MinIO não configurado")
    
    @pytest.mark.skip(reason="Requer dados reais")
    def test_real_data_reading(self):
        """Testa leitura de dados reais (requer dados no MinIO)."""
        try:
            data = read_json_file("test_file.json")
            if data:
                assert 'portal' in data
                assert 'title' in data
            else:
                pytest.skip("Arquivo de teste não encontrado")
                
        except Exception:
            pytest.skip("Ambiente não configurado")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 