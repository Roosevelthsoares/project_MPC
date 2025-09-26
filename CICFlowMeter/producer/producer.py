import csv
import json
from datetime import datetime, timezone
import os
from producer.message_broker import MessageBroker

def process_csv_file(filepath, broker):
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        
        # Índices dinâmicos
        IDX_FLOW_ID   = header.index("Flow ID")
        IDX_IP_SRC    = header.index("Src IP")
        IDX_PORT_SRC  = header.index("Src Port")
        IDX_IP_DST    = header.index("Dst IP")
        # IDX_PORT_DST  = header.index("Dst Port")
        IDX_TIMESTAMP = header.index("Timestamp")
        # IDX_PROTOCOL  = header.index("Protocol")
        IDX_LABEL     = header.index("Label")

        # Colunas que não entram no vetor de features
        excluded_indices = {
            IDX_FLOW_ID,
            IDX_IP_SRC,
            IDX_PORT_SRC,
            IDX_IP_DST,
            # IDX_PORT_DST,
            IDX_TIMESTAMP,
            # IDX_PROTOCOL,
            IDX_LABEL
        }
        
        for row in reader:
            try:
                ip_src   = row[IDX_IP_SRC]
                port_src = int(row[IDX_PORT_SRC]) if row[IDX_PORT_SRC] else 0
                ip_dst   = row[IDX_IP_DST]

                features = []
                for idx, val in enumerate(row):
                    if idx in excluded_indices:
                        continue
                    col_name = header[idx]
                    try:
                        f = float(val) if val else 0.0
                    except ValueError:
                        print(f"[ERROR] coluna '{col_name}' idx {idx} → '{val}' não é float")
                        raise
                    features.append(f)

                # Cria mensagem JSON
                message = {
                    "IP Src":   ip_src,
                    "Port Src": port_src,
                    "IP Dst":   ip_dst,
                    "id":       str(os.path.basename(filepath)).split('.')[0],
                    "features": features
                }

                print(json.dumps(message))
                broker.publish_message(message)

            except Exception as e:
                print(f"[ERROR] Linha ignorada por erro: {e}")        

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print(f"Uso: python3 {sys.argv[0]} <arquivo_csv>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    broker = MessageBroker()
    print("[DEBUG] Iniciando process_csv_file com arquivo:", csv_file_path)
    process_csv_file(csv_file_path, broker)
    broker.close()
