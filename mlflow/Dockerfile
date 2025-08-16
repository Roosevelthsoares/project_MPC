FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install "mlflow[extras]"
WORKDIR /mlflow
EXPOSE 5000
CMD ["bash", "-lc", "mlflow server --help"]