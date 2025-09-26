#!/bin/sh
# Minimal script to extract the last 'stats' event from eve.json and print an InfluxDB line.
# Usage: suricata_stats_to_influx.sh [path_to_eve.json]

EVE=${1:-/var/log/suricata/eve.json}
HOST=$(hostname | tr ' ' '_')

if [ ! -f "$EVE" ]; then
  exit 0
fi

# Read last 100KB of file, then find last line containing event_type=="stats"
LINE=$(tail -c 131072 "$EVE" 2>/dev/null | tac | grep -m1 '"event_type".*"stats"' | head -n1)
if [ -z "$LINE" ]; then
  exit 0
fi

# Use jq to extract nested fields if available
if command -v jq >/dev/null 2>&1; then
  FLOW_TOTAL=$(printf '%s' "$LINE" | jq -r '.stats.flow.total // 0')
  FLOW_ACTIVE=$(printf '%s' "$LINE" | jq -r '.stats.flow.active // 0')
  UPTIME=$(printf '%s' "$LINE" | jq -r '.stats.uptime // 0')
  ALERTS=$(printf '%s' "$LINE" | jq -r '.stats.detect.alert // 0')
else
  # Fallback: try crude extraction using sed (best-effort)
  FLOW_TOTAL=$(printf '%s' "$LINE" | sed -n 's/.*"flow".*"total"[: ]*\([0-9]*\).*/\1/p')
  FLOW_ACTIVE=$(printf '%s' "$LINE" | sed -n 's/.*"flow".*"active"[: ]*\([0-9]*\).*/\1/p')
  UPTIME=$(printf '%s' "$LINE" | sed -n 's/.*"uptime"[: ]*\([0-9]*\).*/\1/p')
  ALERTS=$(printf '%s' "$LINE" | sed -n 's/.*"detect".*"alert"[: ]*\([0-9]*\).*/\1/p')
fi

FLOW_TOTAL=${FLOW_TOTAL:-0}
FLOW_ACTIVE=${FLOW_ACTIVE:-0}
UPTIME=${UPTIME:-0}
ALERTS=${ALERTS:-0}

TS=$(date +%s%N)

printf "suricata,host=%s flow_total=%si,flow_active=%si,uptime_seconds=%si,alerts_total=%si %s\n" "$HOST" "$FLOW_TOTAL" "$FLOW_ACTIVE" "$UPTIME" "$ALERTS" "$TS"
