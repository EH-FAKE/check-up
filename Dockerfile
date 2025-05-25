# builder
FROM python:3.12.3 AS builder

# Instala o pipenv
RUN pip install --user pipenv

# Cria o venv dentro do projeto
ENV PIPENV_VENV_IN_PROJECT=1

# Copia arquivos de dependência
COPY Pipfile Pipfile.lock /usr/src/
WORKDIR /usr/src

# Instala dependências com pipenv
RUN /root/.local/bin/pipenv sync --dev

# Verifica se playwright foi instalado
RUN /usr/src/.venv/bin/python -c "import playwright; print(playwright)"

# runtime
FROM python:3.12.3 AS runtime

# Copia o ambiente virtual
COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

# Instala dependências do sistema para o Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 \
    libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 \
    libnss3 libpango-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 wget xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Define variáveis de ambiente
ENV PATH=/usr/src/.venv/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /project
COPY . /project

# Instala pacote do minio
RUN pip install minio==7.2.15

# Instala navegador do playwright
RUN playwright install --with-deps firefox

CMD ["ipython"]
