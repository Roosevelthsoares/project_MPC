#!/bin/bash

# Verifica se dois diretórios foram passados
if [ $# -ne 2 ]; then
    echo "Uso: $0 <diretorio_origem> <diretorio_destino>"
    exit 1
fi

SRC="$1"
DST="$2"

# Verifica se origem existe
if [ ! -d "$SRC" ]; then
    echo "Erro: diretório de origem não existe."
    exit 1
fi

# Cria destino se não existir
if [ ! -d "$DST" ]; then
    mkdir -p "$DST"
fi

# Copia arquivos um por um com atraso de 0.01s
for file in "$SRC"/*; do
    if [ -f "$file" ]; then
        cp "$file" "$DST"/
        echo "Enviado: $(basename "$file")"
        sleep 5
    fi
done
