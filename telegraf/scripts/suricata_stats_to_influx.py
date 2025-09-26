#!/usr/bin/env python3
"""
Read the last 'stats' event from a Suricata eve.json file and print a single InfluxDB line.
Used by Telegraf inputs.exec to emit suricata_* metrics.

Usage: suricata_stats_to_influx.py [path_to_eve.json]
"""
import sys
import json
import time
import socket
from pathlib import Path


def find_last_stats(path: Path, max_bytes=131072):
    try:
        with path.open('rb') as f:
            f.seek(0, 2)
            filesize = f.tell()
            read_from = max(0, filesize - max_bytes)
            f.seek(read_from)
            data = f.read()
    except Exception:
        return None

    try:
        lines = data.splitlines()
    except Exception:
        return None

    for raw in reversed(lines):
        try:
            obj = json.loads(raw.decode('utf-8', errors='ignore'))
        except Exception:
            continue
        if obj.get('event_type') == 'stats':
            return obj
    return None


def to_int(v):
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return 0


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/var/log/suricata/eve.json')
    if not path.exists():
        # Nothing to print; telegraf will handle empty result
        return

    stats_event = find_last_stats(path)
    if not stats_event:
        return

    stats = stats_event.get('stats') or {}

    # Try to extract values from nested structure
    flow = stats.get('flow', {}) if isinstance(stats, dict) else {}
    tcp = stats.get('tcp', {}) if isinstance(stats, dict) else {}
    detect = stats.get('detect', {}) if isinstance(stats, dict) else {}

    # Fallback to flattened keys (some Telegraf JSON parsing produces these)
    def maybe(name, default=0):
        v = 0
        if isinstance(stats_event.get(name), (int, float)):
            return to_int(stats_event.get(name))
        # try nested
        return default

    host = socket.gethostname().replace(' ', '_')

    flow_total = to_int(flow.get('total', maybe('stats_flow_total', 0)))
    flow_active = to_int(flow.get('active', maybe('stats_flow_active', 0)))
    uptime = to_int(stats.get('uptime', maybe('stats_uptime', 0)))
    alerts = to_int(detect.get('alert', maybe('stats_detect_alert', 0)))

    # Timestamp: use current time in nanoseconds
    ts = time.time_ns()

    # Build Influx line; use integers (trailing i) to be parsed as ints
    fields = []
    fields.append(f"flow_total={flow_total}i")
    fields.append(f"flow_active={flow_active}i")
    fields.append(f"uptime_seconds={uptime}i")
    fields.append(f"alerts_total={alerts}i")

    line = f"suricata,host={host} " + ",".join(fields) + f" {ts}"
    print(line)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Do not raise: inputs.exec expects clean behavior
        pass
