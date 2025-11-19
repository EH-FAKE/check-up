import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from minio import Minio
from dotenv import load_dotenv
from datetime import datetime

app = FastAPI()

# Permitir CORS para facilitar o desenvolvimento local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
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
load_dotenv(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../../.env')))


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/portais", response_model=List[str])
def listar_portais():
    portais = set()
    try:
        objetos = minio_client.list_objects(MINIO_BUCKET, recursive=False)
        for obj in objetos:
            if obj.is_dir:
                nome_portal = obj.object_name.rstrip('/')
                portais.add(nome_portal)
            else:
                partes = obj.object_name.split('/')
                if len(partes) > 1:
                    portais.add(partes[0])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o MinIO: {str(e)}")
    return sorted(list(portais))

# --- FUNÇÃO AUXILIAR PARA TRATAR DATA ---
def processar_data_noticia(noticia):
    data_str = (
        noticia.get('date') or 
        noticia.get('publishedAt') or 
        noticia.get('createdAt') or 
        noticia.get('scraped_at') 
    )
    if data_str:
        noticia['date'] = data_str 
        try:
            data_limpa = data_str[:19] 
            return datetime.fromisoformat(data_limpa)
        except Exception:
            pass
    
    return datetime.min

@app.get("/noticias/{portal}")
def listar_noticias(
    portal: str,
    order: str = Query("desc", regex="^(asc|desc)$")
):
    prefix = f"{portal}/"
    noticias = []
    try:
        objetos = minio_client.list_objects(
            MINIO_BUCKET, prefix=prefix, recursive=True)
        for obj in objetos:
            if obj.object_name.endswith('.json'):
                try:
                    response = minio_client.get_object(
                        MINIO_BUCKET, obj.object_name)
                    conteudo = response.read()
                    noticia = json.loads(conteudo.decode('utf-8'))
                    noticia['_data_ordenacao'] = processar_data_noticia(noticia)
                    
                    noticias.append(noticia)
                except Exception:
                    continue
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o MinIO: {str(e)}")

    # Ordenação
    reverse = order == 'desc'
    noticias.sort(key=lambda n: n['_data_ordenacao'], reverse=reverse)
    for n in noticias:
        n.pop('_data_ordenacao', None)

    return noticias


@app.get("/noticias/{portal}/search")
def buscar_noticias(
    portal: str,
    q: str = Query(..., description="Termo de busca"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    termo = q.strip().lower()
    prefix = f"{portal}/"
    resultados = []
    try:
        objetos = minio_client.list_objects(
            MINIO_BUCKET, prefix=prefix, recursive=True)
        for obj in objetos:
            if obj.object_name.endswith('.json'):
                try:
                    response = minio_client.get_object(
                        MINIO_BUCKET, obj.object_name)
                    conteudo = response.read()
                    noticia = json.loads(conteudo.decode('utf-8'))
                    
                    campos = [
                        str(noticia.get('title', '')),
                        str(noticia.get('description', '')),
                        str(noticia.get('body', '')),
                        ' '.join(noticia.get('tags', []) or [])
                    ]
                    
                    if any(termo in campo.lower() for campo in campos):
                        # Usa a mesma função auxiliar
                        noticia['_data_ordenacao'] = processar_data_noticia(noticia)
                        resultados.append(noticia)
                        
                except Exception:
                    continue
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o MinIO: {str(e)}")

    # Ordenação
    reverse = order == 'desc'
    resultados.sort(key=lambda n: n['_data_ordenacao'], reverse=reverse)

    # Remover campo auxiliar
    for n in resultados:
        n.pop('_data_ordenacao', None)

    return resultados