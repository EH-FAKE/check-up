# builder
FROM python:3.12.3 AS builder

# Instala o pipenv com versão fixa
RUN pip install --user pipenv==2023.12.1

# Cria o venv dentro do projeto
ENV PIPENV_VENV_IN_PROJECT=1

# Copia apenas os arquivos de dependência primeiro para melhor utilização de cache
COPY Pipfile Pipfile.lock /usr/src/
WORKDIR /usr/src

# Instala dependências com pipenv
RUN /root/.local/bin/pipenv sync --dev

# Verifica se playwright foi instalado
RUN /usr/src/.venv/bin/python -c "import playwright; print(playwright)"

# runtime
FROM python:3.12.3-slim AS runtime

# Copia o ambiente virtual
COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

# Install OS-level dependencies required by Playwright browsers
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    wget \
    xdg-utils \

    && rm -rf /var/lib/apt/lists/*


# Define variáveis de ambiente
ENV PATH=/usr/src/.venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala pacote do minio e playwright antes de copiar o código-fonte
# para aproveitar melhor o cache de camadas
RUN pip install minio==7.2.15 && \
    playwright install --with-deps firefox

# Configuração do diretório de trabalho
WORKDIR /project

# Cria usuário não-root
RUN groupadd -r scraper && \
    useradd --no-log-init -r -g scraper -d /project scraper && \
    chown -R scraper:scraper /project /usr/src/.venv

# Copia o código-fonte para o diretório de trabalho
COPY --chown=scraper:scraper . /project

# Muda para o usuário não-root
USER scraper

# Health check para verificar se o container está saudável
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Install scrapy-playwright extension
RUN pip install scrapy-playwright==0.0.43

# Comando padrão ao iniciar o container
CMD ["ipython"]
