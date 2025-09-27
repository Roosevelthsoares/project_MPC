FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=10
ENV POETRY_HTTP_TIMEOUT=0
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Instalar dependências do sistema de forma otimizada
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

COPY pyproject.toml ./

RUN poetry install --no-ansi --no-interaction --no-root

COPY ./app /app

EXPOSE 8000

ENV FIREWALL_CLIENT_ID=your_FIREWALL_CLIENT_ID
ENV FIREWALL_TOKEN_ID=your_FIREWALL_TOKEN_ID
ENV URL_FIREWALL=http://firewall.url


ENV API_RUN_HOST=0.0.0.0
ENV API_RUN_PORT=8000

CMD ["poetry", "run", "python", "main.py"]