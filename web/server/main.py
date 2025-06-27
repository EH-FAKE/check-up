import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from minio import Minio
from dotenv import load_dotenv

app = FastAPI()

# Permitir CORS para facilitar o desenvolvimento local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'scraped-articles')

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Carregar variáveis do .env da raiz do projeto
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')))

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/portais", response_model=List[str])
def listar_portais():
    # Lista os prefixos (portais) diretamente do MinIO
    portais = set()
    try:
        objetos = minio_client.list_objects(MINIO_BUCKET, recursive=False)
        for obj in objetos:
            if obj.is_dir:
                nome_portal = obj.object_name.rstrip('/')
                portais.add(nome_portal)
            else:
                # Caso não venha como diretório, extrai o prefixo do nome do objeto
                partes = obj.object_name.split('/')
                if len(partes) > 1:
                    portais.add(partes[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o MinIO: {str(e)}")
    return sorted(list(portais))

@app.get("/noticias/{portal}")
def listar_noticias(portal: str):
    prefix = f"{portal}/"
    noticias = []
    try:
        objetos = minio_client.list_objects(MINIO_BUCKET, prefix=prefix, recursive=True)
        for obj in objetos:
            if obj.object_name.endswith('.json'):
                try:
                    response = minio_client.get_object(MINIO_BUCKET, obj.object_name)
                    conteudo = response.read()
                    noticia = json.loads(conteudo.decode('utf-8'))
                    noticias.append(noticia)
                except Exception:
                    continue  # Ignora arquivos com erro
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o MinIO: {str(e)}")
    return noticias

@app.get("/noticias/{portal}/search")
def buscar_noticias(portal: str, q: str = Query(..., description="Termo de busca")):
    termo = q.strip().lower()
    prefix = f"{portal}/"
    resultados = []
    try:
        objetos = minio_client.list_objects(MINIO_BUCKET, prefix=prefix, recursive=True)
        for obj in objetos:
            if obj.object_name.endswith('.json'):
                try:
                    response = minio_client.get_object(MINIO_BUCKET, obj.object_name)
                    conteudo = response.read()
                    noticia = json.loads(conteudo.decode('utf-8'))
                    # Busca em título, descrição, body e tags
                    campos = [
                        str(noticia.get('title', '')),
                        str(noticia.get('description', '')),
                        str(noticia.get('body', '')),
                        ' '.join(noticia.get('tags', []) or [])
                    ]
                    if any(termo in campo.lower() for campo in campos):
                        resultados.append(noticia)
                except Exception:
                    continue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o MinIO: {str(e)}")
    return resultados 