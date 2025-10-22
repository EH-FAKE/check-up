# builder
FROM python:3.12.3 AS builder

RUN pip install --user pipenv==2023.12.1
ENV PIPENV_VENV_IN_PROJECT=1

COPY Pipfile Pipfile.lock /usr/src/
WORKDIR /usr/src

# Instala dependências com pipenv
RUN /root/.local/bin/pipenv sync --dev

# Instala minio e browsers no venv
RUN /root/.local/bin/pipenv install minio==7.2.15
RUN /root/.local/bin/pipenv install scrapy-playwright==0.0.43
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/src/.venv/pw-browsers
RUN /root/.local/bin/pipenv run playwright install --with-deps firefox

# Confirma que playwright foi instalado corretamente
RUN /usr/src/.venv/bin/python -c "import playwright; print(playwright)"

# runtime
FROM python:3.12.3-slim AS runtime

COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 \
    libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libstdc++6 libx11-6 \
    libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 \
    libxi6 libxrandr2 libxrender1 libxss1 libxtst6 wget xdg-utils \
    && rm -rf /var/lib/apt/lists/*

ENV PATH=/usr/src/.venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/usr/src/.venv/pw-browsers

WORKDIR /project

RUN groupadd -r scraper && \
    useradd --no-log-init -r -g scraper -d /project scraper && \
    chown -R scraper:scraper /project /usr/src/.venv

COPY --chown=scraper:scraper . /project

USER scraper

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"


CMD ["ipython"]
