#!/usr/bin/env python3
import pandas as pd
import csv
from collections import OrderedDict

# --- 1) Ajuste aqui para os caminhos dos seus arquivos ---
csv_path = "/home/roosevelth/project/CICFlowMeter/flows/teste_ether.pcap_Flow.csv"
parquet_path = "/home/roosevelth/project/Oraculo/app/data/models/calibrate/CICIDS2018_preprocessed_test.parquet"
out_map_path = "csv_vs_parquet_map.csv"
# ---------------------------------------------------------

# 2) Carrega automaticamente os nomes de colunas
csv_cols = pd.read_csv(csv_path, nrows=0).columns.tolist()
parquet_cols = pd.read_parquet(parquet_path, engine="pyarrow").columns.tolist()

base_mapping = {
    # colunas sem equivalentes no Parquet
    "Flow ID": None,
    "Src IP": None,
    "Src Port": None,
    "Dst IP": None,

    # colunas que mudaram de nome
    "Dst Port":           "Dst Port",
    "Protocol":           "Protocol",
    "Timestamp":          "Timestamp",
    "Flow Duration":      "Flow Duration",
    "Total Fwd Packet":   "Tot Fwd Pkts",
    "Total Bwd packets":  "Tot Bwd Pkts",
    "Total Length of Fwd Packet": "TotLen Fwd Pkts",
    "Total Length of Bwd Packet": "TotLen Bwd Pkts",
    "Fwd Packet Length Max":  "Fwd Pkt Len Max",
    "Fwd Packet Length Min":  "Fwd Pkt Len Min",
    "Fwd Packet Length Mean": "Fwd Pkt Len Mean",
    "Fwd Packet Length Std":  "Fwd Pkt Len Std",
    "Bwd Packet Length Max":  "Bwd Pkt Len Max",
    "Bwd Packet Length Min":  "Bwd Pkt Len Min",
    "Bwd Packet Length Mean": "Bwd Pkt Len Mean",
    "Bwd Packet Length Std":  "Bwd Pkt Len Std",
    "Flow Bytes/s":       "Flow Byts/s",
    "Flow Packets/s":     "Flow Pkts/s",
    "Flow IAT Mean":      "Flow IAT Mean",
    "Flow IAT Std":       "Flow IAT Std",
    "Flow IAT Max":       "Flow IAT Max",
    "Flow IAT Min":       "Flow IAT Min",
    "Fwd IAT Total":      "Fwd IAT Tot",
    "Fwd IAT Mean":       "Fwd IAT Mean",
    "Fwd IAT Std":        "Fwd IAT Std",
    "Fwd IAT Max":        "Fwd IAT Max",
    "Fwd IAT Min":        "Fwd IAT Min",
    "Bwd IAT Total":      "Bwd IAT Tot",
    "Bwd IAT Mean":       "Bwd IAT Mean",
    "Bwd IAT Std":        "Bwd IAT Std",
    "Bwd IAT Max":        "Bwd IAT Max",
    "Bwd IAT Min":        "Bwd IAT Min",
    "Fwd PSH Flags":      "Fwd PSH Flags",
    "Bwd PSH Flags":      "Bwd PSH Flags",
    "Fwd URG Flags":      "Fwd URG Flags",
    "Bwd URG Flags":      "Bwd URG Flags",
    "Fwd Header Length":  "Fwd Header Len",
    "Bwd Header Length":  "Bwd Header Len",
    "Fwd Packets/s":      "Fwd Pkts/s",
    "Bwd Packets/s":      "Bwd Pkts/s",
    "Packet Length Min":  "Pkt Len Min",
    "Packet Length Max":  "Pkt Len Max",
    "Packet Length Mean": "Pkt Len Mean",
    "Packet Length Std":  "Pkt Len Std",
    "Packet Length Variance": "Pkt Len Var",
    "FIN Flag Count":     "FIN Flag Cnt",
    "SYN Flag Count":     "SYN Flag Cnt",
    "RST Flag Count":     "RST Flag Cnt",
    "PSH Flag Count":     "PSH Flag Cnt",
    "ACK Flag Count":     "ACK Flag Cnt",
    "URG Flag Count":     "URG Flag Cnt",
    "CWR Flag Count":     "CWE Flag Count",
    "ECE Flag Count":     "ECE Flag Cnt",
    "Down/Up Ratio":      "Down/Up Ratio",
    "Average Packet Size":"Pkt Size Avg",
    "Fwd Segment Size Avg":"Fwd Seg Size Avg",
    "Bwd Segment Size Avg":"Bwd Seg Size Avg",
    "Fwd Bytes/Bulk Avg": "Fwd Byts/b Avg",
    "Fwd Packet/Bulk Avg":"Fwd Pkts/b Avg",
    "Fwd Bulk Rate Avg":  "Fwd Blk Rate Avg",
    "Bwd Bytes/Bulk Avg": "Bwd Byts/b Avg",
    "Bwd Packet/Bulk Avg":"Bwd Pkts/b Avg",
    "Bwd Bulk Rate Avg":  "Bwd Blk Rate Avg",
    "Subflow Fwd Packets":"Subflow Fwd Pkts",
    "Subflow Fwd Bytes":  "Subflow Fwd Byts",
    "Subflow Bwd Packets":"Subflow Bwd Pkts",
    "Subflow Bwd Bytes":  "Subflow Bwd Byts",
    "FWD Init Win Bytes": "Init Fwd Win Byts",
    "Bwd Init Win Bytes": "Init Bwd Win Byts",
    "Fwd Act Data Pkts":  "Fwd Act Data Pkts",
    "Fwd Seg Size Min":   "Fwd Seg Size Min",
    "Active Mean":        "Active Mean",
    "Active Std":         "Active Std",
    "Active Max":         "Active Max",
    "Active Min":         "Active Min",
    "Idle Mean":          "Idle Mean",
    "Idle Std":           "Idle Std",
    "Idle Max":           "Idle Max",
    "Idle Min":           "Idle Min",
    "Label":              "Label",
}



# 4) Monta OrderedDict respeitando a ordem do CSV
mapping = OrderedDict()
for col in csv_cols:
    if col in parquet_cols:
        mapping[col] = col
    else:
        mapping[col] = base_mapping.get(col)

# 5) Escreve o CSV de comparação vertical
with open(out_map_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["csv_column", "parquet_column"])
    for csv_col, pq_col in mapping.items():
        writer.writerow([csv_col, pq_col or ""])  # se for None, grava vazio

print(f"Mapeamento gerado em   → {out_map_path}")
