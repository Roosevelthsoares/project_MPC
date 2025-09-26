import json
import os
import csv
from collections import defaultdict
from pathlib import Path

# Caminhos
# EVE_FILE = Path("/suricata/logs/eve.json")
# CSV_FILE = Path("/suricata/logs/flows.csv")
# JSON_FILE = Path("/suricata/logs/flows.json")

EVE_FILE = Path(os.getenv("EVE_FILE", "/var/log/suricata/eve.json"))
CSV_FILE = Path(os.getenv("CSV_FILE", "/var/log/suricata/flows.csv"))
JSON_FILE = Path(os.getenv("JSON_FILE", "/var/log/suricata/flows.json"))

def main():
    # Flow agregado por flow_id
    flows = defaultdict(lambda: {
        "src_ip": None,
        "src_port": None,
        "dst_ip": None,
        "dst_port": None,
        "proto": None,
        "labels": set(),       # pode ter mais de um alerta
        "severities": set()    # idem
    })

    with EVE_FILE.open() as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if "flow_id" not in event:
                continue

            fid = event["flow_id"]
            flow = flows[fid]

            # Preenche metadados
            flow["src_ip"] = event.get("src_ip", flow["src_ip"])
            flow["src_port"] = event.get("src_port", flow["src_port"])
            flow["dst_ip"] = event.get("dest_ip", flow["dst_ip"])
            flow["dst_port"] = event.get("dest_port", flow["dst_port"])
            flow["proto"] = event.get("proto", flow["proto"])

            # Captura alertas
            if "alert" in event:
                sig = event["alert"].get("signature", "Unknown Alert")
                sev = event["alert"].get("severity", "NA")
                flow["labels"].add(sig)
                flow["severities"].add(str(sev))

    # Escreve CSV
    with CSV_FILE.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "flow_id", "src_ip", "src_port", "dst_ip", "dst_port", "proto", "labels", "severities"
        ])
        for fid, data in flows.items():
            labels = ";".join(sorted(data["labels"])) if data["labels"] else "Normal"
            severities = ";".join(sorted(data["severities"])) if data["severities"] else "0"
            writer.writerow([
                fid,
                data["src_ip"],
                data["src_port"],
                data["dst_ip"],
                data["dst_port"],
                data["proto"],
                labels,
                severities
            ])

    # Escreve JSON (para RabbitMQ / Oráculo)
    with JSON_FILE.open("w") as jf:
        for fid, data in flows.items():
            labels = list(data["labels"]) if data["labels"] else ["Normal"]
            severities = list(data["severities"]) if data["severities"] else ["0"]

            msg = {
                "flow_id": fid,
                "IP Src": data["src_ip"],
                "Port Src": data["src_port"],
                "IP Dst": data["dst_ip"],
                "Port Dst": data["dst_port"],
                "proto": data["proto"],
                "labels": labels,
                "severities": severities
            }
            jf.write(json.dumps(msg) + "\n")

    print(f"[✓] Arquivo CSV salvo em {CSV_FILE}")
    print(f"[✓] Arquivo JSON salvo em {JSON_FILE}")

if __name__ == "__main__":
    main()
