#!/bin/bash

echo "[suricata] preparando ambiente"
mkdir -p /shared/suri /etc/suricata/rules

echo "[suricata] instalando curl..."
apt-get update && apt-get install -y curl > /dev/null 2>&1

echo "[suricata] atualizando regras públicas (ET Open)..."
suricata-update -v || echo "[suricata] WARNING: falha ao atualizar regras, usando cache existente"

echo "[suricata] verificando configuração..."
suricata -c /etc/suricata/suricata.yaml -T

echo "[suricata] iniciando suricata"
exec suricata \
  -c /etc/suricata/suricata.yaml \
  --pidfile /var/run/suricata.pid \
  --runmode=autofp \
  --pcap-file-continuous \
  -v \
  -r /shared/suri