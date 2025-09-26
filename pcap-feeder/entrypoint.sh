#!/bin/sh
set -eu

# config
CAP_IF="${CAP_IF:-eth0}"         # capture interface
CAPTURE="${CAPTURE:-1}"          # set to 0 to disable live capture (replay-only mode)

MIRROR_SURICATA="${MIRROR_SURICATA:-false}"
MIRROR_ORACULO="${MIRROR_ORACULO:-true}"
POLL_INTERVAL="${POLL_INTERVAL:-2}"  # seconds between polls

is_true() {
  case "$1" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *)                         return 1 ;;
  esac
}

# shared dirs (single volume so hard-links work)
mkdir -p /shared/incoming
is_true "$MIRROR_SURICATA" && mkdir -p /shared/suri
is_true "$MIRROR_ORACULO"  && mkdir -p /shared/cic

# start flow-aware capture (one pcap per completed flow) into /shared/incoming
if [ "$CAPTURE" = "1" ]; then
  echo "[pcap-feeder] starting netsniff-ng on $CAP_IF (flow-aware rotation)"
  netsniff-ng -i "$CAP_IF" --interval-flows --output=/shared/incoming --silent &
fi

dispatch_file() {
  f="$1"
  base="$(basename "$f")"
  dispatched=0

  if is_true "$MIRROR_SURICATA"; then
    ln "$f" "/shared/suri/$base" 2>/dev/null || {
      cp "$f" "/shared/suri/$base.part" && mv "/shared/suri/$base.part" "/shared/suri/$base"
    }
    dispatched=1
  fi

  if is_true "$MIRROR_ORACULO"; then
    ln "$f" "/shared/cic/$base" 2>/dev/null || {
      cp "$f" "/shared/cic/$base.part" && mv "/shared/cic/$base.part" "/shared/cic/$base"
    }
    dispatched=1
  fi

  if [ "$dispatched" -eq 1 ]; then
    rm -f "$f"
    echo "[pcap-feeder] dispatched $base ->$(is_true "$MIRROR_SURICATA" && printf ' suri')$(is_true "$MIRROR_ORACULO" && printf ' cic')"
  else
    echo "[pcap-feeder] WARNING: no mirror destinations enabled; leaving $base in /shared/incoming"
  fi
}

# poll loop
echo "[pcap-feeder] polling /shared/incoming for new pcaps every $POLL_INTERVAL seconds…"
while true; do
  for f in $(ls -1 /shared/incoming/*.pcap 2>/dev/null | sort); do
    [ -f "$f" ] && dispatch_file "$f"
  done
  sleep "$POLL_INTERVAL"
done
