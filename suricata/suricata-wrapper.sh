#!/bin/bash
set -e

echo "[suricata] preparando ambiente"
mkdir -p /shared/suri /etc/suricata/rules

: > /var/log/suricata/eve.json

echo "[suricata] instalando curl e suricata-update..."
apt-get update && apt-get install -y curl suricata-update > /dev/null 2>&1

echo "[suricata] configurando fontes de regras gratuitas..."

suricata-update enable-source et/open                 
suricata-update add-source snort-community \
  https://www.snort.org/downloads/community/community-rules.tar.gz

suricata-update update-sources


echo "[suricata] atualizando regras..."
suricata-update -v || echo "[suricata] WARNING: falha ao atualizar regras, usando cache existente"

echo "[suricata] verificando configuração..."
suricata -c /etc/suricata/suricata.yaml -T

echo "[suricata] iniciando suricata"

while true; do
  if suricata --help 2>&1 | grep -q -- "--pcap-dir"; then
    exec suricata \
      -c /etc/suricata/suricata.yaml \
      --pidfile /var/run/suricata.pid \
      --runmode=autofp \
      --pcap-file-continuous \
      --pcap-dir /shared/suri \
      -v \
      --pcap-remove
  else
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
