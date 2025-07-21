import csv
import json
from datetime import datetime, timezone
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
        # (se quiser usar Porta Dst, Timestamp, Protocol, Label, basta descomentar:)
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
                # Campos obrigatórios
                ip_src   = row[IDX_IP_SRC]
                port_src = int(row[IDX_PORT_SRC]) if row[IDX_PORT_SRC] else 0
                ip_dst   = row[IDX_IP_DST]

                # Monta vetor de features, convertendo para float e marcando 0.0 se vazio
                features = []
                for idx, val in enumerate(row):
                    if idx in excluded_indices:
                        continue
                    col_name = header[idx]
                    try:
                        f = float(val) if val else 0.0
                    except ValueError:
                        # debug em caso de valores não numéricos inesperados
                        print(f"[ERROR] coluna '{col_name}' idx {idx} → '{val}' não é float")
                        raise
                    features.append(f)

                # Cria mensagem JSON
                message = {
                    "IP Src":   ip_src,
                    "Port Src": port_src,
                    "IP Dst":   ip_dst,
                    "features": features
                }

                print(json.dumps(message))  # log para debug
                broker.publish_message(message)

            except Exception as e:
                print(f"[ERROR] Linha ignorada por erro: {e}")        
        
        # for row in reader:
        #     try:
        #         # Campos obrigatórios
        #         ip_src = row[IDX_IP_SRC]
        #         port_src = int(row[IDX_PORT_SRC]) if row[IDX_PORT_SRC] else 0
        #         ip_dst = row[IDX_IP_DST]

        #         excluded_indices = {IDX_FLOW_ID, IDX_IP_SRC, IDX_PORT_SRC, IDX_IP_DST,
        #                             # IDX_PORT_DST,IDX_TIMESTAMP, IDX_PROTOCOL, IDX_LABEL, IDX_TOTAL_LEN_BWD
        #                             }

        #         # features = [
        #         #     float(val) if val else 0.0
        #         #     for idx, val in enumerate(row)
        #         #     if idx not in excluded_indices
        #         # ]
                
                
                
                
                
                
        #         # Construção do JSON
        #         message = {
        #             "IP Src": ip_src,
        #             "Port Src": port_src,
        #             "IP Dst": ip_dst,
        #             # "Port Dst": port_dst,
        #             # "Timestamp": timestamp,
        #             # "Protocol": protocol,
        #             "features": features
        #         }

        #         print(json.dumps(message))  # log para debug
        #         broker.publish_message(message)

            # except Exception as e:
            #     print(f"[ERROR] Linha ignorada por erro: {e}")

#  Adicionado para permitir execução direta

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




# import csv
# import json
# # from datetime import datetime, UTC
# from datetime import datetime, timezone


# # Índices das colunas no CSV (ajustar se necessário)
# IDX_FLOW_ID = 0
# IDX_IP_SRC = 1
# IDX_PORT_SRC = 2
# IDX_IP_DST = 3
# IDX_PORT_DST = 4
# IDX_PROTOCOL = 5
# IDX_TIMESTAMP = 6
# IDX_LABEL = -1  # última coluna
# IDX_TOTAL_LEN_BWD = 10  # exemplo, ajuste conforme layout do CSV

# def process_csv_file(filepath, broker):
#     with open(filepath, 'r') as file:
#         reader = csv.reader(file)
#         header = next(reader)  # pula cabeçalho
#         for row in reader:
#             try:
#                 # Campos obrigatórios
#                 ip_src = row[IDX_IP_SRC]
#                 port_src = int(row[IDX_PORT_SRC])
#                 ip_dst = row[IDX_IP_DST]
#                 port_dst = int(row[IDX_PORT_DST])
#                 timestamp_str = row[IDX_TIMESTAMP]
#                 protocol = int(row[IDX_PROTOCOL])

#                 # Converter timestamp para ISO format
#                 try:
#                     timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %I:%M:%S %p").isoformat()
#                 except ValueError:
#                     timestamp = datetime.now(timezone.utc).isoformat()


#                 # Construção da lista de features (remove campos desnecessários)
#                 excluded_indices = {IDX_FLOW_ID, IDX_IP_SRC, IDX_PORT_SRC, IDX_IP_DST, IDX_PORT_DST,
#                                     IDX_TIMESTAMP, IDX_PROTOCOL, IDX_LABEL, IDX_TOTAL_LEN_BWD}

#                 features = [
#                     float(val) if val else 0.0
#                     for idx, val in enumerate(row)
#                     if idx not in excluded_indices
#                 ]

#                 # Construção do JSON
#                 message = {
#                     "IP Src": ip_src,
#                     "Port Src": port_src,
#                     "IP Dst": ip_dst,
#                     "Port Dst": port_dst,
#                     "Timestamp": timestamp,
#                     "Protocol": protocol,
#                     "features": features
#                 }

#                 print(json.dumps(message))  # log para debug
#                 broker.publish_message(message)

#             except Exception as e:
#                 print(f"[ERROR] Linha ignorada por erro: {e}")
