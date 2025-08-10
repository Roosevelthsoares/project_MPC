# ./pcap-feeder/entrypoint.sh
#!/bin/sh
set -eu

# config
CAP_IF="${CAP_IF:-eth0}"         # capture interface
CAPTURE="${CAPTURE:-1}"          # set to 0 to disable live capture (replay-only mode)

# shared dirs (single volume so hard-links work)
mkdir -p /shared/incoming /shared/suri /shared/cic

# start flow-aware capture (one pcap per completed flow) into /shared/incoming
if [ "$CAPTURE" = "1" ]; then
  echo "[pcap-feeder] starting netsniff-ng on $CAP_IF (flow-aware rotation)"
  netsniff-ng -i "$CAP_IF" --interval-flows --output=/shared/incoming --silent &
fi

# watch for fully-written files, then hard-link to both destinations atomically
echo "[pcap-feeder] watching /shared/incoming for new pcaps…"
inotifywait -m -e close_write --format '%w%f' /shared/incoming | while read -r f; do
  base="$(basename "$f")"
  # create hard links so there’s only one physical copy on disk
  ln "$f" "/shared/suri/$base" 2>/dev/null || { cp "$f" "/shared/suri/$base.part" && mv "/shared/suri/$base.part" "/shared/suri/$base"; }
  ln "$f" "/shared/cic/$base"  2>/dev/null || { cp "$f" "/shared/cic/$base.part"  && mv "/shared/cic/$base.part"  "/shared/cic/$base"; }
  # drop the original name; two links remain (CIC may delete its link later without hurting Suricata’s)
  rm -f "$f"
  echo "[pcap-feeder] dispatched $base -> suri + cic"
done
