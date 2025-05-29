FROM python:3.12.3 AS dependencies

LABEL maintainer="Check-up Project"
LABEL description="Health advertisement analysis scraper"
LABEL version="1.0"

# Configurações de build para otimização
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Variáveis de ambiente para otimização de build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIPENV_VENV_IN_PROJECT=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar pipenv com versão estável
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user pipenv

# Criar diretório de trabalho
WORKDIR /build

# Copiar apenas arquivos de dependência para melhor cache
COPY Pipfile Pipfile.lock ./

# Instalar dependências Python com cache
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pipenv \
    /root/.local/bin/pipenv sync --dev

# Verificar instalações críticas
RUN /build/.venv/bin/python -c "import playwright, sqlalchemy, scrapy; print('✅ Core dependencies installed')"

# =====================================
# System dependencies stage
# =====================================
FROM python:3.12.3-slim AS system-deps

# Instalar dependências do sistema com cache apt
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        # Essenciais para Playwright
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
        # Utilitários
        wget \
        xdg-utils \
        curl \
        # PostgreSQL client
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# =====================================
# Playwright browsers stage
# =====================================
FROM system-deps AS playwright-setup

# Copiar ambiente virtual da etapa de dependências
COPY --from=dependencies /build/.venv /app/.venv

# Configurar PATH para usar o venv ANTES de qualquer comando
ENV PATH="/app/.venv/bin:$PATH"

# Instalar MinIO client usando o venv correto
RUN --mount=type=cache,target=/root/.cache/pip \
    /app/.venv/bin/pip install minio==7.2.15

# Instalar browsers do Playwright com cache usando o caminho correto
RUN --mount=type=cache,target=/ms-playwright \
    /app/.venv/bin/playwright install --with-deps firefox && \
    /app/.venv/bin/playwright install-deps

# Verificar instalação do Playwright usando PATH configurado
RUN /app/.venv/bin/python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('✅ Playwright ready'); p.stop()"

# =====================================
# Final runtime stage
# =====================================
FROM system-deps AS runtime

# Copiar ambiente virtual completo
COPY --from=playwright-setup /app/.venv /app/.venv

# Copiar browsers do Playwright
COPY --from=playwright-setup /ms-playwright /ms-playwright

# Configurar variáveis de ambiente
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Configurar diretório de trabalho
WORKDIR /project

# Criar usuário não-root com UID/GID específicos
RUN groupadd -g 1001 scraper && \
    useradd --no-log-init -r -u 1001 -g scraper -d /project scraper && \
    chown -R scraper:scraper /project /app/.venv /ms-playwright && \
    chmod -R 775 /ms-playwright

# Copiar código-fonte para o diretório de trabalho
COPY --chown=scraper:scraper . /project

# Mudar para usuário não-root
USER scraper

# Criar diretórios necessários
RUN mkdir -p /project/{screenshots,sessions,logs} && \
    chmod 755 /project/{screenshots,sessions,logs}

# Health check otimizado
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; import playwright; sys.exit(0)" || exit 1

# Adicionar metadata de runtime
LABEL org.opencontainers.image.source="https://github.com/EH-FAKE/check-up" \
      org.opencontainers.image.documentation="https://github.com/EH-FAKE/docs/blob/main/README.md"

# Comando padrão otimizado
CMD ["ipython", "--no-banner"]
