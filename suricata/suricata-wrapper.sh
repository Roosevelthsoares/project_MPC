#!/bin/sh
while true; do
  for f in /shared/suri/*.pcap; do
    [ -f "$f" ] || continue
    echo "[suricata] processing $f"
    suricata -c /etc/suricata/suricata.yaml -r "$f"
    rm -f "$f"
  done
  sleep 5
done