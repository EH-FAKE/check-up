import json
from typing import Dict, Optional

from decouple import config
from minio import Minio
from minio.error import S3Error

from plog import logger


class DataReader:
    """
    Classe simples para leitura de dados JSON salvos no MinIO.
    """
    
    def __init__(self):
        self.minio_client = self._get_minio_client()
        self.bucket_name = config("MINIO_BUCKET", default="scraped-articles")
        
    def _get_minio_client(self) -> Minio:
        """Inicializa cliente MinIO com configurações do ambiente."""
        endpoint = config("MINIO_ENDPOINT")
        access_key = config("MINIO_ACCESS_KEY")
        secret_key = config("MINIO_SECRET_KEY")
        secure = config("MINIO_SECURE", cast=bool)
        
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        try:
            client.list_buckets()
            logger.info(f"✅ Connected to MinIO at {endpoint}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MinIO: {e}")
            raise
            
        return client
    
    def read_single_json(self, object_name: str) -> Optional[Dict]:
        """
        Lê um único arquivo JSON do MinIO.
        
        Args:
            object_name: Nome do objeto no MinIO (ex: "metropoles_com/20240101_120000_123.json")
            
        Returns:
            Dict com dados do JSON ou None se não encontrado
        """
        try:
            logger.info(f"📥 Reading JSON from MinIO: {object_name}")
            
            obj = self.minio_client.get_object(self.bucket_name, object_name)
            json_data = json.load(obj)
            
            logger.debug(f"✅ Successfully read {object_name}")
            return json_data
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.warning(f"📁 File not found: {object_name}")
                return None
            logger.error(f"❌ MinIO error reading {object_name}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in {object_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error reading {object_name}: {e}")
            raise


def read_json_file(object_name: str) -> Optional[Dict]:
    """Função de conveniência para ler um único arquivo JSON."""
    reader = DataReader()
    return reader.read_single_json(object_name)


if __name__ == "__main__":
    # Exemplo de uso simples
    data = read_json_file("example_file.json")
    if data:
        print(f"📰 Loaded JSON data: {data.get('title', 'No title')}")
    else:
        print("❌ Failed to load JSON data") 