# Ambiente congelado de la prueba: Python, dependencias, Chrome y chromedriver en versiones exactas.
# Se publica en GitHub Packages (ghcr.io) con cada release; permite ejecutar la suite igual que en la entrega.
#
#   docker run --rm ghcr.io/yoelalmiron1997/farmatodo-qa-test-engineering:1.0.0                # E2E + reporte
#   docker run --rm ghcr.io/yoelalmiron1997/farmatodo-qa-test-engineering:1.0.0 pytest       # unit + integración
#   docker run --rm -v "$PWD/reports:/app/reports" ghcr.io/...:1.0.0                         # reportes en el host
FROM python:3.12.3-slim-bookworm

ARG CHROME_VERSION=155.0.8059.39
ARG UV_VERSION=0.11.32
ARG VERSION=dev

LABEL org.opencontainers.image.title="farmatodo-qa-test-engineering" \
      org.opencontainers.image.description="Prueba técnica QA Farmatodo — ambiente congelado (Python, dependencias, Chrome y driver)" \
      org.opencontainers.image.source="https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering" \
      org.opencontainers.image.authors="Ing. Yoel Maximiliano Almirón" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}"

# Librerías del sistema que necesita Chrome for Testing en Debian bookworm.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 \
      libcups2 libdbus-1-3 libdrm2 libexpat1 libgbm1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 \
      libvulkan1 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 \
      libxshmfence1 xdg-utils zip \
 && rm -rf /var/lib/apt/lists/*

ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    SE_CACHE_PATH=/opt/selenium \
    QA_HEADLESS=true \
    QA_BROWSER_VERSION=${CHROME_VERSION}

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

WORKDIR /app

# Dependencias primero (capa reutilizable), después el proyecto.
COPY pyproject.toml uv.lock .python-version README.md ./
RUN uv sync --frozen --group dev --no-install-project
COPY . .
RUN uv sync --frozen --group dev

# Chrome y chromedriver exactos, descargados al construir: la imagen no depende de la versión del host.
RUN python -c "from selenium.webdriver.common.selenium_manager import SeleniumManager as M; \
print(M().binary_paths(['--browser', 'chrome', '--browser-version', '${CHROME_VERSION}']))"

CMD ["sh", "-c", "pytest tests/e2e --reruns 2 --qa-results-dir reports; qa results build --results-dir reports --out reports/run-result.json && qa report summary --run reports/run-result.json --out-dir reports && qa gate --run reports/run-result.json"]
