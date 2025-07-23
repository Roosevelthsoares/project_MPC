FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instalar dependências do sistema de forma otimizada
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Usar `--no-cache-dir` para evitar que o pip deixe arquivos temporários ocupando espaço
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./app /app

EXPOSE 8000

ENV CLIENT_ID=your_client_id
ENV TOKEN_ID=your_token_id
ENV URL_FIREWALL=http://firewall.url

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

CMD ["python", "main.py"]


# # Use an official Python runtime as a parent image
# FROM python:3.12.3-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set the working directory inside the container
# WORKDIR /app

# # ASFORA ALTERAR
# #ENV PYTHONPATH=/app/moe/src

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     gcc \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# COPY requirements.txt ./requirements.txt
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Copy project files into the container
# COPY app /app


# # Expose the port Flask is expected to run on
# EXPOSE 8000

# # Set environment variables required for the config
# # (You can also use a .env file and docker-compose if preferred)
# ENV CLIENT_ID=your_client_id
# ENV TOKEN_ID=your_token_id
# ENV URL_FIREWALL=http://firewall.url

# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_RUN_PORT=8000

# # Command to run the application
# CMD ["python", "main.py"]
