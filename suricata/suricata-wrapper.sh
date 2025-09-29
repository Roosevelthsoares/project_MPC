#!/bin/bash
set -e

echo "[suricata] preparando ambiente"
mkdir -p /shared/suri /etc/suricata/rules

: > /var/log/suricata/eve.json

echo "[suricata] instalando curl..."
apt-get update && apt-get install -y curl > /dev/null 2>&1

echo "[suricata] atualizando regras públicas (ET Open)..."
suricata-update -v || echo "[suricata] WARNING: falha ao atualizar regras, usando cache existente"

echo "[suricata] verificando configuração..."
suricata -c /etc/suricata/suricata.yaml -T

echo "[suricata] iniciando suricata"

while true; do
  # Se Suricata suporta --pcap-dir (>= 6.0)
  if suricata --help 2>&1 | grep -q -- "--pcap-dir"; then
    exec suricata \
      -c /etc/suricata/suricata.yaml \
      --pidfile /var/run/suricata.pid \
      --runmode=autofp \
      --pcap-file-continuous \
      --pcap-dir /shared/suri \
      -v \
      --pcap-remove   # <- remove o .pcap após processar (flag nativa)
  else
    # Fallback: processa todos PCAPs da pasta em loop e deleta depois
    for f in /shared/suri/*.pcap; do
      [ -e "$f" ] || continue
      echo "[suricata] processando $f"
      suricata \
        -c /etc/suricata/suricata.yaml \
        --runmode=autofp \
        -r "$f" -v
      echo "[suricata] removendo $f"
      rm -f "$f"
    done
    sleep 2
  fi
done
