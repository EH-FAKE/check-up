# builder
FROM docker.io/python:3.12.3 AS builder

# Install pipenv
RUN pip install --user pipenv

ENV PIPENV_VENV_IN_PROJECT=1

COPY Pipfile Pipfile.lock /usr/src/
WORKDIR /usr/src

# Install all dependencies (including dev, so playwright is installed)
RUN /root/.local/bin/pipenv sync --dev

# Verify Playwright is available in venv
RUN /usr/src/.venv/bin/python -c "import playwright; print(playwright)"

# runtime
FROM docker.io/python:3.12.3 AS runtime

# Copy the virtualenv from builder
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

# Ensure the venv's bin directory is on PATH
ENV PATH=/usr/src/.venv/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /project
COPY . /project

# Install minio package
RUN pip install minio==7.2.15

# Download Playwright browser binaries (Firefox only) along with necessary deps
RUN playwright install --with-deps firefox

CMD ["ipython"]
