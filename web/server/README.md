# Como rodar o projeto localmente

## Pré-requisitos
- **Python.js** (v3.10+).

## 2. Rodando o Backend (FastAPI)

### Rodando localmente
```sh
cd web/server
pip install -r requirements.txt
uvicorn main:app --reload
```

O backend estará disponível em http://localhost:8000