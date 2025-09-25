#!/bin/sh
set -e

echo "[suricata] preparando ambiente"
mkdir -p /shared/suri
mkdir -p /etc/suricata/rules

echo "[suricata] atualizando regras públicas (ET Open)..."
suricata-update || echo "[suricata] WARNING: falha ao atualizar regras, usando cache existente"

echo "[suricata] iniciando em modo contínuo"
exec suricata \
  -c /etc/suricata/suricata.yaml \
  --pcap-file-continuous \
  -r /shared/suri
